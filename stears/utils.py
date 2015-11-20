from urllib2 import urlopen
from pymongo import MongoClient
from models import ArticleImageModel
from mongoengine.django.auth import User
from django.core.mail import send_mail
from writers.settings import EMAIL_HOST_USER as email_host
from writers.settings import client
from datetime import datetime

import params
import json
import time
import re
import random


def handle_uploaded_file(image):
    with open('media/articleImages/', 'wb+') as destination:
        for chunk in image.chunks():
            destination.write(chunk)


def mongo_calls(collection_name, c=client):
    collection = None
    try:
        if not c:
            c = MongoClient(params.MONGO_URI)
        collection = c[params.db][collection_name]
    except Exception:
        print "URGENT ERROR: DATABASE UNAVAILABLE"
        collection = None
    return collection


def new_column(user, bio, description, title, email, photo, **kwargs):
    dels = []
    for key in kwargs:
        if not kwargs[key]: dels.append(key)

    for key in dels:
        del kwargs[key]

    column_page = dict({
        'writer': user.username,
        'bio': bio,
        'description': description,
        'title': title,
        'column_id': make_id('columns', 'column_id'),
        'email': email,
        'photo': photo,
        'state': 'inactive',
    }, **kwargs)
    return column_page


def make_id(collection_name, id_field):
    collection = mongo_calls(collection_name)
    ids = collection.distinct(id_field)
    new_id = first_missing_number(ids)
    return new_id


def make_new_quote(body, author):
    onsite = mongo_calls('onsite')
    onsite.update({'page': 'home'},
                  {'$set': {'quote': {'body': body, 'author': author}}},
                  False, False)
    # Add to list of quotes!


def make_url(name, True_for_snapshot):

    link = "http://staging.globaltrybe.com/nseij.svc/" + name

    if name is "Company":
        link = link + "?reqobj={'Symbol':'ACCESS'}&sid="

    elif name is "MarketIndex":
        link = link + "?reqobj={'Symbol':'ASI'}&sid="

    else:
        link = link + "?sid="

    link = link + params.sid + "&app=nseiws-"

    if True_for_snapshot:
        return link + "snapshot"

    elif not True_for_snapshot:
        return link + name

    return link


def first_missing_number(taken_numbers):
    if taken_numbers:
        max_id = max(taken_numbers)
    else:
        max_id = 1

    all_numbers = set(range(1, max_id + 2))
    available = all_numbers - set(taken_numbers)
    return min(available)


def make_writer_id(writer):
    users = mongo_calls('user')
    ids = users.distinct('writer_id')
    writer_id = first_missing_number(ids)

    users.update({
        "username": writer
    }, {'$set': {"writer_id": writer_id}
        }, False, False
    )
    return writer_id


def edit_user(username, key, item):
    users = mongo_calls('user')
    users.update({
        "username": username},
        {'$set': {key: item}
         }, False, False
    )
    # print "%s's %s has been changed from %s to
    # %s"%(username,key,current_item,item)


def do_magic_user():
    foo = User()
    foo.first_name = 'stears'
    foo.last_name = 'admin'
    foo.email = 'stears@stears.com'
    foo.username = make_username(foo.first_name, foo.last_name)
    foo.set_password(params.cheeky_password)
    foo.is_superuser = True
    foo.is_staff = True
    foo.save()
    edit_user(foo.username, 'state', 'admin')
    edit_user(foo.username, 'reviews', [])
    edit_user(foo.username, 'role', 'Columnist')
    make_writer_id(foo.username)


def new_member(form):
    new_member = {}
    # Use dict comprehension
    for field in form.cleaned_data:
        if field not in ['password', 'confirm']:
            new_member[field] = str(form.cleaned_data[field])

    new_member['state'] = 'request'
    new_member['reviews'] = []

    writers = mongo_calls('user')
    writers.update(
        {'email': form.cleaned_data['email']},
        {'$set': new_member},
        False,
        False
    )
    return True


def edit_writer_registration_details(form):
    writers = mongo_calls('user')
    updated_writer = {}
    # dict comprehension
    for field in form.cleaned_data:
        updated_writer[field] = str(form.cleaned_data[field])
    writers.update(
        {'username': form.cleaned_data['username']},
        {'$set': updated_writer},
        False,
        False
    )
    return True


def make_username(first_name, last_name):
    first_name = first_name.replace(" ", "_")
    last_name = last_name.replace(" ", "_")
    long_name = "%s_%s" % (first_name, last_name)
    while True:
        if long_name not in User.objects.distinct('username'):
            return long_name
        else:
            long_name = "%s%i" % (long_name, random.randint(1, 9))
        if not re.match(r'^[a-zA-Z0-9_]+$', long_name):
            raise Exception(
                "Username should include only alphanumeric characters,\
                 letters and numbers")


def forgot_password_email(email):
    users = mongo_calls('user')
    user = users.find_one({"email": email})
    password = "If you see this message, please contact admin, \
                as this shouldn't be here"
    username = user['username']
    send_mail('Email verification', 'Hi Stears writer, weve made you a \
        new password: "%s" . Also, your username is "%s" incase you forgot \
        that too' % (password, username), email_host,
              [email], fail_silently=False)


def print_links():
    for link in params.glo_trybe_data:
        print make_url(params.glo_trybe_data[link], True)
        print make_url(params.glo_trybe_data[link], False)


def request_json(URL):
    try:
        website = urlopen(URL, timeout=10)
        return json.loads(website.read())

    except Exception:
        return {}


def suggest_nse_article(username, article_id):
    users = mongo_calls('user')
    users.update(
        {'username': username},
        {'$push': {'suggested_articles': int(article_id)}}, False)


# Optimize query here
def update_writers_article(username, form):
    headline = form.cleaned_data['headline']
    content = form.cleaned_data['content']
    category = form.cleaned_data['categories']

    article = {
        'headline': headline,
        'content': stears_italics(content),
        'category': category,
        'type': 'writers_article'
    }

    article_id = form.cleaned_data['article_id']

    # Use mongo update
    articles = mongo_calls('articles')
    existing_article = articles.find_one({'article_id': int(article_id)})
    for key, value in article.items():
        if key not in params.persistent:
            existing_article[key] = value

    articles.save(existing_article)
    # print "%s updated article with id %s"%(username,article_id)
    return existing_article


def add_writers(article_id, usernames):
    articles = mongo_calls('articles')
    articles.update(
        {'article_id': article_id},
        {'$addToSet': {'writers.others': {'$each': usernames}}},
        False,
        False
    )


def remove_writers(article_id, usernames):
    articles = mongo_calls('articles')
    articles.update(
        {'article_id': article_id},
        {'$pullAll': {'writers.others': usernames}},
        False,
        False
    )

# Pretty damn inefficient!!!!!!


def submit_writers_article(article_id):
    article_id = int(article_id)
    articles = mongo_calls('articles')
    if True:
        articles.update(
            {'article_id': article_id},
            {'$set': {'state': 'submitted',
             'reviewer': 'No reviewer', 'time': datetime.now()}},
            False, False
        )
        return False


def make_writers_article(form, username):
    nse_article_id = form.cleaned_data.get('nse_headlines', 0)
    headline = form.cleaned_data['headline']
    content = form.cleaned_data['content']
    category = form.cleaned_data.get('categories', "Other")
    article = {
        'nse_article_id': nse_article_id,
        'headline': headline,
        'content': stears_italics(content),
        'category': category,
        'time': datetime.now(),
        'writer': username,
        'writers': {'original': username, 'others': []},
        'reviewer': '',
        'state': 'in_progress',
        'type': 'writers_article'
    }

    # article = request_to_write(article)
    return article


def stears_italics(content):
    return content


def make_comment(username, article_id, comment):
    comment_body = {
        'time': datetime.now(),
        'writer': username,
        'comment': comment,
    }
    articles = mongo_calls('articles')
    articles.update(
        {'article_id': article_id},
        {'$push': {'comments': comment_body}},
        False,
        False
    )


def article_key_words(pk, word, **kwargs):
    articles = mongo_calls('articles')
    nse_news = mongo_calls('nse_news')

    other = kwargs.get('other', '')
    if other and other != 'None':
        word = other
    elif word == 'None':
        return None

    response = articles.update(
        {'article_id': pk},
        {'$addToSet': {'keywords': word}},
        False,
        False
    )
    nse_news.update(
        {'type': 'tags'},
        {'$addToSet': {'keywords': word}},
        True,
        False
    )
    if response['nModified']:
        return word
    return None


def request_to_write(article):
    username = article['writer']
    user = User.objects.get(username=username)
    if user.is_superuser or user.is_staff:
        return article
    if article['category'] in params.request_categories:
        article['visible'] = False
    return article


def accept_to_write(article_id):
    articles = mongo_calls('articles')
    articles.update(
        {
            "article_id": int(article_id),
            'category': {'$in': params.request_categories},
            'visible': False},
        {'$set': {'visible': True}},
        False,
        False
    )


def move_to_trash(pk):
    articles = mongo_calls('articles')
    bin = mongo_calls('bin')
    users = mongo_calls('users')
    article = articles.find_one({'article_id': int(pk)})
    nse_article_id = int(article['nse_article_id'])

    users.update(
        {'username': article['writer']},
        {'$pull': {'articles': int(pk)}},
        False,
        False
    )

    if nse_article_id:
        articles.update(
            {'article_id': int(nse_article_id), 'type': 'nse_article'},
            {'$pull': {'versions': int(pk)}},
            False,
            False
        )

    article['binned'] = True
    bin.insert(article)
    articles.remove({'article_id': int(pk)})


def revive_from_trash(pk):
    articles = mongo_calls('articles')
    bin = mongo_calls('bin')
    users = mongo_calls('users')
    article = bin.find_one({'article_id': int(pk)})
    nse_article_id = int(article['nse_article_id'])

    users.update(
        {'username': article['writer']},
        {'$push': {'articles': int(pk)}},
        False,
        False
    )

    if nse_article_id:
        articles.update(
            {'article_id': int(nse_article_id), 'type': 'nse_article'},
            {'$push': {'versions': int(pk)}},
            False,
            False
        )

    article['binned'] = False
    articles.insert(article)
    bin.remove({'article_id': int(pk)})


def site_ready(article):
    p = article.get('photo', '')
    if not (p and len(article.get('keywords', []))):
        # Photo has not yet been assigned
        # No tags
        return False

    link = p.replace('/media/', '')
    photo = ArticleImageModel.objects.filter(docfile=link)
    if not photo.count():
        # Photo does not exist in the database.
        # Maybe deleted? Use change photo!
        return False
    return True


def migrate_article(article_id):
    articles = mongo_calls('articles')
    migrations = mongo_calls('migrations')
    article = articles.find_one(
        {'article_id': article_id, 'type': 'writers_article'})

    if not site_ready(article):
        return False

    try:
        article['state'] = 'site_ready'
        article['time'] = datetime.now()
        migrations.update({'article_id': article_id}, article, upsert=True)
        articles.remove({'article_id': article_id})
    except Exception:
        raise Exception


def retract(pk):
    pk = int(pk)
    m = mongo_calls('migrations')
    a = mongo_calls('articles')
    article = m.find_one({'article_id': pk})

    if article and article.get('state') == 'site_ready':
        try:
            article['state'] = 'submitted'
            a.update({'article_id': pk}, article, upsert=True)
        except Exception:
            raise Exception
    return True


def save_writers_article(article):
    articles = mongo_calls('articles')
    users = mongo_calls('users')
    nse_article_id = int(article['nse_article_id'])
    article = add_id_to_dict(article)
    username = article['writer']
    article_id = int(article['article_id'])

    users.update(
        {'username': username},
        {'$push': {'articles': article_id}, '$pull': {
            'suggested_articles': nse_article_id}},
        False,
        False,
    )

    if nse_article_id:
        articles.update(
            {'article_id': nse_article_id, 'type': 'nse_article'},
            {'$push': {'versions': article_id}},
            True,
            False,
        )
    else:
        articles.save(article)
        # print 'ERROR, no article to save versions'

    return article['article_id']


def get_nse_headlines():
    return [(0, 'None')]


def add_id_to_dict(article):
    available_id = available_article_id()
    article['article_id'] = available_id
    nse_news = mongo_calls('nse_news')
    nse_news.update(
        {'type': 'register'},
        {'$push': {'article_ids': available_id}},
        False,
        False
    )
    return article


# Can be further optimised
def available_article_id():
    nse_news = mongo_calls('nse_news')
    register = nse_news.find_one({'type': 'register'})
    if not register:
        register = {'type': 'register', 'article_ids': []}
        nse_news.insert(register)
    article_ids = register.get('article_ids', [])
    return first_missing_number(article_ids)


def drop_everything():
    for name in ['articles', 'user', 'bin', 'migrations', 'nse_news']:
        mongo_calls[name].drop()
    from stears.utils import do_magic_user
    do_magic_user()

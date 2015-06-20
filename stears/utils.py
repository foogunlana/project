from urllib2 import urlopen
from pymongo import MongoClient
from threading import Thread, active_count
import threading
from mongoengine.django.auth import User
from django.core.mail import send_mail
from writers.settings import EMAIL_HOST_USER as email_host

# import enchant
import params
import json
import time
import re
import random


def get_mongo_client():
    client = None
    
    while True:
        if client != None:
            print "YIELD CLIENT"
            yield client
        else:
            try:
                # print "Getting new Mongo Client"
                client = MongoClient(params.MONGO_URI)
                print "NEW CLIENT"
            except Exception as e:
                print e
                raise Exception


def handle_uploaded_file(image):
    with open('media/articleImages/', 'wb+') as destination:
        for chunk in image.chunks():
            destination.write(chunk)


def mongo_calls(collection_name):
    client = NseNews.client
    try:
        collection = client[params.db][collection_name]
    except Exception as e:
        print e
        raise Exception
    return collection


def make_new_quote(body, author):
    onsite = mongo_calls('onsite')
    articles = mongo_calls('articles')
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
    edit_user(foo.username, 'role', 'stearsColumnist')
    make_writer_id(foo.username)


def new_member(form):
    new_member = {}
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
    long_name = "%s_%s" % (first_name, last_name)
    while True:
        if long_name not in User.objects.distinct('username'):
            return long_name
        else:
            long_name = "%s%i" % (long_name, random.randint(1, 9))
        if not re.match(r'^[a-zA-Z0-9_]+$', long_name):
            raise Exception(
                "Username should include only alphanumeric characters, letters and numbers")


def forgot_password_email(email):
    users = mongo_calls('user')
    user = users.find_one({"email": email})
    password = "If you see this message, please contact admin, as this shouldn't be here"
    username = user['username']
    send_mail('Email verification', 'Hi Stears writer, weve made you a new password: "%s" . Also, your username is "%s" incase you forgot that too' % (password, username), email_host,
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
        {'username': username}, {'$push': {'suggested_articles': int(article_id)}}, False)


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

    articles = mongo_calls('articles')
    existing_article = articles.find_one({'article_id': int(article_id)})
    for key, value in article.items():
        if key not in params.persistent:
            existing_article[key] = value

    articles.save(existing_article)
    # print "%s updated article with id %s"%(username,article_id)


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


def put_in_review(article_id):
    article_id = int(article_id)
    articles = mongo_calls('articles')
    article = articles.find_one(
        {'article_id': article_id}, {'_id': 0, 'category': 1, 'writers': 1})
    writers = article['writers']['others']
    writers.append(article['writers']['original'])

    category = article['category']

    if (category == 'stearsTutorial') or (category == 'stearsColumn'):
        articles.update(
            {'article_id': article_id},
            {'$set': {'state': 'submitted', 'reviewer': 'No reviewer'}},
            False, False
        )
        return False

    users = mongo_calls('user')
    reviewers = users.find(
        {'username': {'$nin': writers}}).distinct('username')
    reviewer = random.choice(reviewers)

    users.update(
        {'username': reviewer},
        {'$addToSet': {'reviews': article_id}},
        False, False
    )
    articles.update(
        {'article_id': article_id},
        {'$set': {'state': 'in_review', 'reviewer': reviewer}},
        False, False
    )


def submit_writers_article(article_id, review):
    articles = mongo_calls('articles')
    review['time'] = time.time()
    articles.update({'article_id': int(article_id)},
                    {'$set': {'state': 'submitted'}, '$addToSet': {'reviews': review}}, False, False)


def make_writers_article(form, username):
    nse_article_id = form.cleaned_data.get('nse_headlines', 0)
    headline = form.cleaned_data['headline']
    content = form.cleaned_data['content']
    category = form.cleaned_data.get('categories', "Other")
    category = "%s%s" % ('stears', category.replace(' ', '_'))
    article = {
        'nse_article_id': nse_article_id,
        'headline': headline,
        'content': stears_italics(content),
        'category': category,
        'time': time.time(),
        'writer': username,
        'writers': {'original': username, 'others': []},
        'reviewer': '',
        'state': 'in_progress',
        'type': 'writers_article'
    }

    article = request_to_write(article)
    return article


def stears_italics(content):
    content = content.replace(
        'stears', '<i>stears</i>').replace('Stears', '<i>Stears</i>')
    return content


def make_comment(username, article_id, comment):
    comment_body = {
        'time': time.time(),
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
        return

    articles.update(
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


def migrate_article(article_id):
    articles = mongo_calls('articles')
    migrations = mongo_calls('migrations')

    try:
        article = articles.find_one(
            {'article_id': article_id, 'type': 'writers_article'})
        article['state'] = 'on_site'
        migrations.update({'article_id': article_id}, article, True)
        if article_id:
            articles.remove({'article_id': article_id})
    except Exception:
        # print e
        raise Exception


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
    articles = mongo_calls('articles')
    headlines = []
    for article in articles.find({'type': 'nse_article'}, {'article_id': 1, 'headline': 1, '_id': 0}):
        headline_tuple = (article['article_id'], article['headline'])
        headlines.append(headline_tuple)
    return [(0, 'None')] + headlines


def organise_new_articles():
    collection_with_news = mongo_calls('nse_news')
    articles = mongo_calls('articles')

    new_bulletins = collection_with_news.find_one({'type': 'news'})
    if new_bulletins:
        new_bulletins = new_bulletins.get('Bulletins', '')
        if not new_bulletins:
            # print "NOT WORKING: BUllETINS WERE NOT DOWNLOADED"
            raise Exception
        for article in new_bulletins:
            new_article = {
                'headline': article.get('Headline', ''),
                'content': article.get('Content', ''),
                'time': article.get('Time', ''),
                'versions': [],
                'type': 'nse_article',
            }
            existing_article = articles.find_one({
                'headline': article.get('Headline', ''),
                'time': article.get('Time', ''),
                'type': 'nse_article',
            })
            if existing_article:
                for key, value in new_article.items():
                    if key != 'versions':
                        existing_article[key] = value
                articles.save(existing_article)
            else:
                new_article = add_id_to_dict(new_article)
                articles.insert(new_article)


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


def thread_stuff():
    nse_news = mongo_calls('nse_news')
    while params.thread_running:
        URL = make_url(params.glo_trybe_data['news'], False)
        data = request_json(URL)
        data['type'] = 'news'
        nse_news.update({'type': 'news'}, data, True)
        organise_new_articles()
        print "sleeping....................................................", threading.enumerate()
        time.sleep(params.nse_period)


class Singleton(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance


class NseNews(Singleton):
    nse_thread = Thread(target=thread_stuff, args=())
    name = "NseNewsThread"
    nse_thread.daemon = True

    client = next(get_mongo_client())

    def startThread(self):
        if active_count() == 1:
            try:
                threading.enumerate()
                self.nse_thread.start()
                threading.enumerate()
            except Exception:
                raise Exception
                # print "Could not start thread"


def drop_everything():
    client = NseNews.client
    for name in ['articles', 'user', 'bin', 'migrations', 'nse_news']:
        client.stears[name].drop()
    from stears.utils import do_magic_user
    do_magic_user()


nse_news_object = NseNews()

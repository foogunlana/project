from urllib2 import urlopen
from pymongo import MongoClient
from threading import Thread, active_count
import threading
from datetime import datetime
from mongoengine.django.auth import User
from django.core.mail import send_mail
from writers.settings import EMAIL_HOST_USER as email_host

import params
import json
import time


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


def make_writer_id(writer):
    collection = client.stears.user
    writer_dict = collection.find_one({'username': writer})
    ids = collection.distinct('writer_id')
    if ids and (None not in ids):
        max_id = max(ids)
        writer_dict['writer_id'] = int(max_id) + 1
    else:
        writer_dict['writer_id'] = 1
    collection.save(writer_dict)


def edit_user(username, key, item):
    user = client.stears.user.find_one({'username': username})
    # current_item = user.get(key, 'NOVALUE')
    user[key] = item
    client.stears.user.save(user)
    # print "%s's %s has been changed from %s to
    # %s"%(username,key,current_item,item)


def do_magic_user():
    foo = User()
    foo.username = 'stearsadmin'
    foo.email = 'stears@stears.com'
    foo.password = params.cheeky_password
    foo.is_superuser = True
    foo.is_staff = True
    foo.save()
    make_writer_id(foo.username)

    foo = User()
    foo.username = 'folusoogunlana'
    foo.email = 'foogunlana@gmail.com'
    foo.password = params.cheeky_password
    foo.is_superuser = True
    foo.is_staff = True
    foo.save()
    make_writer_id(foo.username)

    foo = User()
    foo.username = 'foo'
    foo.email = 'foo@foo.com'
    foo.password = params.cheeky_password
    foo.save()
    edit_user('foo', 'state', 'request')
    make_writer_id(foo.username)


def forgot_password_email(email):
    user = client.stears.user.find_one({"email": email})
    password = str(user['password'])
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
        # print e
        return {}


def unique(username, key):
    if client.stears.writers.find_one({key: username}):
        return False
    return True


def nse_time_string(string):
    bin = ['/Date(', '000+0100)/']
    for rubbish in bin:
        string = string.replace(rubbish, '')
    # return time.asctime(time.localtime(int(num)))
    return datetime.fromtimestamp(int(string)).strftime('%Y-%m-%d %H:%M:%S')


def retrieve_values(key, doc, collection):
    items = []
    for user in collection.find(doc):
        items.append(user.get(key, ''))
    return items


def suggest_nse_article(username, article_id):
    users = client.stears.user
    user = users.find_one({'username': username})
    user['suggested_articles'] = list(
        set(user.get('suggested_articles', []) + [article_id]))
    users.save(user)


def update_writers_article(username, form):
    headline = form.cleaned_data['headline']
    content = form.cleaned_data['content']

    article = {
        'headline': headline,
        'content': content,
        'time': time.time(),
        'state': 'in_progress',
        'type': 'writers_article'
    }

    article_id = form.cleaned_data['article_id']

    articles = client.stears.articles
    existing_article = articles.find_one({'article_id': int(article_id)})
    for key, value in article.items():
        if key not in params.persistent:
            existing_article[key] = value
    existing_article['state'] = 'in_progress'

    articles.save(existing_article)
    # print "%s updated article with id %s"%(username,article_id)


def submit_writers_article(article_id):
    articles = client.stears.articles
    article = articles.find_one({'article_id': int(article_id)})
    article['state'] = 'submitted'
    articles.save(article)


def make_writers_article(form, username):
    nse_article_id = form.cleaned_data.get('nse_headlines', 0)
    headline = form.cleaned_data['headline']
    content = form.cleaned_data['content']
    category = form.cleaned_data.get('categories', "Other")
    article = {
        'nse_article_id': nse_article_id,
        'headline': headline,
        'content': content,
        'category': category,
        'time': time.time(),
        'writer': username,
        'state': 'in_progress',
        'type': 'writers_article'
    }

    article = request_to_write(article)
    return article


def request_to_write(article):
    print article
    username = article['writer']
    user = User.objects.get(username=username)
    if user.is_superuser or user.is_staff:
        return article
    if article['category'] in params.request_categories:
        article['visible'] = False
    return article


def accept_to_write(article_id):
    articles = client.stears.articles
    article = articles.find_one({"article_id": int(article_id)})
    if article.get('category', None) in params.request_categories:
        if not article.get('visible', True):
            article['visible'] = True
        # else:
        # 	print "Article was never requested or has already been approved!"
    articles.save(article)


def move_to_trash(pk):
    articles = client.stears.articles
    bin = client.stears.bin
    users = client.stears.user

    article = articles.find_one({'article_id': int(pk)})
    writer = users.find_one({'username': article['writer']})
    writer['articles'] = list(set(writer['articles']) - set([int(pk)]))
    nse_article_id = int(article['nse_article_id'])

    if nse_article_id:
        nse_article_id = int(nse_article_id)
        nse_article = articles.find_one(
            {'article_id': nse_article_id, 'type': 'nse_article'})
        print nse_article_id, nse_article
        nse_article['versions'] = list(
            set(nse_article['versions']) - set([int(pk)]))
        articles.save(nse_article)

    users.save(writer)
    bin.insert(article)
    articles.remove({'article_id': int(pk)})


def migrate_article(article_id):
    articles = client.stears.articles
    migrations = client.stears.migrations

    try:
        article = articles.find_one(
            {'article_id': article_id, 'type': 'writers_article'})
        migrations.update(article, article, True)
        if article_id:
            articles.remove({'article_id': article_id})
    except Exception:
        # print e
        raise Exception


def save_writers_article(article):
    articles = client.stears.articles
    nse_article_id = int(article['nse_article_id'])
    article = add_id_to_dict(article)

    username = article['writer']
    users = client.stears.user
    writer = users.find_one({'username': username})
    writer['articles'] = writer.get('articles', []) + [article['article_id']]

    if nse_article_id and nse_article_id != 'None':
        nse_article = articles.find_one(
            {'article_id': int(nse_article_id), 'type': 'nse_article'})
        if nse_article:
            nse_article['versions'] = nse_article[
                'versions'] + [article['article_id']]
            articles.save(nse_article)

            suggested_articles = writer.get('suggested_articles', [])
            writer['suggested_articles'] = list(
                set(suggested_articles) - set([nse_article_id]))
        else:
            # print 'ERROR, no article to save versions'
            raise Exception

    users.save(writer)
    articles.save(article)
    return article['article_id']


def get_nse_headlines():
    collection = client.stears.articles
    headlines = []
    for article in collection.find({'type': 'nse_article'}):
        headline_tuple = (article['article_id'], article['headline'])
        headlines.append(headline_tuple)
    return [(0, 'None')] + headlines


def organise_new_articles():
    collection_with_news = client.stears.nse_news
    articles = client.stears.articles
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
    register = client.stears.nse_news.find_one({'type': 'register'})
    register['article_ids'] = register.get('article_ids', []) + [available_id]
    client.stears.nse_news.save(register)
    return article


def available_article_id():
    register = client.stears.nse_news.find_one({'type': 'register'})
    if not register:
        register = {'type': 'register', 'article_ids': []}
        # print register,'register'
        client.stears.nse_news.insert(register)
    article_ids = register.get('article_ids', [])

    if article_ids:
        max_id = max(article_ids)
    else:
        max_id = 1

    all_numbers = set([number for number in range(1, max_id + 2)])
    available = all_numbers - set(article_ids)
    return int(min(available))


# Change the way that the articles are stored inside the database
def thread_stuff():
    while params.thread_running:
        # print 'thread_running'
        URL = make_url(params.glo_trybe_data['news'], False)
        data = request_json(URL)
        data['type'] = 'news'
        client.stears.nse_news.update({'type': 'news'}, data, True)
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
    client.stears.articles.drop()
    client.stears.nse_news.drop()
    client.stears.bin.drop()
    client.stears.user.drop()
    from stears.utils import do_magic_user
    do_magic_user()


nse_news_object = NseNews()
client = NseNews.client

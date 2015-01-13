from django import template
from stears.params import remove_from_date
from mongoengine.django.auth import User
from stears.utils import mongo_calls
from stears.permissions import editor
import time

register = template.Library()


@register.filter("mongo_id")
def mongo_id(value):
    return str(value['_id'])


@register.filter("is_editor")
def is_editor(user):
    if editor(user):
        return True
    return False
    # do the cool stuff


@register.filter("full_category")
def full_category(short):
    pass


@register.filter("can_suggest")
def can_suggest(username, article):
    writer = article.get('writer', '')
    if editor(username) and not writer:
        return True
    return False


@register.filter("article_array")
def article_array(pk):
    article_collection = mongo_calls('articles')
    nse_article = article_collection.find_one({'article_id': int(pk)})
    versions = nse_article.get('versions', [])
    articles = []
    articles = articles + [article for article in article_collection.find(
        {'article_id': {'$in': versions}})]
    return articles


@register.filter("nse_date")
def nse_date(value):
    value = str(value)
    for item in remove_from_date:
        value = value.replace(item, '')
    try:
        value = int(value)
    except ValueError:
        value = float(value)
    return time.asctime(time.localtime(value))


@register.filter("can_write")
def can_write(username, article):
    writer = article.get('writer', '')
    state = article.get('state', '')

    if state == 'in_progress':
        if (str(username) == str(writer)):
            return True
        return False

    elif state == 'submitted':
        if editor(username):
            return True
        return False

    return False


@register.filter("get_headline")
def get_headline(pk):
    article_collection = mongo_calls('articles')
    article = article_collection.find_one({'article_id': int(pk)})
    if article:
        return article['headline']
    return None


@register.filter('can_approve')
def can_approve(username, article):
    if article['state'] != 'submitted':
        return False
    if is_editor(username):
        return True
    return False

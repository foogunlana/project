from django import template
from stears.params import remove_from_date
from mongoengine.django.auth import User
from stears.utils import client
import time

register = template.Library()


@register.filter("mongo_id")
def mongo_id(value):
    return str(value['_id'])


@register.filter("is_editor")
def is_editor(user):
    writer = User.objects.get(username=str(user))
    if writer.is_superuser or writer.is_staff:
        return True
    # do the cool stuff


@register.filter("full_category")
def full_category(short):
    pass


@register.filter("can_suggest")
def can_suggest(username, article):
    writer = article.get('writer', '')
    user = User.objects.get(username=username)
    if (user.is_staff or user.is_superuser) and not writer:
        return True
    return False


@register.filter("article_array")
def article_array(pk):
    nse_article = client.stears.articles.find_one({'article_id': int(pk)})
    versions = nse_article.get('versions', [])
    articles = []
    for version_pk in versions:
        articles = articles + \
            [client.stears.articles.find_one({'article_id': int(version_pk)})]
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

    user = User.objects.get(username=username)
    if user.is_superuser or writer == None:
        return True

    if (str(username) == str(writer)):
        if article.get('state', '') != 'submitted':
            return True
    return False


@register.filter("get_headline")
def get_headline(pk):
    article = client.stears.articles.find_one({'article_id': int(pk)})
    if article:
        return article['headline']
    return None

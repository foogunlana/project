from stears.utils import mongo_calls
from abc import ABCMeta, abstractmethod
from lxml import html
from stears.models import ArticleImageModel
from django.core.cache import cache
from datetime import datetime

import stears.params as params
import htmlentitydefs
import re


def expire_page(page, sector=None):
    identifier = 'newscache:{}{}'.format(
        page, sector if sector else '')
    cache.delete(identifier)


class StearsPage(object):
    """
    A page on the Stears website.
    Attributes:
    """
    singles = ['main_feature', 'secondary']
    multiples = ['features', 'tertiaries']

    __metaclass__ = ABCMeta

    @abstractmethod
    def is_ready(self):
        return False


class Article(object):
    """
     An article object to create articles with
    """

    def __init__(self, headline, content, writer, category, article_id):
        self.headline = headline
        self.content = content
        self.writer = writer
        self.category = category
        self.article_id = article_id


class HomePage(StearsPage):

    def __init__(self, *args, **kwargs):
        super(HomePage, self).__init__()
        self.main_feature = kwargs.get('main_feature', None)
        self.daily_column = kwargs.get('daily_column', None)
        self.secondary = kwargs.get('secondary', None)
        self.tertiaries = kwargs.get('tertiaries', None)
        self.features = kwargs.get('features', None)
        self.quote = kwargs.get('quote', None)

    def is_ready(self):
        return not self.vacancies()

    def vacancies(self):
        return [key for key, value in self.__dict__.items() if not value]

    def articles(self, func=lambda x: x):
        page = self.__dict__
        singles = [func(page[key]) for key in self.singles if page[key]]
        multiples = []
        for key in self.multiples:
            section = page[key]
            multiples = multiples + [func(item) for item in section if item]
        return singles + multiples


class BusinessPage(StearsPage):

    def __init__(self, *args, **kwargs):
        super(BusinessPage, self).__init__()
        self.main_feature = kwargs.get('main_feature', None)
        self.features = kwargs.get('features', None)
        self.sector = kwargs.get('sector', None)

    def is_ready(self):
        return False

    def vacancies(self):
        return [key for key, value in self.__dict__.items() if not value]

    def articles(self, func=lambda x: x):
        page = self.__dict__
        singles = [func(page[key]) for key in self.singles if page.get(key)]
        multiples = []
        for key in self.multiples:
            section = page.get(key)
            if section:
                multiples = multiples + [func(item) for item in section if item]
        return singles + multiples


def articles_on_site(func=lambda x: x):
    onsite = mongo_calls('onsite')
    home_page = onsite.find_one({'page': 'home'})
    b_e_pages = list(onsite.find({'page': 'b_e'}, multi=True))

    home = HomePage(**home_page)
    home_items = home.articles(func)

    b_e_items = []
    for b_e_page in b_e_pages:
        b_e = BusinessPage(**b_e_page)
        b_e_items = b_e_items + b_e.articles(func)

    return home_items + b_e_items


def locate(article_id):
    onsite = mongo_calls('onsite')
    home_page = onsite.find_one({'page': 'home'})
    home = HomePage(**home_page)
    locations = []
    if article_id in home.articles(lambda a: a['article_id']):
        locations = [{'page': 'home'}]

    b_e_pages = list(onsite.find({'page': 'b_e'}, multi=True))
    for b_e_page in b_e_pages:
        b_e = BusinessPage(**b_e_page)
        if article_id in b_e.articles(lambda a: a['article_id']):
            locations = locations + [{'page': 'b_e', 'sector': b_e.sector}]

    return locations


def htmltag_text(html_string):
    tree = html.fromstring(html_string)
    paragraphs = list(tree.xpath("//p/text()"))
    if not paragraphs:
        paragraphs = list(tree.xpath("//span/text()"))
    return reversed(paragraphs)


def remove_special_characters(mystring):
    mystring = re.sub(
        '&([^;]+);',
        lambda m: unichr(htmlentitydefs.name2codepoint[m.group(1)]),
        mystring)
    return mystring.encode('utf-8')


def summarize(article):
    try:
        paragraphs = htmltag_text(article['content'])
        for p in paragraphs:
            if len(p) > 200:
                summary = p
        summary = remove_special_characters(summary)
    except Exception:
        summary = summarize2(article)
    return summary


def summarize2(article):
    try:
        tree = html.fromstring(article['content'])
        text = remove_special_characters(tree.text_content())
    except Exception:
        return 'Summary unavailable'
    return text[:200]


def photoset(link):
    photo = ArticleImageModel.objects.get(docfile=link)
    photoset = {'photop': photo.picker.url, 'photof': photo.feature.url,
                'photomfm': photo.main_feature_mobile.url,
                'photomf': photo.main_feature.url}
    return photoset


def put_article_on_page(page, section, article_id, sector=None, number=None):
    article_id = int(article_id)
    articles = mongo_calls('migrations')
    onsite = mongo_calls('onsite')
    article = articles.find_one({'article_id': article_id})

    if not article.get('summary', None):
        article['par1'] = summarize(article)
    else:
        article['par1'] = article.get('summary')

    link = article.get('photo', '').replace('/media/', '')
    article['photoset'] = photoset(link)

    key = 'lposted' if article.get('posted') else 'posted'

    article[key] = datetime.now()
    posted = {key: datetime.now()}
    articles.update({'article_id': article_id},
                    {'$set': posted})

    if sector:
        find_doc = {'page': page, 'sector': sector}
    else:
        find_doc = {'page': page}
    if number is not None:
        number = int(number)
        onsite.update(find_doc,
                      {'$set': {'active': True,
                       '{}.{}'.format(section, number): article}},
                      upsert=True)
    else:
        onsite.update(find_doc,
                      {'$set': {'active': True, section: article}},
                      upsert=True)

    if page == 'home':
        if section == 'features':
            expire_page(page='index', sector='features')
        if section == 'secondary' or section == 'tertiaries':
            expire_page(page='index', sector='top_picks')

    pcs = {'home': 'index', 'b_e': 'business'}
    expire_page(page=pcs[page], sector=sector)


def allocator_commands(page_name, sector=None):
    onsite = mongo_calls('onsite')
    commands = []
    singles = ['main_feature', 'secondary']
    multiples = ['tertiaries', 'features']
    alias = {'index': 'home', 'business': 'b_e'}
    page_name = alias.get(page_name, page_name)

    if sector:
        page = onsite.find_one({'page': page_name, 'sector': sector})
    else:
        page = onsite.find_one({'page': page_name})
    if not page:
        return None

    for section in singles:
        try:
            command = {
                'page': page_name,
                'section': section,
                'article_id': page[section]['article_id'],
                'sector': sector,
                'number': None,
            }
            commands += [command]
        except Exception, e:
            print e

    for section in multiples:
        if not page.get(section):
            continue
        count = len(page[section])
        for number in range(count):
            try:
                command = {
                    'page': page_name,
                    'section': section,
                    'article_id': page[section][number]['article_id'],
                    'sector': sector,
                    'number': number,
                }
                commands += [command]
            except Exception, e:
                print e
    return commands


def reset_page(page):
    onsite = mongo_calls('onsite')
    if page == 'b_e':
        for sector in params.sectors.values():
            onsite.update({'page': 'b_e', 'sector': sector},
                          {'page': 'b_e', 'sector': sector,
                           'features': [], 'active': True},
                          upsert=True)
    if page == 'home':
        onsite.update(
            {'page': 'home'},
            {'page': 'home', 'features': [], 'tertiaries': [],
             'daily_column': {}, 'active': True},
            upsert=True)



def obj_dict_recursive(obj):
    obj_dict = dict(obj.__dict__)
    for key in obj_dict:
        item = obj_dict[key]
        if hasattr(item, '__dict__'):
            obj_dict[key] = obj_dict_recursive(item)
        elif type(item) == list:
            elements = []
            for element in item:
                if hasattr(element, '__dict__'):
                    elements.append(obj_dict_recursive(element))
                else:
                    elements.append(element)
            obj_dict[key] = elements
    return obj_dict

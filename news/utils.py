from stears.utils import mongo_calls
from lxml import html

import stears.params as params
import htmlentitydefs
import re


def htmltag_text(html_string, tag):
    tree = html.fromstring(html_string)
    paragraphs = list(reversed(tree.xpath("//p/text()")))
    return paragraphs


def remove_special_characters(mystring):
    mystring = re.sub(
        '&([^;]+);',
        lambda m: unichr(htmlentitydefs.name2codepoint[m.group(1)]),
        mystring)
    return mystring.encode('utf-8')


def put_article_on_page(page, section, article_id, sector=None, number=None):
    articles = mongo_calls('migrations')
    onsite = mongo_calls('onsite')
    article = articles.find_one({'article_id': article_id})

    if not article.get('summary', None):
        try:
            par1 = remove_special_characters(
                htmltag_text(article['content'], 'p').pop())
        except Exception:
            par1 = 'Summary not available'

        article['par1'] = par1

    if sector:
        find_doc = {'page': page, 'sector': sector}
    else:
        find_doc = {'page': page}
    if number:
        onsite.update(find_doc,
                      {'$set': {'active': True,
                       '{}.{}'.format(section, number): article}},
                      upsert=True)
    else:
        onsite.update(find_doc,
                      {'$set': {'active': True, section: article}},
                      upsert=True)


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

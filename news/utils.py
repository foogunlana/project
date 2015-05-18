from abc import ABCMeta, abstractmethod
from stears.utils import mongo_calls

import copy


class StearsPage(object):
    """
    A page on the Stears website.

    Attributes:

    """

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
        self.market_snapshot = kwargs.get('market_snapshot', None)
        self.daily_column = kwargs.get('daily_column', None)
        self.secondary = kwargs.get('secondary', None)
        self.tertiaries = kwargs.get('tertiaries', None)
        self.extras = kwargs.get('extras', None)
        self.quote = kwargs.get('quote', None)

    def is_ready(self):
        return not self.vacancies()

    def vacancies(self):
        vacancies = []
        for key, value in self.__dict__.items():
            if value is None:
                vacancies = vacancies + [key]
        return vacancies


class BusinessPage(StearsPage):

    def __init__(self, *args, **kwargs):
        super(BusinessPage, self).__init__()
        self.main_feature = kwargs.get('main_feature', None)
        self.business_posts = kwargs.get('business_posts', None)

    def is_ready(self):
        return False


class EconomyPage(StearsPage):
    def __init__(self, *args, **kwargs):
        super(EconomyPage, self).__init__()
        self.main_feature = kwargs.get('main_feature', None)
        self.economic_snapshot = kwargs.get('economic_snapshot', None)
        self.economy_posts = kwargs.get('economy_posts', None)

    def is_ready(self):
        return False


def put_article_on_page(page, section, article_id):
    articles = mongo_calls('migrations')
    onsite = mongo_calls('onsite')

    article = articles.find_one(
        {'article_id': article_id},
        {'headline': 1, 'content': 1, 'writer': 1, 'category': 1, 'article_id': 1})

    onsite.update(
        {'active': True, 'page': page},
        {'$set': { section: article }},
        True, False)


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


def populate_site(collection):
    # ids = [12, 17, 21, 27, 5, 22, 23]
    article_collection = mongo_calls(collection)
    items = {
        'headline': 1,
        'content': 1,
        'writer': 1,
        'category': 1,
        'article_id': 1,
        '_id': 0
    }
    articles = [article for article in article_collection.find({
        '$query': {},
        '$orderby': {'time': -1}}, items).limit(7)]

    article_list = copy.copy(articles)

    home_page = HomePage(
        main_feature=Article(**articles.pop()),
        daily_column=Article(**articles.pop()),
        secondary=Article(**articles.pop()),
        tertiaries=[
            Article(**articles.pop()),
            Article(**articles.pop())],
        extras=[
            Article(**articles.pop()),
            Article(**articles.pop())],
        quote="'If what happened in 2011 should again \
        happen in 2015, by the grace of God, the dog and \
        the baboon will all be soaked in blood.' - Buhari")

    business_page = BusinessPage(
        main_feature=Article(**article_list[0]),
        business_posts=[Article(**article) for article in article_list])

    economy_page = EconomyPage(
        main_feature=Article(**article_list[2]),
        economy_posts=[Article(**article) for article in article_list])

    home = obj_dict_recursive(home_page)
    business = obj_dict_recursive(business_page)
    economy = obj_dict_recursive(economy_page)

    home['page'] = 'home'
    business['page'] = 'business'
    economy['page'] = 'economy'

    home['active'] = True
    business['active'] = True
    economy['active'] = True

    onsite = mongo_calls('onsite')
    onsite.update({'active': True, 'page': 'home'},
                  home, True, False)
    onsite.update({'active': True, 'page': 'business'},
                  business, True, False)
    onsite.update({'active': True, 'page': 'economy'},
                  economy, True, False)


# def populate_home():
#     return
#     page = random_home('migrations')
#     page_dict = obj_dict_recursive(page)
#     page_dict['active'] = True
#     page_dict['page'] = 'home'
#     onsite = mongo_calls('onsite')
#     onsite.update({'active': True},
#                   page_dict, True, False)

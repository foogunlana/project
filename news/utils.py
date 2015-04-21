from abc import ABCMeta, abstractmethod


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

    def __init__(self, headline, body):
        assert(type(headline) == str)
        assert(type(body) == str)
        self.headline = headline
        self.body = body


class HomePage(StearsPage):

    def __init__(self, *args, **kwargs):
        super(HomePage, self).__init__(*args, **kwargs)
        self.main_feature = kwargs.get('main_feature', None)
        self.market_snapshot = kwargs.get('market_snapshot', None)
        self.daily_column = kwargs.get('daily_column', None)
        self.secondary = kwargs.get('secondary', None)
        self.tertiaries = kwargs.get('tertiaries', None)
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
        super(BusinessPage, self).__init__(*args, **kwargs)
        self.main_feature = kwargs.get('main_feature', None)
        self.business_posts = kwargs.get('business_posts', None)

    def is_ready(self):
        return False


class EconomyPage(StearsPage):
    def __init__(self, *args, **kwargs):
        super(EconomyPage, self).__init__(*args, **kwargs)
        self.main_feature = kwargs.get('main_feature', None)
        self.economic_snapshot = kwargs.get('economic_snapshot', None)
        self.economy_posts = kwargs.get('economy_posts', None)

    def is_ready(self):
        return False


def obj_dict_recursive(obj):
    obj_dict = dict(obj.__dict__)
    for key in obj_dict:
        item = obj_dict[key]
        if hasattr(item, '__dict__'):
            obj_dict[key] = obj_dict_recursive(item)
    return obj_dict

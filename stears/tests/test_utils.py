from stears import utils
from pymongo import MongoClient

import unittest
import mock

client = MongoClient()


def mock_mongo_calls(collection_name):
    # collection = client.test[collection_name]
    # return collection
    print "bla"
    return "Bla"


utils.mongo_calls = mock.Mock(return_value=mock_mongo_calls)


class TestMakeWriterId(unittest.TestCase):

    def set_up(self):
        client.test.user.drop()
        self.users = utils.mongo_calls('user')
        self.foo = {
            u'_cls': u'User',
            u'articles': [4, 6],
            u'is_staff': True,
            u'is_superuser': True,
            u'password': u'foo',
            u'username': u'foo',
            u'writer_id': 1
        }
        self.users.insert(self.foo)

    def test_database(self):
        self.foo_check = client.test.user.find_one()
        assert(self.foo_check != None)
        assert(self.foo['username'] == self.foo_check['username'])

    def test_make_writer_id(self):
        pass

    def test_basic_2(self):
        pass

    def tear_down(self):
        pass

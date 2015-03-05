from stears import utils
from pymongo import MongoClient

import unittest
import mock
import random

# client = MongoClient()


def mock_mongo_calls(collection_name):
    return "Mongo collection %s from database" % (collection_name)


utils.mongo_calls = mock.Mock(return_value=mock_mongo_calls)


class TestFirstMissingNumber(unittest.TestCase):

    def setUp(self):
        pass

    def test_first_missing_found(self):
        for i in range(1, 20):
            missing_numbers = {random.randint(1, 10), random.randint(1, 10)}
            all_numbers = set(range(1, 10)) - missing_numbers
            first_missing_number = utils.first_missing_number(all_numbers)
            self.assertEqual(
                min(missing_numbers), first_missing_number)

    def test_first_number_empty_list(self):
        all_numbers = []
        first_missing_number = utils.first_missing_number(all_numbers)
        self.assertEqual(first_missing_number, 1)

    def test_first_number_full_list(self):
        all_numbers = range(1, 20)
        first_missing_number = utils.first_missing_number(all_numbers)
        self.assertNotIn(20, range(1, 20))
        self.assertEqual(first_missing_number, 20)

    def tearDown(self):
        pass


class TestMakeUsername(unittest.TestCase):

    def setUp(self):
        self.first_name = 'myfirstname'
        self.last_name = 'mylastname'
        self.invalid_name = 'invalidname%2#'
        self.username = 'myfirstname_mylastname'

    def test_username_generation(self):
        self.assertEquals(
            utils.make_username(self.first_name, self.last_name), self.username)

    def test_username_invalidation(self):
        self.assertRaises(
            Exception, utils.make_username(self.invalid_name, self.last_name))

    def tearDown(self):
        pass

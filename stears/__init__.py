from stears.utils import mongo_calls

import pymongo


articles = mongo_calls('articles')

articles.ensure_index([("state", pymongo.ASCENDING)])
articles.ensure_index([("time", pymongo.DESCENDING)])

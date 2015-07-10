from stears.utils import mongo_calls

import pymongo


articles = mongo_calls('migrations')

try:
    articles.ensure_index([("category", pymongo.ASCENDING)])
    articles.ensure_index([("state", pymongo.ASCENDING)])
    articles.ensure_index([("time", pymongo.DESCENDING)])
    articles.ensure_index([("article_id", pymongo.DESCENDING)])
except Exception:
    pass

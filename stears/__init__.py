from stears.utils import nse_news_object, mongo_calls

import pymongo

nse_news_object.startThread()

articles = mongo_calls('articles')

articles.ensure_index([("state", pymongo.ASCENDING)])
articles.ensure_index([("time", pymongo.DESCENDING)])

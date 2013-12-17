from pymongo import MongoClient
from django.conf import settings
import sys


client = MongoClient(*settings.MONGO_CLIENT_ARGUMENTS)

if 'test' in sys.argv:
    db = client['test_' + settings.MONGO_DB]
else:
    db = client[settings.MONGO_DB]


class Document(dict):
    """For outputing in tastypie"""
    __getattr__ = dict.get


class MongoFlushMixin(object):
    """Mongo flush mixin"""
    mongo_flush = []

    def setUp(self):
        super(MongoFlushMixin, self).setUp()
        for collection in self.mongo_flush:
            db[collection].remove()

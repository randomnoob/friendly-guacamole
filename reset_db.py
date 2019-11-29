# Resets all keywords from DB to scraped=False
import json
from mongoengine import *
from items import Proxy, Key, Storage, KeywordBatch, GoogleResult


if __name__ == "__main__":
    stor = Storage()
    keys = Key.objects()
    for key in keys:
        key.update(scraped=False)
        print ("Updated key \"{}\"".format(key.kw))
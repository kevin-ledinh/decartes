# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
# from scrapy.conf import settings

class ScrapybBootsPipeline:

    def __init__(self, mongo_uri, mongo_db, mongo_col):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_col = mongo_col

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGODB_DB', 'items'),
            mongo_col=crawler.settings.get('MONGODB_COLLECTION')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.db[self.mongo_col].create_index([("product_name",pymongo.TEXT)])
        self.client.close()

    def process_item(self, item, spider):

        myquery = {"store_name": item['store_name'], "sku_no": item['sku_no']}
        
        # check if item exists
        if self.db[self.mongo_col].find(myquery).count() > 0:
            #    update
            newvalues = { "$set": dict(item) }
            self.db[self.mongo_col].update_one(myquery, newvalues)
        else:
            #    insert
            self.db[self.mongo_col].insert_one(dict(item))
        return item
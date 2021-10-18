# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BabyFoodItem(scrapy.Item):
    # define the fields for your item here like:
    store_name = scrapy.Field()
    scan_date = scrapy.Field()
    product_name = scrapy.Field()
    product_price = scrapy.Field()
    product_offer = scrapy.Field()
    product_link = scrapy.Field()
    weightUnitprice = scrapy.Field()
    product_img = scrapy.Field()
    was_price = scrapy.Field()
    sku_no = scrapy.Field()    
    product_weight_vol = scrapy.Field()

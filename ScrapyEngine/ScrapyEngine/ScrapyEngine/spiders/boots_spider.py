import scrapy
import datetime
import json
from scrapyExample.items import BabyFoodItem

class BootsSpider(scrapy.Spider):
    name = "BootsSpider"
    storeName = "Boots"
    urlJsonPath = "./urlList/bootsUrls.json"
    jsonName = "BabyToddler"
    headers = {}
    timenow = datetime.datetime.utcnow()

    def start_requests(self):
        json_file = open(self.urlJsonPath)
        json_data = json.load(json_file)
        json_file.close()
        self.headers = json_data["headers"]
        for urlObj in json_data["urlObjs"]:
            # url = urlObj["urls"]
            yield scrapy.Request(url=urlObj["urls"], headers=self.headers, callback=self.parse,dont_filter=True)
            # for i in range (1, urlObj["maxPage"] + 1):
            #     urlToScan = url + str(i)
            #     yield scrapy.Request(url=urlToScan, headers=json_data["headers"], callback=self.parse,dont_filter=True)

    def parse(self, response):
        if response.status in (302,) :
            self.logger.debug("(parse_page) Location header: %r" % response.headers['Location'])
            yield scrapy.Request(
                response.urljoin(response.headers['Location']),
                callback=self.parse)


        currentItem = BabyFoodItem()
        currentItem['store_name'] = self.storeName
        currentItem['scan_date'] = self.timenow

        productContainer = response.xpath('//div[has-class("estore_product_container")]')

        for product in productContainer:
            
            currentItem['product_name'] = product.xpath('.//div[has-class("product_name")]//a/text()').get().strip()
            currentItem['product_price'] = product.xpath('.//div[has-class("product_price")]/text()').get().strip()
            currentItem['product_offer'] = product.xpath('.//div[has-class("product_offer")]//span//a/text()').get()
            currentItem['product_link'] = product.xpath('.//div[has-class("product_name")]//a/@href').get()
            currentItem['weightUnitprice'] = product.xpath('//span[has-class("price")]//text()').get()
            currentItem['product_img'] = product.xpath('.//img[has-class("product_img")]/@src').get()
            currentItem['was_price'] = product.xpath('.//div[has-class("product_savePrice")]//span[2]/text()').get()
            currentItem['sku_no'] = currentItem['product_link'].split('-')[-1]

            yield currentItem

        if response.xpath('//a[contains(@title,"Show next page")]/@href').get() != None:
            nextPg = int(response.url[-1]) + 1
            nextPageUrl = response.url[:(len(response.url)-1)] + str(nextPg)
            self.logger.info(nextPageUrl)
            yield scrapy.Request(url=nextPageUrl, headers=self.headers, callback=self.parse,dont_filter=True)
        
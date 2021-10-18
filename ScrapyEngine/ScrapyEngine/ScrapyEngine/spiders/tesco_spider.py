import scrapy
import datetime
import json
from scrapyExample.items import BabyFoodItem

class TescoSpider(scrapy.Spider):
    name = "TescoSpider"
    storeName = "Tesco"
    urlJsonPath = "./urlList/tescoUrls.json"
    jsonName = "BabyToddler"
    tescoUrl = "https://www.tesco.com"
    headers = ""
    
    timenow = datetime.datetime.utcnow()

    def start_requests(self):
        json_file = open(self.urlJsonPath)
        json_data = json.load(json_file)
        json_file.close()
        self.headers = json_data["headers"]
        for urlObj in json_data["urlObjs"]:
            url = urlObj["urls"]
            # for i in range (1, urlObj["maxPage"] + 1):
            #     urlToScan = url + str(i)
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse,dont_filter=True)

    def parse(self, response):
        if response.status in (302,) :
            self.logger.debug("(parse) Location header: %r" % response.headers['Location'])
            yield scrapy.Request(
                response.urljoin(response.headers['Location']),
                callback=self.parse)
        
        productContainer = response.xpath('//li[contains(@class,"product-list--list-item")]')
        
        bodyTxt = response.xpath('//body/@data-redux-state').get()
        json_data = {}
        for page in json.loads(bodyTxt)['results']['pages']:
            if page != None:
                json_data = page['serializedData']
                break 

        for product in productContainer:
            currentItem = BabyFoodItem()
            currentItem['store_name'] = self.storeName
            currentItem['scan_date'] = self.timenow
            
            currentItem['product_name'] = product.xpath('.//div[contains(@class, "product-details--content")]')[0].xpath('.//h3//a/text()').get()
            
            pricePerunit = product.xpath('.//div[contains(@class, "price-per-sellable-unit")]')
            if len(pricePerunit) > 0 :
                currentItem['product_price'] = pricePerunit.xpath('.//span[contains(@class, "currency")]//text()').get() + pricePerunit.xpath('.//span[contains(@class, "value")]//text()').get()
            
            productOffer = product.xpath('.//span[contains(@class, "promo-content-small")]')
            if len(productOffer) > 0 :
                currentItem['product_offer'] = productOffer.xpath('.//span[1]/text()').get() + " "+ productOffer.xpath('.//span[2]/text()').get()
            
            currentItem['product_link'] = self.tescoUrl + str(product.xpath('.//div[contains(@class, "product-details--content")]')[0].xpath('.//h3//a/@href').get())
            
            pricePerWeight = product.xpath('.//div[contains(@class, "price-per-quantity-weight")]')
            if len(pricePerWeight) > 0 :
                currentItem['weightUnitprice'] = pricePerWeight.xpath('.//span[contains(@class, "currency")]//text()').get() + pricePerWeight.xpath('.//span[contains(@class, "value")]//text()').get() + pricePerWeight.xpath('.//span[contains(@class, "weight")]//text()').get()
            
            currentItem['sku_no'] = currentItem['product_link'].split('/')[-1]

            # itemId = product.xpath('.//div[contains(@class, "tile-content")]/@data-auto-id').get()
            if currentItem['sku_no'] in json_data:
                currentItem['product_img'] = json_data[currentItem['sku_no']]['serializedData']['product']['defaultImageUrl']
            # currentItem['product_img'] = product.xpath('.//img[contains(@class, "product-image")]/@src').get()

            currentItem['was_price'] = ""

            yield currentItem

        nextPage = response.xpath('//a[contains(@class,"pagination--button prev-next")]')[1].xpath('./@href').get()
        if nextPage != None:
            yield response.follow(url=nextPage, headers=self.headers, callback=self.parse,dont_filter=True)
        
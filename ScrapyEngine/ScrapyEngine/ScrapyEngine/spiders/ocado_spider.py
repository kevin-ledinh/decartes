import scrapy
import datetime
import json
from scrapyExample.items import BabyFoodItem

class OcadoSpider(scrapy.Spider):
    name = "OcadoSpider"
    storeName = "Ocado"
    timenow = datetime.datetime.utcnow()
    url = "file://D:/project/scrapyTut/scrapyExample/scrapyExample/urlList/ocadoToddler.html"
    morrisonsUrl = "https://www.ocado.com"
    reqBody = {}
    headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Cookie': 'CVI=5bc573d3-723e-46ec-9bb4-3d6b44e8a012; RS_18r9e7r=0.6549099197903451'
    }
    catalogUrl = ""
    foodItemList = {}

    def start_requests(self):
        # TODO: Get Urls from Json. 
        
        # for url in self.urls:
        yield scrapy.Request(url=self.url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        productContainer = response.xpath('//li[contains(@class,"fops-item--")]')

        for product in productContainer:
            currentItem = BabyFoodItem()
            currentItem['store_name'] = self.storeName
            currentItem['scan_date'] = self.timenow
            currentItem['product_name'] = product.xpath('.//h4[contains(@class, "fop-title")]//span//text()').get()
            currentItem['product_price'] = product.xpath('.//span[contains(@class, "fop-price")]//text()').get()
            currentItem['product_offer'] = product.xpath('.//div[contains(@class, "promotion-offer")]//span/text()').get()
            currentItem['product_link'] = self.morrisonsUrl + str(product.xpath('.//div[contains(@class, "fop-contentWrapper")]//a/@href').get())
            currentItem['weightUnitprice'] = product.xpath('//span[contains(@class, "unit-price")]//text()').get()
            currentItem['product_img'] = self.morrisonsUrl + str(product.xpath('.//img[has-class("fop-img")]/@src').get())
            currentItem['was_price'] = product.xpath('.//span[contains(@class, "fop-old-price")]//text()').get()

            yield currentItem
        
        


        
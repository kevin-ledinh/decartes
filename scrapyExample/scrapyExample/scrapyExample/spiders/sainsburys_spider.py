import scrapy
import datetime
import json
from scrapyExample.items import BabyFoodItem
from bs4 import BeautifulSoup

class SainsburySpider(scrapy.Spider):
    name = "SainsburysSpider"
    storeName = "Sainsbury"
    urlJsonPath = "./urlList/sainsburysUrls.json"
    jsonName = "BabyToddler"
    
    timenow = datetime.datetime.utcnow()

    def start_requests(self):
        # Get Urls from Json. TODO: try catch 
        json_file = open(self.urlJsonPath)
        json_data = json.load(json_file)
        json_file.close()
        self.headers = json_data["headers"]
        # Send request for each url to get Product ID
        for objJson in json_data[self.jsonName]:
            yield scrapy.Request(url=objJson["urls"], headers=self.headers, callback=self.parse)

    def parse(self, response):
        
        soup = BeautifulSoup(response.text, 'html.parser')

        items = soup.find_all("li", attrs={'class':'gridItem'})

        currentItem = BabyFoodItem()
        currentItem['store_name'] = self.storeName
        currentItem['scan_date'] = self.timenow

        # for product in productContainer:
        for item in items:
            
            currentItem['product_name'] = item.find("div", attrs={'class':'productNameAndPromotions'}).h3.a.get_text().strip()

            currentItem['product_price'] = item.find("p", attrs={'class':'pricePerUnit'})
            if currentItem['product_price'] != None:
                currentItem['product_price'] = currentItem['product_price'].get_text().strip()

            currentItem['product_offer'] = item.find("p", attrs={'class':'promotion'})
            if currentItem['product_offer'] != None:
                currentItem['product_offer'] = currentItem['product_offer'].get_text().strip()
            
            currentItem['product_link'] = item.find('a').get('href')
            currentItem['weightUnitprice'] = "TODO"
            currentItem['product_img'] = 'https:' + item.find("div", attrs={'class':'productNameAndPromotions'}).h3.a.img.get('src')
            currentItem['was_price'] = ""

            if item.find("input", attrs={'name':'SKU_ID'}) != None:
                currentItem['sku_no'] = item.find("input", attrs={'name':'SKU_ID'}).get('value')
            else: # if we can't find it, ignore
                continue

            yield currentItem

        # following next page if exists
        nextLink = soup.find("li", attrs={'class':'next'})
        if (nextLink != None) and (nextLink.a != None):
                yield scrapy.Request(url=nextLink.a.get('href'), headers=self.headers, callback=self.parse)

        
        
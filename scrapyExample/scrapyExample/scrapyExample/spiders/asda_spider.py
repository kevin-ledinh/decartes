import scrapy
import datetime
import json
from scrapyExample.items import BabyFoodItem

class AsdaSpider(scrapy.Spider):
    name = "AsdaSpider"
    storeName = "Asda"
    urlJsonPath = "./urlList/asdaUrls.json"
    jsonName = "BabyToddler"
    timenow = datetime.datetime.utcnow()
    urls = []
    reqBody = {}
    headers = {}
    catalogUrl = ""
    foodItemList = {} # dictionary is used here because Asda has duplicate items
    catalogHeaders = ""
    itemIndex = 0 

    def start_requests(self):
        # Get Urls from Json. TODO: try catch 
        json_file = open(self.urlJsonPath)
        json_data = json.load(json_file)
        json_file.close()
        
        self.reqBody = json_data["ReqBody"]
        self.headers = json_data["headers"]
        self.catalogUrl = json_data["catalogReq"]
        self.catalogHeaders = json_data["catalogHeaders"]
        # Send request for each url to get Product ID
        for ReqBodyObj in json_data["urlObjs"]:
            yield scrapy.Request(url=json_data["skuUrls"], headers=self.headers, body=ReqBodyObj['StoreBody'], callback=self.getRepositoryID, method='POST', cb_kwargs=dict(isle_name=ReqBodyObj["name"]))

    def getRepositoryID(self, response, isle_name):
        resJson = json.loads(response.text)
        # self.logger.info(isle_name)
        skuList = {}
        if 'tempo_cms_content' in resJson['data']:
            skuList = resJson['data']['tempo_cms_content']['zones'][1]['configs']['skus']
        elif 'tempo_items' in resJson['data']:
            skuList = resJson['data']['tempo_items']['skus']
        else:
            self.logger.warning('No SKUs is detected. Problem with ' + isle_name)
            pass
        
        self.reqBody['item_ids'].clear()
        for sku in skuList:
            self.reqBody['item_ids'].append(sku)
            
        yield scrapy.Request(url=self.catalogUrl, headers=self.catalogHeaders, body=json.dumps(self.reqBody), method='POST',callback=self.insertItems)

    def insertItems(self, response):
        resJson = json.loads(response.text)
        # self.logger.info(response.text)
        itemInfoList = resJson['data']['uber_item']['items']
        # # self.logger.info('itemInfoList length %d', len(itemInfoList))

        currentItem = BabyFoodItem()
        currentItem['store_name'] = self.storeName
        currentItem['scan_date'] = self.timenow

        for itemInfo in itemInfoList:

            currentItem['product_link'] = "https://groceries.asda.com/product/" + itemInfo['item']['sku_id']
            currentItem['sku_no'] = itemInfo['item']['sku_id']
            currentItem['product_img'] = itemInfo['item']['images']['scene7_host'] + itemInfo['item']['images']['scene7_id']
            currentItem['product_name'] = itemInfo['item']['name']
            currentItem['product_price'] = itemInfo['price']['price_info']['price']
            currentItem['weightUnitprice'] = itemInfo['price']['price_info']['price_per_uom']

            currentItem['product_offer'] = itemInfo['promotion_info'][0]['base_promotion']['item_promo_type']
                
            currentItem['was_price'] = ""
            if itemInfo['promotion_info'][0]['rollback'] != None:
                currentItem['was_price'] = itemInfo['promotion_info'][0]['rollback']['was_price']

            currentItem['product_weight_vol'] = ""
            if itemInfo['item']['extended_item_info']['weight'] != None:
                currentItem['product_weight_vol'] = itemInfo['item']['extended_item_info']['weight']

            # self.logger.info(currentItem)
            yield currentItem

        
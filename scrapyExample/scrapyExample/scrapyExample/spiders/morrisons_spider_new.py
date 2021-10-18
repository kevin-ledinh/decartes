import scrapy
import datetime
import json
from scrapyExample.items import BabyFoodItem

class MorrisonsSpiderNew(scrapy.Spider):
    name = "MorrisonsSpiderNew"
    storeName = "Morrisons"
    timenow = datetime.datetime.utcnow()
    
    morrisonsUrl = "https://groceries.morrisons.com/products/"
    webShopApi = "https://groceries.morrisons.com/webshop/api/v1/products?skus="
    imageUrl = "https://groceries.morrisons.com/productImages/"
    urlJsonPath = "./urlList/morrisonsUrls.json"
    reqBody = {}
    headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Cookie': 'CVI=5bc573d3-723e-46ec-9bb4-3d6b44e8a012; RS_18r9e7r=0.6549099197903451'
    }
    catalogUrl = ""
    foodItemList = {}

    ItemsRequestUrl = []

    def start_requests(self):
        json_file = open(self.urlJsonPath)
        json_data = json.load(json_file)
        json_file.close()
        for urlObj in json_data["urlObjs"]:
            url = urlObj["urls"]
            yield scrapy.Request(url=url, headers=self.headers, callback=self.getSkus,dont_filter=True)

    def getSkus(self, response):
        if response.status in (302,) :
            self.logger.debug("(parse_page) Location header: %r" % response.headers['Location'])
            yield scrapy.Request(
                response.urljoin(response.headers['Location']),
                callback=self.getSkus)
        
        SkuList = []
        maxItemsRequest = 0
        requestStr = ""
        
        pageInfoJson = response.xpath('//script[1]/text()').get().strip()
        # remove var declaration
        pageInfoJson = pageInfoJson.replace("window.INITIAL_STATE = ", "")
        # remove semicolon at the end
        pageInfoJson = pageInfoJson[:-1]

        pageInfoJsonObj = json.loads(pageInfoJson)

        maxItemsRequest = 30 # int(pageInfoJsonObj['catalogue']['productsPagesByRoute']['/browse/30932']['mainFopCollection']['maxDisplayFops'])

        jsonShelfName = "/browse/" + pageInfoJsonObj['http']['currentRoute'].split("-")[-1]

        for section in pageInfoJsonObj['catalogue']['productsPagesByRoute'][jsonShelfName]['mainFopCollection']['sections']:
            for fopItem in section['fops']:
                skuStr = fopItem['sku']
                SkuList.append(skuStr)
                if skuStr not in self.foodItemList:
                    currentItem = BabyFoodItem()
                    currentItem['store_name'] = self.storeName
                    currentItem['scan_date'] = self.timenow
                    currentItem['product_link'] = self.morrisonsUrl + skuStr
                    currentItem['product_img'] = self.imageUrl + skuStr[0:3] + "/" + skuStr + "_0_150x150.jpg?identifier="
                    currentItem['sku_no'] = skuStr
                    # Add new item to dictionary with key as sku
                    self.foodItemList[skuStr] = currentItem

        startIdx = 0
        endIdx = 0

        for startIdx in range(0, len(SkuList), maxItemsRequest):
            if ( startIdx + (maxItemsRequest - 1) ) >= len(SkuList):
                endIdx = len(SkuList)
            else:
                endIdx = startIdx + maxItemsRequest
            for x in range(startIdx, endIdx):
                requestStr = requestStr + SkuList[x] + ','

            self.ItemsRequestUrl.append(self.webShopApi + requestStr[:-1])
            requestStr = ""
            
        for url in self.ItemsRequestUrl:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        resJson = json.loads(response.text)

        for product in resJson:
            sku = product['sku']
            if sku in self.foodItemList:
                self.foodItemList[sku]['product_name'] = product['name']
                self.foodItemList[sku]['product_price'] = "£" + str(product['price']['current'])
                
                self.foodItemList[sku]['product_offer'] = ""
                if 'offer' in product:
                    self.foodItemList[sku]['product_offer'] = product['offer']['text']                    
                
                if 'unit' in product['price']:
                    if 'per' in product['price']['unit']:
                        self.foodItemList[sku]['weightUnitprice'] = "£" + str(product['price']['unit']['price']) + " " + product['price']['unit']['per']
                
                
                if 'image' in product:
                    self.foodItemList[sku]['product_img'] = self.foodItemList[sku]['product_img'] + product['image']['hash']
                
                self.foodItemList[sku]['product_weight_vol'] = ""
                if 'catchWeight' in product:
                    self.foodItemList[sku]['product_weight_vol'] = product['catchWeight']

                yield self.foodItemList.pop(sku)
        
        


        
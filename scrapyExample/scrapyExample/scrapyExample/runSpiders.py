from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import pymongo
import datetime

scrapySettings = get_project_settings()
logFileName = "./logs/" + datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S") + ".txt"
scrapySettings['LOG_FILE'] = logFileName

process = CrawlerProcess(scrapySettings)

# 'followall' is the name of one of the spiders of the project.
process.crawl('BootsSpider')
process.crawl('AsdaSpider')
process.crawl('MorrisonsSpiderNew')
process.crawl('OcadoSpiderNew')
process.crawl('SainsburysSpider')
process.crawl('TescoSpider')
process.start() # the script will block here until the crawling is finished
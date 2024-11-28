# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ActDataItem(scrapy.Item):
    url = scrapy.Field()
    date = scrapy.Field()
    title = scrapy.Field()
    related_documents = scrapy.Field()
    file_urls = scrapy.Field()

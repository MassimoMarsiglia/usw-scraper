# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

# author: Hang Truong

import scrapy

class CsgoSkinItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    float_value = scrapy.Field()
    timestamp = scrapy.Field()

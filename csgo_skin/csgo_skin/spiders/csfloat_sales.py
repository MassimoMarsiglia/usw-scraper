import scrapy
from csgo_skin.items import CsgoSkinItem
import json

class CSFloatSalesSpider(scrapy.Spider):
    name = 'csfloat_sales'
    allowed_domains = ['csfloat.com']
    start_urls = [
        'https://csfloat.com/api/v1/history/%E2%98%85%20Sport%20Gloves%20%7C%20Superconductor%20(Field-Tested)/sales?paint_index=10018'
    ]

    def parse(self, response):
        data = json.loads(response.text)
        if data['sales']:
            item_data = data['sales'][0]
            skin = CsgoSkinItem()
            skin['name'] = item_data['market_hash_name']
            skin['price'] = item_data['price']
            skin['float_value'] = item_data.get('float_value')
            skin['timestamp'] = item_data['sold_at']
            yield skin
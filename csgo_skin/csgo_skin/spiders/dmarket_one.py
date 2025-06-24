# import scrapy

# class DmarketOneSpider(scrapy.Spider):
#     name = 'dmarket_one'
#     start_urls = ['https://dmarket.com/ingame-items/item-list/csgo-skins']

#     custom_settings = {
#         "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
#         "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60000,
#     }

#     def start_requests(self):
#         for url in self.start_urls:
#             yield scrapy.Request(
#                 url,
#                 meta={"playwright": True}
#             )

#     def parse(self, response):
#         skin = response.css('div.item-card__name::text').get()
#         price = response.css('div.item-card__price span::text').get()

#         yield {
#             'name': skin.strip() if skin else None,
#             'price': price.strip() if price else None
#         }

import scrapy

class DmarketOneSpider(scrapy.Spider):
    name = 'dmarket_one'
    allowed_domains = ['dmarket.com']
    start_urls = [
        'https://dmarket.com/ingame-items/item-list/csgo-skins'
    ]

    def parse(self, response):
        # Scrape the first skin on the page
        skin = response.css('div.item-card__name::text').get()
        price = response.css('div.item-card__price span::text').get()
        
        yield {
            'name': skin.strip() if skin else None,
            'price': price.strip() if price else None
        }

import re
import scrapy
from typing import List

from ..models.CS2_items import SkinVariant
from ..repositories.CS2_items_repository import CS2ItemsRepository
from ..database.database import DatabaseManager


class GamerPaySpider(scrapy.Spider):
    name = "gamerpay"
    allowed_domains = ["gamerpay.gg"]
    base_url = "https://api.gamerpay.gg"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    def clean_item_name(self, raw_name: str) -> str:
        """
        Cleans a CS2 item name by:
        - Removing 'StatTrak™', 'Souvenir', and leading star (★)
        - Removing wear info in parentheses
        - Trimming whitespace
        """
        cleaned = re.sub(r'^(★\s*|StatTrak™\s+|Souvenir\s+)', '', raw_name)
        cleaned = re.sub(r'\s*\((.*?)\)$', '', cleaned)
        return cleaned.strip()

    def build_meta(self, skin: SkinVariant, page: int = 1) -> dict:
        return {
            "skin_variant_id": skin.id,
            "item_name": skin.name,
            "cleaned_name": self.clean_item_name(skin.name),
            "wear": skin.wear.name if skin.wear else None,
            "stattrak": skin.stattrak,
            "souvenir": skin.souvenir,
            "page": page,
            "has_fetched_sales": False,
        }

    def build_listing_request_url(self, meta: dict) -> str:
        # Build the URL using cleaned_name, wear, stattrak, souvenir, and page from meta dict
        url = (
            f"{self.base_url}/feed?"
            f"query={meta['cleaned_name']}&"
            f"wear={meta['wear']}&"
            f"stattrak={meta['stattrak']}&"
            f"souvenir={meta['souvenir']}&"
            f"page={meta['page']}"
        )
        return url

    def get_listing_request(self, meta: dict):
        return scrapy.Request(
            url=self.build_listing_request_url(meta),
            callback=self.parse,
            headers=self.headers,
            meta=meta
        )

    def start_requests(self):
        database = DatabaseManager()
        session = database.get_session()

        repository = CS2ItemsRepository(db=session)
        skins = repository.get_all_skin_variants_with_opts(wears=True, skin=True)

        for skin_variant in skins:
            meta = self.build_meta(skin_variant)
            yield self.get_listing_request(meta)

    def parse(self, response):
        meta = response.meta
        skin_variant_id = meta.get("skin_variant_id")
        item_name = meta.get("item_name", "Unknown Item")
        page = meta.get("page", 1)

        data = response.json()

        if not data or not data.get('items'):
            self.logger.warning(f"No sales data found for skin variant {skin_variant_id} on page {page}")
            return

        for sale in data['items']:
            yield {
                "skin_variant_id": skin_variant_id,
                "item_name": item_name,
                "request_data": sale,
                "type": "list"
            }

        # Fetch sales data for first item if not already fetched
        if not meta.get("has_fetched_sales"):
            first_item_id = data['items'][0].get('id')
            if first_item_id:
                meta["has_fetched_sales"] = True
                yield self.sales_request(item_id=first_item_id, skin_variant_id=skin_variant_id, item_name=item_name)
            else:
                self.logger.warning(f"No item ID found for skin variant {skin_variant_id}")

        # Pagination: if there's more data, yield request for next page
        if data.get('hasMore'):
            next_page_meta = meta.copy()
            next_page_meta['page'] = page + 1
            yield self.get_listing_request(next_page_meta)

    def sales_request(self, item_id: str, skin_variant_id: str = None, item_name: str = None):
        return scrapy.Request(
            url=f"{self.base_url}/items/lastsold?itemId={item_id}",
            headers=self.headers,
            callback=self.parse_sales,
            meta= {
                "skin_variant_id": skin_variant_id if skin_variant_id else "unknown",
                "item_name": item_name if item_name else "unknown"
            }
        )

    def parse_sales(self, response):
        meta = response.meta
        skin_variant_id = meta.get("skin_variant_id")
        item_name = meta.get("item_name")

        data = response.json()
        if not data:
            self.logger.warning(f"No sales data found for variant {skin_variant_id}")
            return

        for sale in data:
            yield {
                "skin_variant_id": skin_variant_id,
                "item_name": item_name,
                "request_data": sale,
                "type": "sales"
            }



import time
import scrapy
from ..models.CS2_items import SkinVariant
from ..repositories.CS2_items_repository import CS2ItemsRepository
from ..database.database import DatabaseManager


class CSGOEmpireSpider(scrapy.Spider):
    name = "csgoempire"
    allowed_domains = ["csgoempire.com"]
    start_urls = ["https://csgoempire.com/"]
    base_url = "https://csgoempire.com/api/v2"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Authorization': '' # field is required to bypass geo-blocking, even if empty
    }

    def build_meta(self, skin: SkinVariant, page: int = 1) -> dict:
        if skin.souvenir:
            raise ValueError("CSGOEmpire does not support souvenir skins.")
        return {
            "skin_variant_id": skin.id,
            "item_name": skin.name,
            "wear": skin.wear.name if skin.wear else None,
            "statTrak": skin.stattrak,
            "page": page,
        }
    
    def build_listing_request_url(self, meta: dict) -> str:
        """Build the URL for fetching listings based on the meta data."""
        stattrak: str = "yes" if meta.get("statTrak") == True else "no"
        url = (
            f"{self.base_url}/trading/items?"
            f"per_page=200&"
            f"page={meta['page']}&"
            f"wear_names[]={meta['wear']}&"
            f"stattrak={stattrak}&"
            f"search={meta['item_name']}&"
            f"sort=asc&"
            f"order=market_value"
        )
        return url

    def get_listing_request(self, meta: dict):
        """Create a Scrapy request for fetching listings."""
        return scrapy.Request(
            url=self.build_listing_request_url(meta),
            headers=self.headers,
            callback=self.parse,
            meta=meta
        )

    def start_requests(self):
        """Generate requests dynamically for listings and sales."""
        # Initialize database connection
        database = DatabaseManager()
        session = database.get_session()

        repository = CS2ItemsRepository(db=session)
        skin_variants = repository.get_all_skin_variants_with_opts(wears=True)

        for skin_variant in skin_variants:
            try:
                meta = self.build_meta(skin_variant)
                yield self.get_listing_request(meta)
            except Exception as e:
                if e is ValueError and str(e) == "CSGOEmpire does not support souvenir skins.":
                    self.logger.info(f"Skipping souvenir skin: {skin_variant.name}")
                    continue
                self.logger.error(f"Error building request for {skin_variant.name}: {e}")

    def parse(self, response):
        # Implement the parsing logic here
        meta = response.meta
        skin_variant_id = meta.get("skin_variant_id")
        item_name = meta.get("item_name", "Unknown Item")
        page = meta.get("page", 1)

        data = response.json()

        if not data or not data.get('data'):
            self.logger.warning(f"No listings found for skin variant {skin_variant_id} on page {page}")
            return

        for item in data['data']:
            price = item.get('market_value')
            if price is None:
                self.logger.warning(f"Missing price for item {item_name} on page {page}")
                continue

            item['market_value'] = round(price / 1.628, 2) # Convert from empire coins to dollars
            yield {
                "skin_variant_id": skin_variant_id,
                "item_name": item_name,
                "request_data": item,
                "type": "list",
            }

        if data.get('next_page_url'):
            next_page_meta = meta.copy()
            next_page_meta['page'] += 1
            yield self.get_listing_request(next_page_meta)
    
    def parse_item(self, item):
        # Implement item parsing logic here
        pass

    def handle_error(self, failure):
        # Handle errors during scraping
        self.logger.error(f"Error occurred: {failure}")
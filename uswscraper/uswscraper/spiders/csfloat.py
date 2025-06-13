import time
from typing import List
import scrapy

from ..models.CS2_items import SkinVariant
from ..repositories.CS2_items_repository import CS2ItemsRepository
from ..database.database import DatabaseManager


class CSFloatSpider(scrapy.Spider):
    name = "csfloat"
    allowed_domains = ["csfloat.com"]

    def start_requests(self):
        """Generate requests dynamically"""
        base_url = "https://csfloat.com/api/v1/history/"

        # Initialize database connection
        database = DatabaseManager()
        session = database.get_session()  # Assuming this method exists

        # Get skin variants from database
        repository = CS2ItemsRepository(db=session)
        skin_variants = repository.get_all_skin_variants()

        # Generate URLs for each skin variant
        for skin_variant in skin_variants:
            market_hash_name = getattr(skin_variant, "market_hash_name", None)
            if market_hash_name:
                url = f"{base_url}{market_hash_name}/sales"
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={"skin_variant_id": getattr(skin_variant, "id", "unknown"), "item_name": market_hash_name},
                )

    def parse(self, response):
        skin_variant_id = response.meta.get("skin_variant_id")
        item_name = response.meta.get("item_name", "Unknown Item")
        data: List = response.json()

        if not data:
            self.logger.warning(f"No sales data found for skin variant {skin_variant_id}")
            return

        for sale in data:
            yield {
                "skin_variant_id": skin_variant_id,
                "item_name": item_name,
                "request_data": sale,
            }
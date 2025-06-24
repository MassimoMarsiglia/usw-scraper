import scrapy
import requests
import json
from dotenv import load_dotenv
from ..database.database import DatabaseManager
from ..models.Buff163 import Buff163_Listing
from ..models.CS2_items import SkinVariant

class ScrapeBuff163Spider(scrapy.Spider):
    name = "scrape_buff163"
    allowed_domains = ["buff.163.com"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        load_dotenv()
        self.db = DatabaseManager()
        self.db.connect()
        self.session = self.db.get_session()
        self.total_inserted = 0

    def closed(self, reason):
        self.session.close()
        self.logger.info(f"Total inserted listings: {self.total_inserted}")

    def start_requests(self):
        id_name_map = self.get_goods_ids()

        for goods_id, market_hash_name in id_name_map.items():
            url = f"https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id={goods_id}&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1749772147804"
            yield scrapy.Request(
                url=url,
                callback=self.parse_listing,
                meta={"goods_id": goods_id,
                      "market_hash_name": market_hash_name}
            )

    def get_goods_ids(self):
        url = "https://raw.githubusercontent.com/ModestSerhat/cs2-marketplace-ids/refs/heads/main/cs2_marketplaceids.json"  
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            id_name_map = {
                str(info["buff163_goods_id"]): name
                for name, info in data["items"].items()
                if "buff163_goods_id" in info
            }
            self.logger.info(f"Extracted goods_ids: {list(id_name_map.keys())}")
            return id_name_map
        except Exception as e:
            self.logger.error(f"Failed to get goods_ids: {e}")
            return []

    def parse_listing(self, response):
        goods_id = response.meta["goods_id"]
        market_hash_name = response.meta["market_hash_name"]

        try:
            data = json.loads(response.text)
        except Exception as e:
            self.logger.error(f"Failed to parse JSON for goods_id {goods_id}: {e}")
            return

        if data.get("code") != "OK":
            self.logger.warning(f"Invalid response for goods_id {goods_id}")
            return

        items = data.get("data", {}).get("items", [])
        for item in items:
            if "id" not in item or "asset_info" not in item:
                continue

            # Lookup the corresponding skin_variant_id in the DB
            skin_variant = self.session.query(SkinVariant).filter_by(
                market_hash_name=market_hash_name
            ).first()

            if not skin_variant:
                self.logger.warning(f"No skin_variant found for item_name: {market_hash_name}")
                continue

            skin_variant_id = skin_variant.id
            # item_name = item.get("description") or item["asset_info"].get("description") or f"Item {skin_variant_id}"
            request_data = json.loads(json.dumps(item))  # Ensure serializable

            listing = Buff163_Listing(
                skin_variant_id=skin_variant_id,
                item_name=market_hash_name,
                request_data=request_data
            )

            try:
                self.session.add(listing)
                self.session.commit()
                self.total_inserted += 1
                self.logger.info(f"Saved listing: {market_hash_name} (skin_variant_id={skin_variant_id})")
            except Exception as db_error:
                self.logger.error(f"DB error on goods_id {goods_id}: {db_error}")
                self.session.rollback()

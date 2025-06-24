# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import date
import json
from itemadapter import ItemAdapter

from .models.CSGOEmpire import CSGOEmpire_Listing, CSGOEmpire_Sale

from .models.Gamerpay import GamerPay_Listing, GamerPay_Sale

from .database.database import DatabaseManager
from .models.CsFloat import CSFloat_Sale

def persist_item(item, session, spider):
    """
    Helper function to persist an item to the database.
    """
    try:
        session.add(item)
        session.commit()
        spider.logger.info(f"Saved item: {item}")
    except Exception as e:
        session.rollback()
        spider.logger.error(f"Error saving item: {e}")


class CSFloatPipeline:
    def __init__(self):
        self.db = DatabaseManager()
        self.session = None

    def open_spider(self, spider):
        self.session = self.db.get_session()

    def close_spider(self, spider):
        if self.session:
            self.session.close()

    def process_item(self, item, spider):
        if spider.name == "csfloat":
            # Create a new CSFloat_Sale object
            request_data = item["request_data"]
            if isinstance(request_data, str):
                request_data = json.loads(request_data)

            sale = CSFloat_Sale(
                skin_variant_id=item["skin_variant_id"],
                item_name=item["item_name"],
                request_data=item["request_data"],
            )
            
            # Add to session and commit
            persist_item(sale, self.session, spider)
        
        return item

class CSGOEmpirePipeline:
    def __init__(self):
        self.db = DatabaseManager()
        self.session = None

    def open_spider(self, spider):
        self.session = self.db.get_session()

    def close_spider(self, spider):
        if self.session:
            self.session.close()

    def process_item(self, item, spider):
        if spider.name == "csgoempire":
            # Create a new CSGOEmpire_Listing object
            request_data = item["request_data"]
            if isinstance(request_data, str):
                request_data = json.loads(request_data)

            data = None
            if item["type"] == "list":
                data = CSGOEmpire_Listing(
                    skin_variant_id=item["skin_variant_id"],
                    item_name=item["item_name"],
                    request_data=item["request_data"],
                )
            elif item["type"] == "sales":
                data = CSGOEmpire_Sale(
                    skin_variant_id=item["skin_variant_id"],
                    item_name=item["item_name"],
                    request_data=item["request_data"],
                )
            
            persist_item(data, self.session, spider)

        return item

class GamerPayPipeline:
    def __init__(self):
        self.db = DatabaseManager()
        self.session = None

    def open_spider(self, spider):
        self.session = self.db.get_session()

    def close_spider(self, spider):
        if self.session:
            self.session.close()

    def process_item(self, item, spider):
        if spider.name == "gamerpay":
            # Create a new GamerPay_Listing object
            request_data = item["request_data"]
            if isinstance(request_data, str):
                request_data = json.loads(request_data)

            data = None
            if item["type"] == "list":
                data = GamerPay_Listing(
                    skin_variant_id=item["skin_variant_id"],
                    item_name=item["item_name"],
                    request_data=item["request_data"],
                )
            elif item["type"] == "sales":
                data = GamerPay_Sale(
                    skin_variant_id=item["skin_variant_id"],
                    item_name=item["item_name"],
                    request_data=item["request_data"],
                )
            
            # Add to session and commit
            persist_item(data, self.session, spider)

        return item
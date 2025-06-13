# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from .database.database import DatabaseManager
from .models.CsFloat import CSFloat_Sale


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
            sale = CSFloat_Sale(
                skin_variant_id=item["skin_variant_id"],
                item_name=item["item_name"],
                request_data=item["request_data"]
            )
            
            # Add to session and commit
            try:
                self.session.add(sale)
                self.session.commit()
                spider.logger.info(f"Saved sale record for {item['item_name']}")
            except Exception as e:
                self.session.rollback()
                spider.logger.error(f"Error saving sale: {e}")
        
        return item
from sqlalchemy import (
    JSON,
    Column,
    Date,
    Integer,
    String,
)
from ..database.database import get_base

Base = get_base()
class Buff163_Listing(Base):
    __tablename__ = 'buff163_listings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    skin_variant_id = Column(String, nullable=False)
    item_name = Column(String, nullable=False)
    request_data = Column(JSON, nullable=False)
    
    def __repr__(self):
        return f"<Buff163_Listing(id={self.id}, item_name='{self.item_name}', item_price={self.item_price})>"
    
class Buff163_BuyOrder(Base):
    __tablename__ = 'buff163_buy_orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    skin_variant_id = Column(String, nullable=False)
    item_name = Column(String, nullable=False)
    request_data = Column(JSON, nullable=False)
    
    def __repr__(self):
        return f"<Buff163_BuyOrder(id={self.id}, item_name='{self.item_name}')>"
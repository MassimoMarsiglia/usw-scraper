from sqlalchemy import (
    JSON,
    DateTime,
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Enum,
    ForeignKey,
    Table,
    Text,
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker


Base = declarative_base()

class Buff163_Listing(Base):
    __tablename__ = 'buff163_listings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    skin_variant_id = Column(String, nullable=False)
    item_name = Column(String, nullable=False)
    request_data = Column(JSON, nullable=False)
    
    def __repr__(self):
        return f"<Buff163_Listing(id={self.id}, item_name='{self.item_name}', item_price={self.item_price})>"
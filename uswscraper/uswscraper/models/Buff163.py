from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
)
from ..database.database import Base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship


class Buff163_Listing(Base):
    __tablename__ = 'buff163_listings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    skin_variant_id = Column(String, ForeignKey('skin_variants.id'), nullable=False)
    item_name = Column(String, nullable=False)
    request_data = Column(JSONB, nullable=False)

    relationship(
        "SkinVariant",
        back_populates="buff163_buy_orders",
        foreign_keys=[skin_variant_id],
    )

    def __repr__(self):
        return f"<Buff163_Listing(id={self.id}, item_name='{self.item_name}')>"

class Buff163_BuyOrder(Base):
    __tablename__ = 'buff163_buy_orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    skin_variant_id = Column(String, ForeignKey('skin_variants.id'), nullable=False)
    item_name = Column(String, nullable=False)
    request_data = Column(JSONB, nullable=False)

    relationship(
        "SkinVariant",
        back_populates="buff163_buy_orders",
        foreign_keys=[skin_variant_id],
    )

    def __repr__(self):
        return f"<Buff163_BuyOrder(id={self.id}, item_name='{self.item_name}')>"
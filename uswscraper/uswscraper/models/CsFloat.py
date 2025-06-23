from sqlalchemy import (
    JSON,
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..database.database import Base

class CSFloat_Sale(Base):
    __tablename__ = 'csfloat_sales'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    skin_variant_id = Column(String, ForeignKey('skin_variants.id'), nullable=False)
    item_name = Column(String, nullable=False)
    request_data = Column(JSONB, nullable=False)
    date = Column(Integer)

    relationship(
        "SkinVariant",
        back_populates="csfloat_sales",
        foreign_keys=[skin_variant_id],
    )
    
    def __repr__(self):
        return f"<CSFloat_Sale(id={self.id}, item_name='{self.item_name}', sale_price={self.sale_price})>"
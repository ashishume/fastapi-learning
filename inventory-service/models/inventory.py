from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from database import Base


class CreateInventory(Base):

    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    product_name = Column(Text, nullable=False)
    category = Column(String(500), nullable=False)
    quantity_in_stock = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    last_restock_date = Column(DateTime, nullable=False)
    supplier = Column(Text, nullable=False)
    reorder_point = Column(Integer, nullable=False)

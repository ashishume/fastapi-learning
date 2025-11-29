import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from database import Base
import uuid

class FoodOrder(Base):
    __tablename__ = "food_orders"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("order.id"), nullable=False)
    menu_id = Column(UUID(as_uuid=True), ForeignKey("menu.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    # total_price = Column(Float, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


    # Relationships
    order = relationship("Order", back_populates="food_orders")
    menus = relationship("Menu", back_populates="food_orders")
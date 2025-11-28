import datetime
import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, UUID, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class Menu(Base):
    __tablename__ = "menu"
    __table_args__ = (
        UniqueConstraint('restaurant_id', 'food_id', name='uq_restaurant_food'),
    )
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurant.id"), nullable=False)
    food_id = Column(UUID(as_uuid=True), ForeignKey("food.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("category.id"), nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


    # Relationships
    restaurant = relationship("Restaurant", back_populates="menus")
    food = relationship("Food", back_populates="menus")
    category = relationship("Category", back_populates="menus")
    food_orders = relationship("FoodOrder", back_populates="menu")
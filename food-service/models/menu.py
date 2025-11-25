import datetime
import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class Menu(Base):
    __tablename__ = "menu"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    restaurant_id = Column(uuid.UUID(as_uuid=True), ForeignKey("restaurant.id"), nullable=False)
    food_id = Column(uuid.UUID(as_uuid=True), ForeignKey("food.id"), nullable=False)
    category_id = Column(uuid.UUID(as_uuid=True), ForeignKey("category.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


    # Relationships
    restaurant = relationship("Restaurant", back_populates="menus")
    food = relationship("Food", back_populates="menus")
    category = relationship("Category", back_populates="menus")
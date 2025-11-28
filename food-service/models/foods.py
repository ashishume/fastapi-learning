import datetime
from sqlalchemy import Boolean, Column, String, Float, DateTime, ForeignKey, Text, UUID
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Food(Base):
    __tablename__ = "food"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(100), index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(Text, nullable=True)
    is_vegetarian = Column(Boolean, nullable=False, default=False)   
    
    category_id = Column(UUID(as_uuid=True), ForeignKey("category.id"), nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


    # Relationships
    menus = relationship("Menu", back_populates="food", cascade="all, delete-orphan")
    category = relationship("Category", back_populates="foods")
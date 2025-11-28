import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, UUID
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Restaurant(Base):
    __tablename__ = "restaurant"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(100), index=True, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    address = Column(Text, nullable=False)
    restaurant_type = Column(String(100), nullable=False) # e.g., Fast Food, Fine Dining
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


    # Relationships
    menus = relationship("Menu", back_populates="restaurant", cascade="all, delete-orphan")

    
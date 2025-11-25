import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Category(Base):
    __tablename__ = "category"
    id = Column(uuid.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(100), index=True, nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String(100), index=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


    # Relationships
    menus = relationship("Menu", back_populates="category", cascade="all, delete-orphan")
    foods = relationship("Food", back_populates="category", cascade="all, delete-orphan")
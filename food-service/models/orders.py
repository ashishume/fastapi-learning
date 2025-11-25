import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Order(Base):
    __tablename__ = "order"
    id = Column(uuid.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(uuid.UUID(as_uuid=True), nullable=False)
    order_number = Column(String(100), index=True, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String(100), nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


    # Relationships
    food_orders = relationship("FoodOrder", back_populates="order", cascade="all, delete-orphan")
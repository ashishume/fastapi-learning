from datetime import date
import datetime
from sqlalchemy import UUID, Column, Date, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
import uuid


class Theater(Base):

    __tablename__ = "theaters"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(Text, nullable=False)
    address = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow,onupdate=datetime.datetime.utcnow)

    # Relationships
    seats = relationship("Seat", back_populates="theater",cascade="all, delete-orphan")
    showings = relationship("Showing", back_populates="theater",cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="theater",cascade="all, delete-orphan")
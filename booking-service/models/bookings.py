from datetime import date
import datetime
from enum import Enum
from sqlalchemy import (
    UUID,
    Column,
    Date,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from database import Base
import uuid
from sqlalchemy.orm import relationship


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    REFUNDED = "refunded"


class Booking(Base):

    __tablename__ = "bookings"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
   
    showing_id = Column(UUID(as_uuid=True), ForeignKey("showings.id"), nullable=False)

    user_id = Column(UUID(as_uuid=True), nullable=False)
    
    booking_number = Column(String(255), nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(
        SQLEnum(BookingStatus), nullable=False, default=BookingStatus.PENDING
    )
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.utcnow , onupdate=datetime.datetime.utcnow
    )

    # Relationships
    # movie = relationship("Movie", back_populates="bookings")
    # theater = relationship("Theater", back_populates="bookings")
    showing = relationship("Showing", back_populates="bookings")
    booking_seats = relationship("BookingSeat", back_populates="booking", cascade="all, delete-orphan")

    # Production-ready indexes
    __table_args__ = (
        Index("ix_bookings_user_id", "user_id"),  # Frequently queried by user
        Index("ix_bookings_showing_id", "showing_id"),  # Foreign key for joins
        Index("ix_bookings_status", "status"),  # Filtered by booking status
        Index("ix_bookings_booking_number", "booking_number"),  # Unique lookups by booking number
        Index("ix_bookings_created_at", "created_at"),  # Sorting and date range queries
        Index("ix_bookings_user_status", "user_id", "status"),  # Composite: filter user bookings by status
        Index("ix_bookings_showing_status", "showing_id", "status"),  # Composite: filter showings by status
    )

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
    movie_id = Column(UUID(as_uuid=True), ForeignKey("movies.id"), nullable=False)

    theater_id = Column(UUID(as_uuid=True), ForeignKey("theaters.id"), nullable=False)

    showing_id = Column(UUID(as_uuid=True), ForeignKey("showings.id"), nullable=False)

    seats_id = Column(UUID(as_uuid=True), ForeignKey("seats.id"), nullable=False)

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
    movie = relationship("Movie", back_populates="bookings")
    theater = relationship("Theater", back_populates="bookings")
    showing = relationship("Showing", back_populates="bookings")
    seats = relationship("Seat", back_populates="bookings")

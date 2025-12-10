from sqlalchemy import UUID, Column, ForeignKey, Index, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from database import Base
import uuid
import datetime

class BookingSeat(Base):
    __tablename__ = "booking_seats"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)
    showing_id = Column(UUID(as_uuid=True), ForeignKey("showings.id"), nullable=False)
    seat_id = Column(UUID(as_uuid=True), ForeignKey("seats.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow,onupdate=datetime.datetime.utcnow)

    # Relationships
    booking = relationship("Booking", back_populates="booking_seats")
    seat = relationship("Seat", back_populates="booking_seats")
    showing = relationship("Showing", back_populates="booking_seats")

    # Production-ready indexes and constraints
    __table_args__ = (
        Index("ix_booking_seats_booking_id", "booking_id"),  # Foreign key for joins
        Index("ix_booking_seats_showing_id", "showing_id"),  # Critical: frequently queried
        Index("ix_booking_seats_seat_id", "seat_id"),  # Foreign key for joins
        Index("ix_booking_seats_showing_seat", "showing_id", "seat_id"),  # Composite: check if seats are booked
        Index("ix_booking_seats_booking_showing", "booking_id", "showing_id"),  # Composite: booking lookups
        UniqueConstraint("showing_id", "seat_id", name="uq_booking_seats_showing_seat"),  # Prevent double booking
    )
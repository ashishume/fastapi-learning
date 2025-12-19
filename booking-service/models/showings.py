from datetime import date
import datetime
from sqlalchemy import UUID, Boolean, Column, Date, DateTime, ForeignKey, Index, Integer, Text
from database import Base
import uuid
from sqlalchemy.orm import relationship


class Showing(Base):

    __tablename__ = "showings"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    movie_id = Column(UUID(as_uuid=True), ForeignKey("movies.id"), nullable=False)
    theater_id = Column(UUID(as_uuid=True), ForeignKey("theaters.id"), nullable=False)
    show_start_datetime = Column(Text, nullable=False)
    show_end_datetime = Column(Text, nullable=False)
    available_seats = Column(Integer, nullable=False,default=0)
    is_active = Column(Boolean, nullable=False,default=True)
    expires_at= Column(DateTime, nullable=True)


    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow,onupdate=datetime.datetime.utcnow)

    # Relationships
    theater = relationship("Theater", back_populates="showings")
    movie = relationship("Movie", back_populates="showings")
    bookings = relationship("Booking", back_populates="showing",cascade="all, delete-orphan")
    booking_seats = relationship("BookingSeat", back_populates="showing",cascade="all, delete-orphan")
    # seats = relationship("Seat", back_populates="showing", primaryjoin="Showing.id == Seat.showing_id", cascade="all, delete-orphan")
    # Production-ready indexes
    __table_args__ = (
        Index("ix_showings_movie_id", "movie_id"),  # Foreign key, frequently queried
        Index("ix_showings_theater_id", "theater_id"),  # Foreign key, frequently queried
        Index("ix_showings_expires_at", "expires_at"),  # Critical: WHERE expires_at > now()
        Index("ix_showings_is_active", "is_active"),  # Filtered by active status
        Index("ix_showings_theater_movie", "theater_id", "movie_id"),  # Composite: frequently queried together
        Index("ix_showings_movie_theater_datetime", "movie_id", "theater_id", "show_start_datetime"),  # Composite: duplicate checking
        Index("ix_showings_expires_active", "expires_at", "is_active"),  # Composite: active showings queries
    )

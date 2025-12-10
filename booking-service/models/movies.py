from datetime import date, datetime
import datetime
from sqlalchemy import (
    ARRAY,
    UUID,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from database import Base
import uuid


class Movie(Base):

    __tablename__ = "movies"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    genre = Column(String(100), nullable=True)
    director = Column(String(255), nullable=True)
    release_date = Column(Date, nullable=True)
    rating = Column(Float, nullable=True)
    language = Column(String(50), nullable=True)
    is_imax = Column(Boolean, nullable=True, default=False)
    poster_url = Column(String(255), nullable=True)
    trailer_url = Column(String(255), nullable=True)
    cast = Column(ARRAY(Text), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relationships
    showings = relationship(
        "Showing", back_populates="movie", cascade="all, delete-orphan"
    )
    # bookings = relationship("Booking", back_populates="movie",cascade="all, delete-orphan")

    # Production-ready indexes
    __table_args__ = (
        Index("ix_movies_title", "title"),  # Search and filtering by title
        Index("ix_movies_genre", "genre"),  # Filtered by genre
        Index("ix_movies_release_date", "release_date"),  # Sorting and filtering by release date
        Index("ix_movies_rating", "rating"),  # Sorting and filtering by rating
        Index("ix_movies_language", "language"),  # Filtered by language
    )

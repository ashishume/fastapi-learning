import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from models.seats import SeatType

class TheaterBrief(BaseModel):
    """Simplified theater info for seat responses"""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    location: str
    city: str

class MovieBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    duration_minutes: int
    genre: Optional[str] = None
    rating: Optional[float] = None
    poster_url: Optional[str] = None

class ShowingBrief(BaseModel):
    """Simplified showing info for seat responses"""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    movie_id: UUID
    theater_id: UUID
    show_start_datetime: datetime.datetime
    show_end_datetime: datetime.datetime
    theater: Optional[TheaterBrief] = None
    movie: Optional[MovieBrief] = None

class SeatCreate(BaseModel):
    # theater_id: UUID
    showing_id: UUID
    seat_number: str
    row: str
    column: str
    seat_type: SeatType

class SeatCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    # theater_id: UUID
    showing_id: UUID
    seat_number: str
    row: str
    column: str
    seat_type: SeatType
    created_at: datetime.datetime
    updated_at: datetime.datetime


class SeatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    # theater_id: UUID
    showing_id: UUID
    seat_number: str
    row: str
    column: str
    seat_type: SeatType
    created_at: datetime.datetime
    updated_at: datetime.datetime
    theater: Optional[TheaterBrief] = None
    showing: Optional[ShowingBrief] = None
import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ShowingCreate(BaseModel):
    movie_id: UUID
    theater_id: UUID
    show_start_datetime: datetime.datetime
    show_end_datetime: datetime.datetime
    available_seats: int
    is_active: bool
    expires_at: datetime.datetime


# Simplified schemas for nested data
class MovieBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    duration_minutes: int
    genre: Optional[str] = None
    rating: Optional[float] = None
    poster_url: Optional[str] = None


class TheaterBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    location: str
    city: str


class ShowingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    movie_id: UUID
    theater_id: UUID
    show_start_datetime: datetime.datetime
    show_end_datetime: datetime.datetime
    available_seats: int
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    movie: Optional[MovieBrief] = None
    theater: Optional[TheaterBrief] = None


class ShowingBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    movie: Optional[MovieBrief] = None
    theater: Optional[TheaterBrief] = None
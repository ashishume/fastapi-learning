import datetime
from typing import List, Optional, Text
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy import ARRAY


class MovieCreate(BaseModel):
    title: str
    description: str
    duration_minutes: int
    genre: str
    director: str
    release_date: datetime.date
    rating: float
    language: str
    is_imax: bool
    poster_url: str
    trailer_url: str
    cast: List[str]

class MovieResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    # id: Optional[str] = None
    id: UUID
    title: str
    description: str
    duration_minutes: int
    genre: str
    director: str
    release_date: datetime.date
    rating: float
    language: str
    is_imax: bool
    poster_url: str
    trailer_url: str
    cast: List[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime


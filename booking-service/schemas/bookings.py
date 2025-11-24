import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from models.bookings import BookingStatus
from schemas.seats import  ShowingBrief
from typing import List, Optional
from schemas.booking_seats import BookingSeatBrief

class BookingCreate(BaseModel):
    # movie_id: UUID
    # theater_id: UUID
    showing_id: UUID
    seats_ids: List[UUID]
    total_price: float



class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    # movie_id: UUID
    # theater_id: UUID
    showing_id: UUID
    # seats_ids: List[UUID]
    total_price: float
    booking_number: str
    status: BookingStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime

    # movie: Optional[MovieResponse] = None
    # theater: Optional[TheaterResponse] = None
    showing: Optional[ShowingBrief] = None
    booking_seats: Optional[List[BookingSeatBrief]] = None
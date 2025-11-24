from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID
import datetime
# from schemas.bookings import BookingResponse
from schemas.seats import SeatResponse, SeatBrief

class BookingSeatCreate(BaseModel):
    booking_id: UUID
    seat_id: UUID
    showing_id: UUID

class BookingSeatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    # booking_id: UUID
    seat_id: UUID
    showing_id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    # booking: Optional[BookingResponse] = None
    seat: Optional[SeatResponse] = None

class BookingSeatBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    # booking_id: UUID
    showing_id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    # seat: Optional[SeatBrief] = None
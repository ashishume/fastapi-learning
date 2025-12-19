from pydantic import BaseModel, ConfigDict
from uuid import UUID
# import datetime

class BookingLockCreate(BaseModel):
    seat_id: UUID
    showing_id: UUID
    lock_seat: bool = True

class BookingLockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # id: UUID
    seat_id: UUID
    showing_id: UUID
    # created_at: datetime.datetime
    # updated_at: datetime.datetime
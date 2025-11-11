import datetime
from uuid import UUID
from pydantic import BaseModel


class TheaterCreate(BaseModel):
    name: str
    location: str
    description: str
    address: str
    city: str


class TheaterResponse(BaseModel):
    id: UUID
    name: str
    location: str
    description: str
    address: str
    city: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
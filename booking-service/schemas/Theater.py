import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class TheaterCreate(BaseModel):
    name: str
    location: str
    description: str
    address: str
    city: str


class TheaterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    location: str
    description: str
    address: str
    city: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
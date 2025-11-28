from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import UUID

class RestaurantSchema(BaseModel):
    id: UUID
    name: str
    image_url: str
    description: str
    restaurant_type: str
    address: str
    created_at: datetime
    updated_at: datetime


class RestaurantResponse(BaseModel):    
    id: UUID
    name: str
    description: str
    address: str
    restaurant_type: str
    image_url: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RestaurantCreate(BaseModel):
    name: str
    description: str
    address: str
    restaurant_type: str
    image_url: str
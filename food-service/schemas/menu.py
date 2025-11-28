from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import UUID


class MenuSchema(BaseModel):
    id: UUID
    restaurant_id: int
    food_id: int
    category_id: int
    price: float
    created_at: datetime
    updated_at: datetime


class MenuResponse(BaseModel):
    id: UUID
    restaurant_id: int
    food_id: int
    category_id: int
    price: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MenuCreate(BaseModel):    
    restaurant_id: int
    food_id: int
    category_id: int
    price: float
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import UUID

class FoodSchema(BaseModel):
    id: UUID
    name: str
    description: str
    price: float
    image_url: str
    is_vegetarian: bool
    category_id: int
    created_at: datetime
    updated_at: datetime



class FoodResponse(BaseModel):
    id: UUID
    name: str
    description: str
    price: float
    image_url: str
    is_vegetarian: bool
    category_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FoodCreate(BaseModel):
    name: str
    description: str
    price: float
    image_url: str
    is_vegetarian: bool
    category_id: int
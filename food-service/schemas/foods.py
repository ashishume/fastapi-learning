from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
class FoodSchema(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    price: float
    image_url: str
    is_vegetarian: bool
    category_id: uuid.UUID
    created_at: datetime
    updated_at: datetime



class FoodResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    price: float
    image_url: str
    is_vegetarian: bool
    category_id: uuid.UUID
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
    category_id: uuid.UUID
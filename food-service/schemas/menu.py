from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class MenuSchema(BaseModel):
    id: uuid.UUID
    restaurant_id: uuid.UUID
    food_id: uuid.UUID
    category_id: uuid.UUID
    price: float
    created_at: datetime
    updated_at: datetime


class MenuResponse(BaseModel):
    id: uuid.UUID
    restaurant_id: uuid.UUID
    food_id: uuid.UUID
    category_id: uuid.UUID
    price: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MenuCreate(BaseModel):    
    restaurant_id: uuid.UUID
    food_id: uuid.UUID
    category_id: uuid.UUID
    price: float
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import UUID



class FoodOrderSchema(BaseModel):
    id: UUID
    order_id: UUID
    menu_id: UUID
    quantity: int
    total_price: float
    created_at: datetime
    updated_at: datetime


class FoodOrderResponse(BaseModel):
    id: UUID
    order_id: UUID
    menu_id: UUID
    quantity: int
    total_price: float  
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FoodOrderCreate(BaseModel):
    order_id: UUID
    menu_id: UUID
    quantity: int
    total_price: float
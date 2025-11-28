from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import UUID


class OrderSchema(BaseModel):
    id: UUID
    user_id: UUID
    order_number: str
    total_price: float
    status: str
    created_at: datetime
    updated_at: datetime


class OrderResponse(BaseModel):
    id: UUID
    order_number: str
    total_price: float
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    user_id: UUID
    order_number: str
    total_price: float
    status: str
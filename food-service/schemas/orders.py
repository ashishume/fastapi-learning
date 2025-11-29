from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
from models.orders import OrderStatus
class OrderSchema(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    order_number: str
    total_price: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime


class OrderResponse(BaseModel):
    id: uuid.UUID
    order_number: str
    total_price: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    user_id: uuid.UUID
    order_number: str
    total_price: float
    status: OrderStatus
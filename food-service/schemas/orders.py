from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from schemas.food_orders import FoodOrderResponse
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

    food_orders: List[FoodOrderResponse]

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    menu_ids: List[uuid.UUID]
    quantity: int


class OrderAddFoodResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    menu_id: uuid.UUID
    quantity: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
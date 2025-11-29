from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
from schemas.menu import MenuResponse


class FoodOrderSchema(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    menu_id: uuid.UUID
    quantity: int
    # total_price: float
    created_at: datetime
    updated_at: datetime


class FoodOrderResponse(BaseModel):
    id: uuid.UUID
    # order_id: uuid.UUID
    menu_id: uuid.UUID
    quantity: int
    # total_price: float  
    created_at: datetime
    updated_at: datetime
 
     # FETCH MENU items from the menu table
    # menu: MenuResponse
    # order: OrderResponse

    class Config:
        from_attributes = True

class FoodOrderCreate(BaseModel):
    order_id: uuid.UUID
    menu_id: uuid.UUID
    quantity: int
    # total_price: float
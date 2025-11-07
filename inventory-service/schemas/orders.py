from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel

class OrderCreate(BaseModel):
    product_id: int
    quantity: int
    total_price: float
    status: str
    created_at: datetime
    updated_at: datetime

class OrderResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    product_id: int
    quantity: int
    total_price: float
    status: str
    created_at: datetime
    updated_at: datetime

class OrderDetailResponse(BaseModel):
    model_config = {"from_attributes": True}
    order: OrderResponse
    product: Optional[Any] = None
    user: Optional[Any] = None
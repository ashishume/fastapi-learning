from datetime import datetime
from pydantic import BaseModel


class InventoryResponse(BaseModel):
    id: int
    product_name: str
    category: str
    quantity_in_stock: int
    unit_price: float
    last_restock_date: datetime
    supplier: str
    reorder_point: int

    class Config:
        from_attributes = True


class InventoryPayload(BaseModel):
    product_name: str
    category: int
    quantity_in_stock: int
    unit_price: float
    last_restock_date: datetime
    supplier: str
    reorder_point: int

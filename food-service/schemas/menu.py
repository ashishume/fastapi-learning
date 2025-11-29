from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from schemas.categories import CategoryResponse
from schemas.foods import FoodResponse
from schemas.restaurants import RestaurantResponse

class MenuSchema(BaseModel):
    id: uuid.UUID
    restaurant_id: uuid.UUID
    food_id: uuid.UUID
    category_id: uuid.UUID
    price: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True




class MenuResponse(BaseModel):
    id: uuid.UUID
    # restaurant_id: uuid.UUID
    # food_id: uuid.UUID
    # category_id: uuid.UUID
    price: float
    created_at: datetime
    updated_at: datetime

    # category: CategoryResponse
    food: FoodResponse
    restaurant: RestaurantResponse

    class Config:
        from_attributes = True


class MenuFoodCreateResponse(BaseModel):
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
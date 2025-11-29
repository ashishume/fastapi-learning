from sqlalchemy import select
from sqlalchemy.orm import Session
from schemas.restaurants import RestaurantCreate
from models.restaurants import Restaurant
from typing import List
import uuid
class RestaurantRepository:
    def __init__(self,db:Session):
        self.db = db

    def create_restaurant(self,restaurant:RestaurantCreate) -> Restaurant:
        new_restaurant = Restaurant(**restaurant.model_dump())
        self.db.add(new_restaurant)
        self.db.commit()
        self.db.refresh(new_restaurant)
        return new_restaurant

    def get_all_restaurants(self) -> List[Restaurant]:
        return self.db.execute(select(Restaurant)).scalars().all()

    def get_restaurant_by_id(self,restaurant_id:uuid.UUID) -> Restaurant:
        return self.db.execute(select(Restaurant).where(Restaurant.id == restaurant_id)).scalar_one_or_none()
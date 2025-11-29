from repository.restaurants_repo import RestaurantRepository
from schemas.restaurants import RestaurantCreate
from models.restaurants import Restaurant
from typing import List
import uuid
from sqlalchemy.orm import Session
class RestaurantService:
    def __init__(self,db:Session):
        self.restaurant_repository = RestaurantRepository(db)

    def create_restaurant(self,restaurant:RestaurantCreate) -> Restaurant:
        return self.restaurant_repository.create_restaurant(restaurant)

    def get_all_restaurants(self) -> List[Restaurant]:
        return self.restaurant_repository.get_all_restaurants()

    def get_restaurant_by_id(self,restaurant_id:uuid.UUID) -> Restaurant:
        return self.restaurant_repository.get_restaurant_by_id(restaurant_id)

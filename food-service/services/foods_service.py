from repository.foods_repo import FoodsRepository
from schemas.foods import FoodCreate
from models.foods import Food
from typing import List
import uuid
from sqlalchemy.orm import Session
class FoodsService:
    def __init__(self,db:Session):
        self.foods_repository = FoodsRepository(db)

    def create_food(self,food:FoodCreate) -> Food:
        return self.foods_repository.create_food(food)

    def get_all_foods(self) -> List[Food]:
        return self.foods_repository.get_all_foods()

    def get_food_by_id(self,food_id:uuid.UUID) -> Food:
        return self.foods_repository.get_food_by_id(food_id)
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from schemas.foods import FoodCreate, FoodResponse
from models.foods import Food
from typing import List
import uuid
from models.categories import Category
class FoodsRepository:
    def __init__(self,db:Session):
        self.db = db

    def create_food(self,food:FoodCreate) -> Food:
        new_food = Food(**food.model_dump())
        self.db.add(new_food)
        self.db.commit()
        self.db.refresh(new_food)
        return new_food

    def get_all_foods(self) -> List[FoodResponse]:
        return self.db.execute(select(Food)
        .options(joinedload(Food.category)
        .load_only(Category.name,Category.id))
        .order_by(Food.created_at.desc())).scalars().all()

    def get_food_by_id(self,food_id:uuid.UUID) -> FoodResponse:
        return self.db.execute(select(Food).options(joinedload(Food.category).load_only(Category.name,Category.id)).where(Food.id == food_id)).scalar_one_or_none()
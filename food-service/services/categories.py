from repository.categories import CategoryRepository
from schemas.categories import CategoryCreate
from models.categories import Category
from typing import List
from sqlalchemy.orm import Session
class CategoryService:
    def __init__(self,db:Session):
        self.category_repository=CategoryRepository(db)

    def create_category(self,category:CategoryCreate) -> Category:
        return self.category_repository.create_category(category)


    def get_all_categories(self) -> List[Category]:
        return self.category_repository.get_all_categories()
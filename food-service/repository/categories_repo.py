from models.categories import Category
from schemas.categories import CategoryCreate
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
import uuid
class CategoryRepository:
    def __init__(self,db:Session):
        self.db=db

    def create_category(self,category:CategoryCreate) -> Category:
        new_category = Category(name=category.name, slug=category.slug, description=category.description)
        self.db.add(new_category)
        self.db.commit()
        self.db.refresh(new_category)
        return new_category
    def get_all_categories(self) -> List[Category]:
        return self.db.execute(select(Category).order_by(Category.created_at.desc())).scalars().all()

    def get_category_by_id(self,category_id:uuid.UUID) -> Category:
        return self.db.execute(select(Category).filter(Category.id == category_id)).scalar_one_or_none()
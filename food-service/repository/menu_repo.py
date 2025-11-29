from sqlalchemy.orm import Session, joinedload
from schemas.menu import MenuCreate, MenuFoodCreateResponse, MenuResponse
from models.menu import Menu
from typing import List
from sqlalchemy import select
import uuid
from fastapi import HTTPException, status
class MenuRepository:
    def __init__(self,db:Session):
        self.db = db

    def create_menu(self,menu:MenuCreate) -> MenuFoodCreateResponse:

        if_menu_exists = self.db.execute(select(Menu).where(Menu.food_id == menu.food_id, Menu.restaurant_id == menu.restaurant_id, Menu.category_id == menu.category_id)).scalar_one_or_none()
        if if_menu_exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Menu already exists")

        new_menu = Menu(**menu.model_dump())
        self.db.add(new_menu)
        self.db.commit()
        self.db.refresh(new_menu)
        return new_menu
    def get_menu_by_id(self,menu_id:uuid.UUID) -> MenuResponse:
        return self.db.execute(select(Menu).where(Menu.id == menu_id)).scalar_one_or_none()

    def get_all_menus(self) -> List[MenuResponse]:
        return self.db.execute(select(Menu).options(joinedload(Menu.food), joinedload(Menu.restaurant), joinedload(Menu.category))).scalars().all()
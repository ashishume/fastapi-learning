from repository.menu_repo import MenuRepository
from schemas.menu import MenuCreate, MenuFoodCreateResponse, MenuResponse
from typing import List
import uuid
from sqlalchemy.orm import Session
class MenuService:
    def __init__(self,db:Session):
        self.menu_repository = MenuRepository(db)

    def create_menu(self,menu:MenuCreate) -> MenuFoodCreateResponse:
        return self.menu_repository.create_menu(menu)

    def get_menu_by_id(self,menu_id:uuid.UUID) -> MenuResponse:
        return self.menu_repository.get_menu_by_id(menu_id)

    def get_all_menus(self) -> List[MenuResponse]:
        return self.menu_repository.get_all_menus()

    def get_all_menus_by_restaurant_id(self,restaurant_id:uuid.UUID) -> List[MenuResponse]:
        return self.menu_repository.get_all_menus_by_restaurant_id(restaurant_id)
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.menu import MenuCreate, MenuFoodCreateResponse, MenuResponse
from database import get_db
from sqlalchemy.orm import Session
from services.menu_service import MenuService
from models.menu import Menu
from typing import List
import uuid
router=APIRouter()

@router.post("/",status_code=status.HTTP_201_CREATED,summary="Create a new menu",response_model=MenuFoodCreateResponse)
def create_menu(menu: MenuCreate, db: Session = Depends(get_db)) -> MenuFoodCreateResponse:
    try:
        menu_service = MenuService(db)
        new_menu = menu_service.create_menu(menu)
        return MenuFoodCreateResponse.model_validate(new_menu)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error creating menu: {e}")

@router.get("/{menu_id}",status_code=status.HTTP_200_OK,summary="Get a menu by id",response_model=MenuResponse)
def get_menu_by_id(menu_id: uuid.UUID, db: Session = Depends(get_db)) -> MenuResponse:
    try:
        menu_service = MenuService(db)
        menu = menu_service.get_menu_by_id(menu_id)
        return MenuResponse.model_validate(menu)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting menu: {e}")

@router.get("/",status_code=status.HTTP_200_OK,summary="Get all menus",response_model=List[MenuResponse])
def get_all_menus(db: Session = Depends(get_db)) -> List[MenuResponse]:
    try:
        menu_service = MenuService(db)
        menus = menu_service.get_all_menus()
        return [MenuResponse.model_validate(menu) for menu in menus]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting menus: {e}")
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.foods import FoodCreate, FoodResponse
from database import get_db
from sqlalchemy.orm import Session
from services.foods_service import FoodsService
from typing import List
import uuid
router=APIRouter()

@router.post("/",status_code=status.HTTP_201_CREATED,summary="Create a new food",response_model=FoodResponse)
def create_food(food: FoodCreate, db: Session = Depends(get_db)) -> FoodResponse:
    try:
        food_service = FoodsService(db)
        new_food = food_service.create_food(food)
        return FoodResponse.model_validate(new_food)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error creating food: {e}")


@router.get("/",status_code=status.HTTP_200_OK,summary="Get all foods",response_model=List[FoodResponse])
def get_all_foods(db: Session = Depends(get_db)) -> List[FoodResponse]:
    try:
        food_service = FoodsService(db)
        foods = food_service.get_all_foods()
        return [FoodResponse.model_validate(food) for food in foods]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting foods: {e}")



@router.get("/{food_id}",status_code=status.HTTP_200_OK,summary="Get a food by id",response_model=FoodResponse)
def get_food_by_id(food_id: uuid.UUID, db: Session = Depends(get_db)) -> FoodResponse:
    try:
        food_service = FoodsService(db)
        food = food_service.get_food_by_id(food_id)
        if not food:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Food not found")
        return FoodResponse.model_validate(food)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting food: {e}")
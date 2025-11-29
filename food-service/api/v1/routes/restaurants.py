from fastapi import APIRouter, Depends, HTTPException, status
from schemas.restaurants import RestaurantCreate, RestaurantResponse
from database import get_db
from sqlalchemy.orm import Session
from services.restaurants_service import RestaurantService
from typing import List
import uuid
router=APIRouter()


@router.post("/",status_code=status.HTTP_201_CREATED,summary="Create a new restaurant",response_model=RestaurantResponse)
def create_restaurant(restaurant: RestaurantCreate, db: Session = Depends(get_db)) -> RestaurantResponse:
    try:
        restaurant_service = RestaurantService(db)
        new_restaurant = restaurant_service.create_restaurant(restaurant)
        return RestaurantResponse.model_validate(new_restaurant)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error creating restaurant: {e}")


@router.get("/",status_code=status.HTTP_200_OK,summary="Get all restaurants",response_model=List[RestaurantResponse])
def get_all_restaurants(db: Session = Depends(get_db)) -> List[RestaurantResponse]:
    try:
        restaurant_service = RestaurantService(db)
        restaurants = restaurant_service.get_all_restaurants()
        return [RestaurantResponse.model_validate(restaurant) for restaurant in restaurants]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting restaurants: {e}")


@router.get("/{restaurant_id}",status_code=status.HTTP_200_OK,summary="Get a restaurant by id",response_model=RestaurantResponse)
def get_restaurant_by_id(restaurant_id: uuid.UUID, db: Session = Depends(get_db)) -> RestaurantResponse:
    try:
        restaurant_service = RestaurantService(db)
        restaurant = restaurant_service.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Restaurant not found")
        return RestaurantResponse.model_validate(restaurant)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting restaurant: {e}")
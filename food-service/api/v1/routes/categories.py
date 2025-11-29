from fastapi import APIRouter
from schemas.categories import CategoryCreate, CategoryResponse
# from models.categories import Category
from database import get_db
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from services.categories import CategoryService
# from repository.categories import CategoryRepository
from typing import List
router=APIRouter()


@router.post("/",status_code=status.HTTP_201_CREATED,summary="Create a new category",response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)) -> CategoryResponse:
    try:
        category_service = CategoryService(db)
        new_category = category_service.create_category(category)
        return CategoryResponse.model_validate(new_category)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error creating category: {e}")


@router.get("/",status_code=status.HTTP_200_OK,summary="Get all categories",response_model=List[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)) -> List[CategoryResponse]:
    try:
        category_service = CategoryService(db)
        categories = category_service.get_all_categories()
        return categories
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting categories: {e}")
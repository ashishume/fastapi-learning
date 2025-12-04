from fastapi import APIRouter, Depends, HTTPException, status, Request
from schemas.foods import FoodCreate, FoodResponse
from database import get_db
from sqlalchemy.orm import Session
from services.foods_service import FoodsService
from typing import List
from core.rate_limiter import RateLimiter
import uuid
import logging
from core.redis_client import get_redis_client


router = APIRouter()

def get_rate_limiter() -> RateLimiter:
    """Get rate limiter instance with Redis client."""
    redis_client = get_redis_client()
    return RateLimiter(redis_client, max_requests=5, window_seconds=30)

@router.post("/",status_code=status.HTTP_201_CREATED,summary="Create a new food",response_model=FoodResponse)
def create_food(food: FoodCreate, db: Session = Depends(get_db)) -> FoodResponse:
    try:
        food_service = FoodsService(db)
        new_food = food_service.create_food(food)
        return FoodResponse.model_validate(new_food)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error creating food: {e}")


@router.get("/", status_code=status.HTTP_200_OK, summary="Get all foods", response_model=List[FoodResponse])
async def get_all_foods(
    request: Request, 
    db: Session = Depends(get_db),
    rate_limiter: RateLimiter = Depends(get_rate_limiter)
) -> List[FoodResponse]:
    try:
        client_ip = request.client.host if request.client else "unknown"
        rate_limit_key = f"rate_limit:foods:{client_ip}"

        # Check rate limit
        if not await rate_limiter.check_rate_limit(rate_limit_key):
            remaining = await rate_limiter.get_remaining_requests(rate_limit_key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Too many requests. Remaining requests: {remaining}",
                headers={"Retry-After": "60", "X-RateLimit-Remaining": str(remaining)}
            ) 

        food_service = FoodsService(db)
        foods = food_service.get_all_foods()
        return [FoodResponse.model_validate(food) for food in foods]
    except HTTPException:
        # Re-raise HTTP exceptions (like rate limit errors)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting foods: {e}"
        )



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
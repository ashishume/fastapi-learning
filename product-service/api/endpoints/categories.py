import json
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, status
from core.database import get_db
from models.category import Category
from schemas.category import CategoryCreate, CategoryResponse, CategoryResponseList
from sqlalchemy.orm import Session
from core.redis_client import redis_client

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def category_create(
    item: CategoryCreate, db: Session = Depends(get_db)
) -> CategoryResponse:
    try:
        logger.info(f"Category created ${item.name}")
        db_item = Category(name=item.name, slug=item.slug, description=item.description)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)

        logger.info("successfully added")
        return db_item

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error while creating item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Item already exists"
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"db error ${str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="db error"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"unexpected error {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="unexpected error"
        )


@router.get("/", response_model=CategoryResponseList, status_code=status.HTTP_200_OK)
async def read_categories(db: Session = Depends(get_db)):
    try:
        logger.info("fetching categories")

        cached_key = "category:all"
        cached_data = await redis_client.get(cached_key)

        if cached_data:
            logger.info("returning cached data")
            return json.loads(cached_data)

        db_items = db.query(Category).all()
        
        # Convert to response format
        response_data = {
            "categories": [
                CategoryResponse.model_validate(item).model_dump() for item in db_items
            ]
        }

        # Cache the serialized response
        await redis_client.set(cached_key, json.dumps(response_data), ex=60)
        
        # Return SQLAlchemy objects (Pydantic will handle conversion)
        return {"categories": db_items}
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An unexpected error occurred"
        )


@router.get(
    "/{categoryId}", response_model=CategoryResponse, status_code=status.HTTP_200_OK
)
def fetch_by_category_id(
    categoryId: str, db: Session = Depends(get_db)
) -> CategoryResponse:
    try:
        logger.info("fetching category by id")

        db_item = db.query(Category).filter(Category.id == categoryId).first()

        if not db_item:
            raise HTTPException(
                detail="category id not found", status_code=status.HTTP_404_NOT_FOUND
            )
        return db_item
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="error"
        )

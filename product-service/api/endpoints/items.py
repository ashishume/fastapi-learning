"""Item endpoints for CRUD operations with rate limiting examples."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from core.database import get_db
from models.category import Category
from models.item import Item
from schemas.item import ItemCreate, ItemListResponse, ItemResponse, ItemUpdate
from core.rate_limiter import create_rate_limit_dependency

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new item",
    response_description="The created item",
    # Rate Limit: 50 requests per minute for creating items
    # This is more restrictive than GET endpoints since POST is a mutation
    dependencies=[Depends(create_rate_limit_dependency(limit=50, window=60))],
)
def create_item(
    item: ItemCreate,
    request: Request,  # Required for rate limiting
    db: Session = Depends(get_db)
) -> ItemResponse:
    try:
        logger.info(f"Creating new item: {item.name}")
        category = db.query(Category).filter(Category.id == item.category_id).first()
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found in the database",
            )
        db_item = Item(
            name=item.name, description=item.description, category_id=item.category_id
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)

        logger.info(f"Successfully created item with ID: {db_item.id}")
        return db_item

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error while creating item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item with this name may already exist or violates constraints",
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while creating item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create item due to database error",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while creating item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/",
    response_model=ItemListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all items",
    response_description="List of all items",
    # Rate Limit: 200 requests per minute for listing items
    # GET endpoints typically allow more requests than mutations
    dependencies=[Depends(create_rate_limit_dependency(limit=200, window=60))],
)
def read_items(
    request: Request,  # Required for rate limiting
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> ItemListResponse:
    try:
        logger.info(f"Fetching items (skip={skip}, limit={limit})")

        # Validate pagination parameters
        if skip < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skip parameter must be non-negative",
            )
        if limit <= 0 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit parameter must be between 1 and 100",
            )

        item_list = (
            db.query(Item)
            .options(joinedload(Item.category))
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.info(f"Successfully fetched {len(item_list)} items")

        return {"items": item_list}

    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch items due to database error",
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific item",
    response_description="The requested item",
    # Rate Limit: 300 requests per minute for single item lookups
    # Single item queries are less resource-intensive than listing all items
    dependencies=[Depends(create_rate_limit_dependency(limit=300, window=60))],
)
def read_item(
    item_id: int,
    request: Request,  # Required for rate limiting
    db: Session = Depends(get_db)
) -> ItemResponse:
    try:
        logger.info(f"Fetching item with ID: {item_id}")

        db_item = (
            db.query(Item)
            .options(joinedload(Item.category))
            .filter(Item.id == item_id)
            .first()
        )

        if db_item is None:
            logger.warning(f"Item with ID {item_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with ID {item_id} not found",
            )

        logger.info(f"Successfully fetched item with ID: {item_id}")
        return db_item

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch item due to database error",
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.put(
    "/{item_id}",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    # Rate Limit: 100 requests per minute for updating items
    # Update operations are mutations but more common than creates
    dependencies=[Depends(create_rate_limit_dependency(limit=100, window=60))],
)
def update_item(
    item_id: int,
    item_update_payload: ItemUpdate,
    request: Request,  # Required for rate limiting
    db: Session = Depends(get_db)
) -> ItemResponse:
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        logger.log("Item not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    update_item = item_update_payload.dict(exclude_unset=True)
    for key, value in update_item.items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)

    return db_item

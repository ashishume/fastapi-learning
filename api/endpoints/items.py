"""Item endpoints for CRUD operations."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from core.database import get_db
from models.item import Item
from schemas.item import ItemCreate, ItemListResponse, ItemResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new item",
    response_description="The created item",
)
def create_item(item: ItemCreate, db: Session = Depends(get_db)) -> ItemResponse:
    try:
        logger.info(f"Creating new item: {item.name}")

        db_item = Item(name=item.name, description=item.description)
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
)
def read_items(
    db: Session = Depends(get_db), skip: int = 0, limit: int = 100
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

        item_list = db.query(Item).offset(skip).limit(limit).all()
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
)
def read_item(item_id: int, db: Session = Depends(get_db)) -> ItemResponse:
    try:
        logger.info(f"Fetching item with ID: {item_id}")

        db_item = db.query(Item).filter(Item.id == item_id).first()

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

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
    """
    Create a new item with the following information:

    - **name**: The name of the item (required)
    - **description**: A description of the item (optional)

    Returns:
        ItemResponse: The created item with its assigned ID

    Raises:
        HTTPException: 400 if item data is invalid
        HTTPException: 500 if there's a database error
    """
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
    """
    Retrieve all items from the database.

    Parameters:
        - **skip**: Number of items to skip (for pagination)
        - **limit**: Maximum number of items to return (default: 100, max: 100)

    Returns:
        ItemListResponse: A list containing all items

    Raises:
        HTTPException: 500 if there's a database error
    """
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
    """
    Retrieve a specific item by its ID.

    Parameters:
        - **item_id**: The ID of the item to retrieve

    Returns:
        ItemResponse: The requested item

    Raises:
        HTTPException: 404 if item not found
        HTTPException: 500 if there's a database error
    """
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


@router.put(
    "/{item_id}",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an item",
    response_description="The updated item",
)
def update_item(
    item_id: int, item: ItemCreate, db: Session = Depends(get_db)
) -> ItemResponse:
    """
    Update an existing item.

    Parameters:
        - **item_id**: The ID of the item to update
        - **name**: The new name of the item
        - **description**: The new description of the item

    Returns:
        ItemResponse: The updated item

    Raises:
        HTTPException: 404 if item not found
        HTTPException: 500 if there's a database error
    """
    try:
        logger.info(f"Updating item with ID: {item_id}")

        db_item = db.query(Item).filter(Item.id == item_id).first()

        if db_item is None:
            logger.warning(f"Item with ID {item_id} not found for update")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with ID {item_id} not found",
            )

        # Update item fields
        db_item.name = item.name
        db_item.description = item.description

        db.commit()
        db.refresh(db_item)

        logger.info(f"Successfully updated item with ID: {item_id}")
        return db_item

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while updating item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update item due to database error",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while updating item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an item",
    response_description="Item successfully deleted",
)
def delete_item(item_id: int, db: Session = Depends(get_db)) -> None:
    """
    Delete an item by its ID.

    Parameters:
        - **item_id**: The ID of the item to delete

    Returns:
        None: 204 No Content on success

    Raises:
        HTTPException: 404 if item not found
        HTTPException: 500 if there's a database error
    """
    try:
        logger.info(f"Deleting item with ID: {item_id}")

        db_item = db.query(Item).filter(Item.id == item_id).first()

        if db_item is None:
            logger.warning(f"Item with ID {item_id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with ID {item_id} not found",
            )

        db.delete(db_item)
        db.commit()

        logger.info(f"Successfully deleted item with ID: {item_id}")

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while deleting item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item due to database error",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while deleting item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

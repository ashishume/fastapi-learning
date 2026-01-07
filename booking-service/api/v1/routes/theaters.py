import datetime
from sqlalchemy import delete, select
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.Theater import TheaterCreate, TheaterResponse
from models.theaters import Theater
from services.search_service import SearchService

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new theater",
    response_model=TheaterResponse,
)
def create_theater(
    theater: TheaterCreate, db: Session = Depends(get_db)
) -> TheaterResponse:
    try:
        new_theater = Theater(
            name=theater.name,
            location=theater.location,
            description=theater.description,
            address=theater.address,
            city=theater.city,
        )
        db.add(new_theater)
        db.commit()
        db.refresh(new_theater)

        # Sync to Elasticsearch
        search_service = SearchService(db)
        search_service.sync_theatre_with_elastic_search(new_theater)

        return TheaterResponse.model_validate(new_theater)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating theater: {e}",
        )


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Get all theaters",
    response_model=List[TheaterResponse],
)
def get_all_theaters(db: Session = Depends(get_db)) -> List[TheaterResponse]:
    try:
        theaters = db.execute(select(Theater)).scalars().all()
        return [TheaterResponse.model_validate(theater) for theater in theaters]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting theaters: {e}",
        )


@router.get(
    "/{theater_id}",
    status_code=status.HTTP_200_OK,
    summary="Get a theater by id",
    response_model=TheaterResponse,
)
def get_theater_by_id(
    theater_id: str, db: Session = Depends(get_db)
) -> TheaterResponse:
    try:
        theater = db.execute(
            select(Theater).where(Theater.id == theater_id)
        ).scalar_one_or_none()
        if theater is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Theater not found"
            )
        return TheaterResponse.model_validate(theater)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting theater: {e}",
        )


@router.patch(
    "/{theater_id}",
    status_code=status.HTTP_200_OK,
    summary="Update a theater by id",
    response_model=TheaterResponse,
)
def update_theater_by_id(
    theater_id: str, theater_update: dict[str, Any], db: Session = Depends(get_db)
) -> Any:
    try:
        theater_obj = db.execute(
            select(Theater).where(Theater.id == theater_id)
        ).scalar_one_or_none()
        if theater_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Theater not found"
            )
        for key, value in theater_update.items():
            setattr(theater_obj, key, value)
        theater_obj.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(theater_obj)
        return TheaterResponse.model_validate(theater_obj)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating theater: {e}",
        )


@router.delete(
    "/{theater_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a theater by id",
    response_model=TheaterResponse,
)
def delete_theater_by_id(
    theater_id: str, db: Session = Depends(get_db)
) -> TheaterResponse:
    try:
        db.execute(delete(Theater).where(Theater.id == theater_id))
        db.commit()
        return {"message": "Theater deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting theater: {e}",
        )

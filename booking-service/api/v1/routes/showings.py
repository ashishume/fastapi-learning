import datetime
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, load_only
from database import get_db
from schemas.showings import ShowingCreate, ShowingResponse
from models.movies import Movie
from models.theaters import Theater
from models.showings import Showing
router=APIRouter()

@router.post("/",status_code=status.HTTP_201_CREATED,summary="Create a new showing",response_model=ShowingResponse)
def create_showing(showing: ShowingCreate, db: Session = Depends(get_db)) -> ShowingResponse:
    try:
        if showing.show_start_datetime >= showing.show_end_datetime:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Show start datetime must be before show end datetime")
        if showing.available_seats <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Available seats must be greater than 0")

        movie=db.execute(select(Movie).where(Movie.id == showing.movie_id)).scalar_one_or_none()    
        if movie is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Movie not found")
        theater=db.execute(select(Theater).where(Theater.id==showing.theater_id)).scalar_one_or_none()
        if theater is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Theater not found")


        is_showing_exists=db.execute(select(Showing).where(
            Showing.movie_id == showing.movie_id, 
            Showing.theater_id == showing.theater_id, 
            Showing.show_start_datetime == showing.show_start_datetime.isoformat(), 
            Showing.show_end_datetime == showing.show_end_datetime.isoformat()
        )).scalar_one_or_none()

        if is_showing_exists is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"A showing already exists for this movie and theater at this time")
        
        new_showing=Showing(
            movie_id=showing.movie_id,
            theater_id=showing.theater_id,
            show_start_datetime=showing.show_start_datetime.isoformat(),
            show_end_datetime=showing.show_end_datetime.isoformat(),
            available_seats=showing.available_seats,
            is_active=showing.is_active,
            expires_at=showing.expires_at,
        )
        db.add(new_showing)
        db.commit()
        db.refresh(new_showing)
        return ShowingResponse.model_validate(new_showing)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error creating showing: {e}")

@router.get("/",status_code=status.HTTP_200_OK,summary="Get all showings",response_model=List[ShowingResponse])
def get_all_showings(db: Session = Depends(get_db)) -> List[ShowingResponse]:
    try:
       showings=db.execute(select(Showing).options(
           joinedload(Showing.movie).load_only(
               Movie.id, 
               Movie.title, 
               Movie.duration_minutes, 
               Movie.genre, 
               Movie.rating, 
               Movie.poster_url
           ),
           joinedload(Showing.theater).load_only(
               Theater.id, 
               Theater.name, 
               Theater.location, 
               Theater.city
           )
       ).where(Showing.expires_at > datetime.datetime.utcnow())).scalars().all()
       # check if the showing is expired
       
       return [ShowingResponse.model_validate(showing) for showing in showings]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting showings: {e}")
    

@router.get("/{theater_id}/{movie_id}",status_code=status.HTTP_200_OK,summary="Get all showings by theater id",response_model=List[ShowingResponse])
def get_showing_by_theater_id_and_movie_id(theater_id: str, movie_id: str, db: Session = Depends(get_db)) -> List[ShowingResponse]:
    try:
        showings=db.execute(select(Showing).where(
            Showing.theater_id == theater_id, 
            Showing.movie_id == movie_id,
            Showing.expires_at > datetime.datetime.utcnow()
        )).scalars().all()
        if showings is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Showings not found")
        return [ShowingResponse.model_validate(showing) for showing in showings]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting showings by theater id and movie id: {e}")
    
@router.patch("/{showing_id}",status_code=status.HTTP_200_OK,summary="Update a showing by id",response_model=ShowingResponse)
def update_showing_by_id(showing_id: str, showing_update: dict[str, Any], db: Session = Depends(get_db)) -> ShowingResponse:
    try:
        showing = db.execute(select(Showing).where(Showing.id == showing_id)).scalar_one_or_none()
        if showing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Showing with ID {showing_id} not found")
        for key, value in showing_update.items():
            setattr(showing, key, value)
        showing.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(showing)
        return ShowingResponse.model_validate(showing)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error updating showing with ID {showing_id}: {e}")
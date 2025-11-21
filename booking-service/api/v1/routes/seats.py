import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from schemas.seats import SeatCreate, SeatCreateResponse, SeatResponse, TheaterBrief
from database import get_db
from models.seats import Seat, SeatType
# from models.theaters import Theater
# from models.showings import Showing
# from models.movies import Movie
from typing import List
router=APIRouter()

@router.post("/{theater_id}/initialize",status_code=status.HTTP_201_CREATED,summary="Initialize seats for a theater",response_model=List[SeatResponse])
def initialize_seats(theater_id: UUID, rows: int = 15, seats_per_row: int = 9, db: Session = Depends(get_db)) -> List[SeatResponse]:
    try:

       seats = []
       rows_list = [chr(65 + i) for i in range(rows)]  # A, B, C, ...   , P

       for row in rows_list:
           for col in range(1, seats_per_row + 1):
               seat_number = f"{row}{col}"
               seats.append(Seat(
                   theater_id=theater_id,
                   seat_number=seat_number,
                   row=row,
                   column=str(col),
                   seat_type=SeatType.REGULAR,
               ))
       db.add_all(seats)
       db.commit()
       return [SeatResponse.model_validate(seat) for seat in seats]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error initializing seats: {e}")


@router.get("/{theater_id}",status_code=status.HTTP_200_OK,summary="Get all seats",response_model=List[SeatResponse])
def get_all_seats(theater_id: UUID, db: Session = Depends(get_db)) -> List[SeatResponse]:
    try:
        seats = db.execute(select(Seat).where(Seat.theater_id == theater_id)).scalars().all()
        
        return [SeatResponse.model_validate(seat) for seat in seats]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting seats: {e}")


@router.delete("/{seat_id}",status_code=status.HTTP_204_NO_CONTENT,summary="Delete a seat",response_model=None)
def delete_seat(seat_id: UUID, db: Session = Depends(get_db)) -> None:
        try:
            seat = db.execute(select(Seat).where(Seat.id == seat_id)).scalar_one_or_none()
            if seat is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Seat not found")
            db.delete(seat)
            db.commit()
            return None
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error deleting seat: {e}")
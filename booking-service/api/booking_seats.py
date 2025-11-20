import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from database import get_db
from schemas.bookings import BookingCreate, BookingResponse
# from models.bookings import Booking
# from models.movies import Movie
# from models.theaters import Theater
# from models.showings import Showing
# from models.seats import Seat
# from models.bookings import BookingStatus
from models.booking_seats import BookingSeat
from schemas.booking_seats import BookingSeatCreate, BookingSeatResponse
import uuid
router=APIRouter()


@router.post("/",status_code=status.HTTP_201_CREATED,summary="Create a new booking seat",response_model=BookingSeatResponse)
def create_booking_seat(booking: BookingSeatCreate, request: Request,db: Session = Depends(get_db)) -> BookingSeatResponse:
    new_booking_seat = BookingSeat(
        booking_id=booking.booking_id,
        seat_id=booking.seat_id,
        showing_id=booking.showing_id
    )
    db.add(new_booking_seat)
    db.commit()
    db.refresh(new_booking_seat)
    return BookingSeatResponse.model_validate(new_booking_seat)
        

@router.get("/",status_code=status.HTTP_200_OK,summary="Get all booking seats",response_model=List[BookingSeatResponse])
def get_all_booking_seats(db: Session = Depends(get_db)) -> List[BookingSeatResponse]:
    booking_seats = db.execute(select(BookingSeat)).scalars().all()
    return [BookingSeatResponse.model_validate(booking_seat) for booking_seat in booking_seats]
   

@router.get("/{booking_id}",status_code=status.HTTP_200_OK,summary="Get a booking seat by id",response_model=BookingSeatResponse)
def get_booking_seat_by_id(booking_seat_id: str, db: Session = Depends(get_db)) -> BookingSeatResponse:
    booking_seat = db.execute(select(BookingSeat).where(BookingSeat.id == booking_seat_id)).scalar_one_or_none()
    if booking_seat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Booking seat not found")
    return BookingSeatResponse.model_validate(booking_seat)



@router.delete("/{booking_seat_id}",status_code=status.HTTP_204_NO_CONTENT,summary="Delete a booking seat",response_model=None)
def delete_booking_seat(booking_seat_id: str, db: Session = Depends(get_db)) -> None:
    booking_seat = db.execute(select(BookingSeat).where(BookingSeat.id == booking_seat_id)).scalar_one_or_none()
    if booking_seat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Booking seat not found")
    db.delete(booking_seat)
    db.commit()
    return None
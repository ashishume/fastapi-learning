from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models.booking_seats import BookingSeat
from models.locked_seats import LockedSeat
from schemas.booking_seats import BookingSeatCreate, BookingSeatResponse, LockedSeatResponse, ShowingSeatsResponse
from schemas.locked_seats import BookingLockCreate
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
        

@router.get("/{showing_id}",status_code=status.HTTP_200_OK,summary="Get all booking and locked seats",response_model=ShowingSeatsResponse)
def get_all_booking_seats(showing_id:str,db: Session = Depends(get_db)) -> ShowingSeatsResponse:
    booking_seats = db.execute(
        select(BookingSeat)
        .options(joinedload(BookingSeat.seat))
        .where(BookingSeat.showing_id==showing_id)
    ).scalars().all()

    locked_seats = db.execute(
        select(LockedSeat)
        .where(LockedSeat.showing_id==showing_id)
    ).scalars().all()

    return ShowingSeatsResponse(
        booked_seats=[BookingSeatResponse.model_validate(bs) for bs in booking_seats],
        locked_seats=[LockedSeatResponse.model_validate(ls) for ls in locked_seats]
    )

@router.post("/lock",status_code=status.HTTP_201_CREATED,summary="Lock a seat",response_model=LockedSeatResponse)
def lock_seat(locked_seat: BookingLockCreate,db: Session = Depends(get_db)) -> LockedSeatResponse:
    new_locked_seat = LockedSeat(
        showing_id=locked_seat.showing_id,
        seat_id=locked_seat.seat_id
    )
    db.add(new_locked_seat)
    db.commit()
    db.refresh(new_locked_seat)
    return LockedSeatResponse.model_validate(new_locked_seat)
   

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
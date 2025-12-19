from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models.booking_seats import BookingSeat
from models.locked_seats import LockedSeat
from schemas.booking_seats import BookingSeatCreate, BookingSeatResponse, ShowingSeatsResponse, LockedSeatResponse
from uuid import UUID
from schemas.locked_seats import BookingLockCreate,BookingLockResponse

import datetime
from core.redis_client import get_redis
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
async def get_all_booking_seats(showing_id:str,db: Session = Depends(get_db)) -> ShowingSeatsResponse:
    booking_seats = db.execute(
        select(BookingSeat)
        .options(joinedload(BookingSeat.seat))
        .where(BookingSeat.showing_id==showing_id)
    ).scalars().all()

    redis_client = await get_redis()
    if redis_client is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Redis connection failed") 

    showing_id_str = str(showing_id)      
    locked_seats = await redis_client.keys(f"locked_seat:{showing_id_str}:*")
    locked_seats = [LockedSeatResponse(seat_id=UUID(ls.split(":")[2]), showing_id=UUID(ls.split(":")[1])) for ls in locked_seats]
    return ShowingSeatsResponse(booked_seats=[BookingSeatResponse.model_validate(bs) for bs in booking_seats],locked_seats=locked_seats)




@router.post("/lock",status_code=status.HTTP_201_CREATED,summary="Lock a seat",response_model=BookingLockResponse)
async def lock_seat(locked_seat: BookingLockCreate,db: Session = Depends(get_db)) -> BookingLockResponse:
    redis_client = await get_redis()
    if redis_client is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Redis connection failed")
    # Convert UUIDs to strings for Redis (Redis requires string, bytes, int, or float)
    showing_id_str = str(locked_seat.showing_id)
    seat_id_str = str(locked_seat.seat_id)

    #set the seat as locked for 10 minutes
    await redis_client.set(f"locked_seat:{showing_id_str}:{seat_id_str}", seat_id_str, ex=600)
    return BookingLockResponse(
        # id=locked_seat.id,
        seat_id=locked_seat.seat_id,
        showing_id=locked_seat.showing_id
    )
   

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
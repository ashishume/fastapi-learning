import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from database import get_db
from schemas.bookings import BookingCreate, BookingResponse
from models.bookings import Booking
from models.showings import Showing
from models.seats import Seat
from models.booking_seats import BookingSeat
from services.booking_service import BookingService

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create a new booking", response_model=BookingResponse)
async def create_booking(booking: BookingCreate, request: Request, db: Session = Depends(get_db)) -> BookingResponse:
    try:
        booking_service = BookingService(db)
        return await booking_service.create_booking(booking, request.state.user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating booking: {e}"
        )

@router.get("/",status_code=status.HTTP_200_OK,summary="Get all bookings",response_model=List[BookingResponse])
def get_all_bookings(request: Request, db: Session = Depends(get_db)) -> List[BookingResponse]:
    try:
        booking_service=BookingService(db)
        bookings = booking_service.get_all_bookings(request.state.user_id)
        return bookings
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting bookings: {e}")

@router.get("/{booking_id}",status_code=status.HTTP_200_OK,summary="Get a booking by id",response_model=BookingResponse)
def get_booking_by_id(booking_id: str, db: Session = Depends(get_db)) -> BookingResponse:
    try:
        booking = db.execute(select(Booking).where(Booking.id == booking_id)).scalar_one_or_none()
        if booking is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Booking not found")
        return BookingResponse.model_validate(booking)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting booking: {e}")
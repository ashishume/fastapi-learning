import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from database import get_db
from schemas.bookings import BookingCreate, BookingResponse
from models.bookings import Booking
from models.movies import Movie
from models.theaters import Theater
from models.showings import Showing
from models.seats import Seat
from models.bookings import BookingStatus
from models.booking_seats import BookingSeat
import uuid
router=APIRouter()


@router.post("/",status_code=status.HTTP_201_CREATED,summary="Create a new booking",response_model=BookingResponse)
def create_booking(booking: BookingCreate, request: Request,db: Session = Depends(get_db)) -> BookingResponse:
    try:
        is_showing_exists=db.execute(select(Showing).where(Showing.id== booking.showing_id, Showing.expires_at > datetime.datetime.utcnow())).scalar_one_or_none()
        if is_showing_exists is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Showing not found or expired")


        # Check if any seats are already booked in a single query for better performance
        existing_bookings = db.execute(
            select(BookingSeat.seat_id)
            .where(
                BookingSeat.seat_id.in_(booking.seats_ids),
                BookingSeat.showing_id == booking.showing_id
            )
        ).scalars().all()
        
        if existing_bookings:
            booked_seat_ids = list(existing_bookings)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Seats already booked: {booked_seat_ids}"
            )
        
        new_booking = Booking(
            user_id=request.state.user_id,
            # movie_id=is_showing_exists.movie_id,
            # theater_id=is_showing_exists.theater_id,
            showing_id=booking.showing_id,
            total_price=booking.total_price,
            status=BookingStatus.CONFIRMED,
            booking_number=str(uuid.uuid4()),
        )

        db.add(new_booking)
        db.flush()

        for seat_id in booking.seats_ids:
            booking_seat = BookingSeat(
                booking_id=new_booking.id,
                seat_id=seat_id,
                showing_id=booking.showing_id
            )
            db.add(booking_seat)
        db.commit()
        db.refresh(new_booking)

        return BookingResponse.model_validate(new_booking)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error creating booking: {e}")

@router.get("/",status_code=status.HTTP_200_OK,summary="Get all bookings",response_model=List[BookingResponse])
def get_all_bookings(db: Session = Depends(get_db)) -> List[BookingResponse]:
    try:
        bookings = db.execute(select(Booking).options(
            joinedload(Booking.showing).load_only(
                Showing.id,
                Showing.movie_id,
                Showing.theater_id,
                Showing.show_start_datetime,
                Showing.show_end_datetime
            ),
            joinedload(Booking.booking_seats).joinedload(BookingSeat.seat).load_only(
                Seat.id,
                Seat.seat_number,
                Seat.row,
                Seat.column,
                Seat.seat_type
            ),
        )).scalars().all()
        return [BookingResponse.model_validate(booking) for booking in bookings]
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
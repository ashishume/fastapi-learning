import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session, joinedload
from database import get_db
from schemas.bookings import BookingCreate, BookingResponse
from models.bookings import Booking
from models.movies import Movie
from models.theaters import Theater
from models.showings import Showing
from models.seats import Seat
from models.bookings import BookingStatus
import uuid
router=APIRouter()


@router.post("/",status_code=status.HTTP_201_CREATED,summary="Create a new booking",response_model=BookingResponse)
def create_booking(booking: BookingCreate, request: Request,db: Session = Depends(get_db)) -> BookingResponse:
    try:
        is_booking_exists=db.query(Booking).filter(Booking.user_id == request.state.user_id, Booking.movie_id == booking.movie_id, Booking.theater_id == booking.theater_id, Booking.showing_id == booking.showing_id, Booking.seats_id == booking.seats_id, Booking.status == BookingStatus.CONFIRMED).first()
        if is_booking_exists is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Booking already exists")

        movie=db.query(Movie).filter(Movie.id == booking.movie_id).first()
        if movie is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Movie not found")
        theater=db.query(Theater).filter(Theater.id == booking.theater_id).first()
        if theater is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Theater not found")
        showing=db.query(Showing).filter(Showing.id == booking.showing_id, Showing.expires_at > datetime.datetime.utcnow()).first()
        if showing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Showing not found or expired")
        seats=db.query(Seat).filter(Seat.id == booking.seats_id, Seat.showing_id == booking.showing_id).first()
        if seats is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Seat not found or not available")
        booking_number=uuid.uuid4()
        booking_status=BookingStatus.CONFIRMED
        booking_number=str(booking_number)
        print(request.state.user_id)
        new_booking = Booking(
            user_id=request.state.user_id,
            movie_id=booking.movie_id,
            theater_id=booking.theater_id,
            showing_id=booking.showing_id,
            seats_id=booking.seats_id,
            total_price=booking.total_price,
            status=booking_status,
            booking_number=booking_number,
        )

        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)

        return BookingResponse.model_validate(new_booking)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error creating booking: {e}")

@router.get("/",status_code=status.HTTP_200_OK,summary="Get all bookings",response_model=List[BookingResponse])
def get_all_bookings(db: Session = Depends(get_db)) -> List[BookingResponse]:
    try:
        bookings = db.query(Booking).options(
            joinedload(Booking.movie).load_only(
                Movie.id,
                Movie.title,
                Movie.duration_minutes,
                Movie.genre,
                Movie.rating,
                Movie.poster_url
            ),
            joinedload(Booking.theater).load_only(
                Theater.id,
                Theater.name,
                Theater.location,
                Theater.city
            ),
            joinedload(Booking.showing).load_only(
                Showing.id,
                Showing.movie_id,
                Showing.theater_id,
                Showing.show_start_datetime,
                Showing.show_end_datetime
            ),
            joinedload(Booking.seats).load_only(
                Seat.id,
                Seat.seat_number,
                Seat.row,
                Seat.column,
                Seat.seat_type
            ),
        ).all()
        return [BookingResponse.model_validate(booking) for booking in bookings]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting bookings: {e}")

@router.get("/{booking_id}",status_code=status.HTTP_200_OK,summary="Get a booking by id",response_model=BookingResponse)
def get_booking_by_id(booking_id: str, db: Session = Depends(get_db)) -> BookingResponse:
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if booking is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Booking not found")
        return BookingResponse.model_validate(booking)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting booking: {e}")
from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from models.bookings import Booking, BookingStatus
from models.booking_seats import BookingSeat
from schemas.bookings import BookingCreate, BookingResponse
from repository.booking_repo import BookingRepository
import uuid
import datetime

class BookingService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = BookingRepository(db)

    async def create_booking(self, booking_data: BookingCreate, user_id: UUID) -> BookingResponse:
        # Validate showing exists and is not expired
        showing = self.repository.get_if_showing_exists(booking_data)
        if showing is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Showing not found or expired"
            )

        # Check if any seats are already booked
        existing_bookings = self.repository.get_if_seats_are_already_booked(booking_data)
        check_if_seat_is_locked = await self.repository.get_if_seat_is_locked(booking_data.showing_id)
        
        if existing_bookings or check_if_seat_is_locked:
            booked_seat_ids = list(existing_bookings)
            locked_seat_ids = list(check_if_seat_is_locked)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Seats already booked: {booked_seat_ids} or Seats already locked: {locked_seat_ids}"
            )
        
        # Create the booking
        new_booking = Booking(
            user_id=user_id,
            showing_id=booking_data.showing_id,
            total_price=booking_data.total_price,
            status=BookingStatus.CONFIRMED,
            booking_number=str(uuid.uuid4()),
        )

        # Save booking to database
        self.repository.create_booking(new_booking)

        # Create booking seats
        booking_seats = [
            BookingSeat(
                booking_id=new_booking.id,
                seat_id=seat_id,
                showing_id=booking_data.showing_id
            )
            for seat_id in booking_data.seats_ids
        ]
        
        self.repository.create_booking_seats(booking_seats)

        # Refresh booking to get all relationships
        self.db.refresh(new_booking)

        return BookingResponse.model_validate(new_booking)


    def get_all_bookings(self,user_id: UUID) -> List[BookingResponse]:
     try:   
        bookings=self.repository.get_all_bookings(user_id)
        return [BookingResponse.model_validate(booking) for booking in bookings]
     except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting bookings: {e}")
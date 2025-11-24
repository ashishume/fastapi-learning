from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from models.bookings import Booking
from models.showings import Showing
from schemas.bookings import BookingCreate
from models.booking_seats import BookingSeat
import datetime
from models.movies import Movie
from models.theaters import Theater

class BookingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_booking(self, booking: Booking) -> Booking:
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def get_if_showing_exists(self, booking: BookingCreate) -> Showing | None:
        return self.db.execute(
            select(Showing).where(
                Showing.id == booking.showing_id,
                Showing.expires_at > datetime.datetime.utcnow()
            )
        ).scalar_one_or_none()

    def get_if_seats_are_already_booked(self, booking: BookingCreate) -> List[UUID]:
        return self.db.execute(
            select(BookingSeat.seat_id)
            .where(
                BookingSeat.seat_id.in_(booking.seats_ids),
                BookingSeat.showing_id == booking.showing_id
            )
        ).scalars().all()

    def create_booking_seats(self, booking_seats: List[BookingSeat]) -> List[BookingSeat]:
        self.db.add_all(booking_seats)
        self.db.commit()
        for booking_seat in booking_seats:
            self.db.refresh(booking_seat)
        return booking_seats

    def get_all_bookings(self, user_id: UUID) -> List[Booking]:
        return self.db.execute(
            select(Booking)
            .where(Booking.user_id == user_id)
            .options(
                joinedload(Booking.showing).load_only(
                    Showing.id,
                    Showing.movie_id,
                    Showing.theater_id,
                    Showing.show_start_datetime,
                    Showing.show_end_datetime
                ),
                joinedload(Booking.showing).joinedload(Showing.movie).load_only(
                    Movie.id,
                    Movie.title,
                    Movie.duration_minutes,
                    Movie.genre,
                    Movie.rating,
                    Movie.poster_url
                ),
                joinedload(Booking.showing).joinedload(Showing.theater).load_only(
                    Theater.id,
                    Theater.name,
                    Theater.location,
                    Theater.city
                ),
                joinedload(Booking.booking_seats).load_only(
                    BookingSeat.id,
                    BookingSeat.showing_id,
                    BookingSeat.created_at,
                    BookingSeat.updated_at
                ),
            )
        ).unique().scalars().all()
    
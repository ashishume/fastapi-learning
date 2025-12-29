# Requirements
# - Room -> regular room, luxury, suit
# - Customer
# - checkin/checkout service
# - Reservation system
# - Overbooking prevention
# - Availablity service

from enum import Enum
from threading import Lock
from datetime import date
import uuid


class RoomType(Enum):
    REGULAR = "regular"
    DELUX = "delux"
    LUXURY = "luxury"


class BookingStatus(Enum):
    CONFIRMED = "confirmed"
    CANCELED = "canceled"


class Room:
    def __init__(self, room_id: str, room_type: RoomType, price: float):
        self.room_id = room_id
        self.room_type = room_type
        self.is_available = False
        self.price = price
        self.lock = Lock()


class Customer:
    def __init__(self, customer_id: str, room_id: str):
        self.customer_id = customer_id
        self.assigned_room = room_id


class Booking:
    def __init__(
        self,
        user: Customer,
        room: Room,
        check_in_date: date,
        check_out_date: date,
    ):
        self.user = user
        self.room = room
        self.booking_id = str(uuid.uuid4())
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.status = BookingStatus.CONFIRMED


class RoomInventory:
    def __init__(self):
        self.bookings: dict[str, list[Booking]] = {}

    def is_available(self, room: Room, check_in: date, check_out: date) -> bool:
        for booking in self.bookings.get(room.room_id, []):
            if booking.status != BookingStatus.CANCELED:
                if not (
                    check_out <= booking.check_in_date
                    or check_in >= booking.check_out_date
                ):
                    return False
        return True

    def add_booking(self, booking: Booking):
        self.bookings.setdefault(booking.room.room_id, []).append(booking)


class Hotel:
    def __init__(self, hotel_id: str, name: str):
        self.hotel_id = hotel_id
        self.hotel_name = name
        self.rooms: list[Room] = []

    def add_room(self, room: Room):
        self.rooms.append(room)

    def get_rooms_by_type(self, room_type: RoomType):
        return [room for room in self.rooms if room.room_type == room_type]


class BookingService:
    def __init__(self, inventory: RoomInventory):
        self.inventory = inventory

    def book_room(
        self,
        user: Customer,
        check_in_date: date,
        check_out_date: date,
        hotel: Hotel,
        room_type: RoomType,
    ) -> Booking | None:
        for room in hotel.get_rooms_by_type(room_type):
            with room.lock:
                if self.inventory.is_available(room, check_in_date, check_out_date):
                    booking = Booking(user, room, check_in_date, check_out_date)
                    self.inventory.add_booking(booking)
                    return booking
        return None

    def cancel_booking(self, booking: Booking):
        booking.status = BookingStatus.CANCELED


if __name__ == "__main__":
    hotel = Hotel(hotel_id="1", name="Hotel 1")
    room = Room(room_id="1", room_type=RoomType.REGULAR, price=100)
    hotel.add_room(room)
    customer = Customer(customer_id="1", room_id="1")
    booking_service = BookingService(RoomInventory())
    booking = booking_service.book_room(customer, date(2025, 1, 1), date(2025, 1, 3), hotel, RoomType.REGULAR)
    
    print(booking)

    booking_service.cancel_booking(booking)
    
    print(booking)


from enum import Enum
from abc import ABC, abstractmethod
from threading import Lock, RLock
import uuid
from datetime import datetime, timedelta
class SEAT_TYPE(Enum):
    REGULAR='regular'
    PREMIUM='premium'
    RECLINER='recliner' 

class RATES(Enum):
    REGULAR=200
    PREMIUM=300
    RECLINER=600 

class User:
    def __init__(self,name:str,email:str):
        self.user_id=str(uuid.uuid4())
        self.name=name
        self.email=email

class Movie:
   def __init__(self,movie_id:str,movie_name:str):
    self.movie_name=movie_name
    self.movie_id=movie_id

class Theater:
    def __init__(self,theater_id:str, theater_name:str,location:str):
        self.theater_id=theater_id
        self.theater_name=theater_name
        self.location=location

class Seats:
    def __init__(self,seat_id:str,seat_name:str,seat_type:SEAT_TYPE):
        self.seat_id=seat_id
        self.seat_name=seat_name
        self.seat_type=seat_type
        self.locked_by=None  # User ID who locked the seat
        self.locked_at=None  # Timestamp when seat was locked
        self.lock_expires_at=None  # Timestamp when lock expires
    
    def is_locked(self)->bool:
        """Check if seat is currently locked and not expired"""
        if self.locked_by is None:
            return False
        if self.lock_expires_at is None:
            return True
        return datetime.now() < self.lock_expires_at
    
    def lock(self, user_id:str, lock_duration_seconds:int=300)->bool:
        """
        Lock the seat for a user
        Returns True if lock was successful, False if seat is already locked
        """
        if self.is_locked() and self.locked_by != user_id:
            return False  # Seat is locked by another user
        self.locked_by = user_id
        self.locked_at = datetime.now()
        self.lock_expires_at = datetime.now() + timedelta(seconds=lock_duration_seconds)
        return True
    
    def unlock(self, user_id:str)->bool:
        """
        Unlock the seat if it's locked by the specified user
        Returns True if unlock was successful, False otherwise
        """
        if self.locked_by == user_id:
            self.locked_by = None
            self.locked_at = None
            self.lock_expires_at = None
            return True
        return False
    
         

class Showings:
    def __init__(self, showing_id:str, start_time:str,end_time:str,movie:Movie,theater:Theater,seats:list[Seats]=None):
        self.showing_id=showing_id
        self.theater=theater
        self.movie=movie
        self.start_time=start_time
        self.end_time=end_time
        self.seats=seats or []

class PaymentStrategy(ABC):
    @abstractmethod
    def calculate(self,seat:Seats):
        pass

class UniversalSeatStrategy(PaymentStrategy):
    """Strategy that handles all seat types"""
    def calculate(self,seat:Seats):
        if seat.seat_type == SEAT_TYPE.REGULAR:
            return RATES.REGULAR.value
        elif seat.seat_type == SEAT_TYPE.PREMIUM:
            return RATES.PREMIUM.value
        elif seat.seat_type == SEAT_TYPE.RECLINER:
            return RATES.RECLINER.value
        return 0

class Bookings:
    def __init__(self, user:User,showings:Showings,payment_strategy:PaymentStrategy,seats_ids:list[str], seats:dict[str, Seats]=None):
        self.booking_id=str(uuid.uuid4())
        self.user_id=user.user_id
        self.showing_id=showings.showing_id
        self.is_paid=False
        self.seats_ids=seats_ids
        self.seats=seats or {}  # Dictionary mapping seat_id to Seats object
        self.payment_strategy=payment_strategy
        self.lock=Lock()
        self.confirmed=False
        self.total_price=self.calculate_total_price()
        self.created_at=datetime.now()
    
    def calculate_total_price(self)->float:
        """Calculate total price using payment strategy for all seats"""
        total=0.0
        for seat_id in self.seats_ids:
            if seat_id in self.seats:
                total+=self.payment_strategy.calculate(self.seats[seat_id])
        return total
    
    def confirm_booking(self)->bool:
        """Confirm the booking - keeps seats locked permanently"""
        with self.lock:
            if self.confirmed:
                return False  # Already confirmed
            self.confirmed = True
            self.is_paid = True
            # Seats remain locked after confirmation
            return True
    
    def cancel_booking(self)->bool:
        """Cancel the booking - unlocks all seats"""
        with self.lock:
            if self.confirmed:
                return False  # Cannot cancel confirmed booking
            # Unlock all seats
            for seat_id in self.seats_ids:
                if seat_id in self.seats:
                    self.seats[seat_id].unlock(self.user_id)
            return True
    


class BookingService:
    def __init__(self, lock_duration_seconds:int=300):
        self.bookings=[]
        self.lock=RLock()  # Use RLock for reentrant locking (allows nested lock acquisition)
        self.lock_duration_seconds=lock_duration_seconds  # Default 5 minutes

    def lock_seats(self, user_id:str, seats_ids:list[str], seats:dict[str, Seats])->tuple[bool, list[str]]:
       
        locked_seats = []
        failed_seats = []
        
        for seat_id in seats_ids:
            if seat_id not in seats:
                failed_seats.append(seat_id)
                continue
            
            seat = seats[seat_id]
            if seat.lock(user_id, self.lock_duration_seconds):
                locked_seats.append(seat_id)
            else:
                failed_seats.append(seat_id)
        
        # If any seat failed to lock, unlock all previously locked seats
        if failed_seats:
            for seat_id in locked_seats:
                if seat_id in seats:
                    seats[seat_id].unlock(user_id)
            return (False, failed_seats)
        
        return (True, locked_seats)

    def unlock_seats(self, user_id:str, seats_ids:list[str], seats:dict[str, Seats]):
        """Unlock multiple seats for a user"""
        for seat_id in seats_ids:
            if seat_id in seats:
                seats[seat_id].unlock(user_id)

    def check_seats_availability(self, seats_ids:list[str], seats:dict[str, Seats], user_id:str=None)->tuple[bool, list[str]]:
        """
        Check if seats are available (not locked or locked by the same user)
        Returns (all_available, unavailable_seat_ids)
        """
        unavailable = []
        for seat_id in seats_ids:
            if seat_id not in seats:
                unavailable.append(seat_id)
                continue
            
            seat = seats[seat_id]
            if seat.is_locked():
                # Seat is locked
                if user_id is None or seat.locked_by != user_id:
                    # Locked by another user or checking without user context
                    unavailable.append(seat_id)
        
        return (len(unavailable) == 0, unavailable)

    def create_booking(self,user:User,showings:Showings,payment_strategy:PaymentStrategy,seats_ids:list[str], seats:dict[str, Seats]=None)->tuple[Bookings, str]:
        """
        Create a booking and lock the seats
        Returns (booking, error_message)
        If error_message is not None, booking creation failed
        """
        with self.lock:
            seats = seats or {}
            
            # Check if seats are available
            all_available, unavailable = self.check_seats_availability(seats_ids, seats, user.user_id)
            if not all_available:
                return (None, f"Seats {unavailable} are already locked by another user")
            
            # Lock the seats
            success, failed_seats = self.lock_seats(user.user_id, seats_ids, seats)
            if not success:
                return (None, f"Failed to lock seats {failed_seats}")
            
            try:
                booking=Bookings(user,showings,payment_strategy,seats_ids, seats)
                self.bookings.append(booking)
                return (booking, None)
            except Exception as e:
                # If booking creation fails, unlock the seats
                self.unlock_seats(user.user_id, seats_ids, seats)
                return (None, f"Failed to create booking: {str(e)}")

    def get_booking(self,booking_id:str):
        with self.lock:
            return next((booking for booking in self.bookings if booking.booking_id==booking_id),None)
    
    def confirm_booking(self, booking_id:str, user_id:str)->tuple[bool, str]:
        """
        Confirm a booking
        Returns (success, error_message)
        """
        with self.lock:
            booking = self.get_booking(booking_id)
            if not booking:
                return (False, "Booking not found")
            if booking.user_id != user_id:
                return (False, "Unauthorized: Booking belongs to another user")
            return (booking.confirm_booking(), None)
    
    def cancel_booking(self, booking_id:str, user_id:str)->tuple[bool, str]:
        """
        Cancel a booking and unlock seats
        Returns (success, error_message)
        """
        with self.lock:
            booking = self.get_booking(booking_id)
            if not booking:
                return (False, "Booking not found")
            if booking.user_id != user_id:
                return (False, "Unauthorized: Booking belongs to another user")
            return (booking.cancel_booking(), None)

            
movie=Movie(movie_id='1',movie_name='The Dark Knight')

theater=Theater(theater_id='1',theater_name='Theater 1',location='New York')

showing=Showings(showing_id='1',start_time='2025-01-01 10:00:00',end_time='2025-01-01 12:00:00',movie=movie,theater=theater)

user=User(name='John Doe',email='john.doe@example.com')

payment_strategy=UniversalSeatStrategy()

seats_ids=['1','2','3']

seats={
'1':Seats(seat_id='1',seat_name='A1',seat_type=SEAT_TYPE.REGULAR),
'2':Seats(seat_id='2',seat_name='A2',seat_type=SEAT_TYPE.REGULAR),
'3':Seats(seat_id='3',seat_name='A3',seat_type=SEAT_TYPE.PREMIUM)
}

booking_service=BookingService()

# Test 1: Create booking and lock seats
booking, error = booking_service.create_booking(user,showing,payment_strategy,seats_ids,seats)
if error:
    print(f"Booking failed: {error}")
else:
    print(f"Booking created: {booking.booking_id}")
    print(f"Total price: {booking.total_price}")
    print(f"Booking confirmed: {booking.confirmed}")
    
    # Check seat lock status
    print("\nSeat lock status:")
    for seat_id in seats_ids:
        seat = seats[seat_id]
        if seat.is_locked():
            print(f"  Seat {seat.seat_name} (ID: {seat_id}): LOCKED by {seat.locked_by}")
        else:
            print(f"  Seat {seat.seat_name} (ID: {seat_id}): AVAILABLE")
    
    # Test 2: Try to book same seats with different user (should fail)
    print("\n--- Testing concurrent booking attempt ---")
    user2 = User(name='Jane Doe', email='jane.doe@example.com')
    booking2, error2 = booking_service.create_booking(user2, showing, payment_strategy, seats_ids, seats)
    if error2:
        print(f"Expected failure: {error2}")
    else:
        print(f"Unexpected success: {booking2.booking_id}")
    
    # Test 3: Confirm booking
    print("\n--- Confirming booking ---")
    success, error = booking_service.confirm_booking(booking.booking_id, user.user_id)
    if success:
        print(f"Booking confirmed successfully")
        print(f"Booking confirmed status: {booking.confirmed}")
    else:
        print(f"Confirmation failed: {error}")
    
    # Test 4: Try to cancel confirmed booking (should fail)
    print("\n--- Testing cancel of confirmed booking ---")
    success, error = booking_service.cancel_booking(booking.booking_id, user.user_id)
    if not success:
        print(f"Expected failure: {error}")
    else:
        print("Unexpected: Cancellation succeeded")
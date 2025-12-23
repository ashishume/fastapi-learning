# Requirements:
# - Rider
# - Driver
# - Ride
# - Ride Request
# Services:
# - Ride Services
# - Driver Services
# - Matching Services
# - Pricing Services 

from abc import ABC, abstractmethod
from threading import Lock
from enum import Enum
import uuid

class RIDE_STATUS(Enum):
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    REQUESTED = "REQUESTED"
    ASSIGNED = "ASSIGNED"

class DRIVER_STATUS(Enum):
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    BUSY = "BUSY"   

class Location:
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon



class Rider:
    def __init__(self, user_id: str, active_ride_id: str | None = None):
        self.user_id = user_id
        self.active_ride_id = active_ride_id


class Driver:
    def __init__(self, driver_id: str, driver_name: str, location: Location):
        self.driver_id = driver_id
        self.driver_name = driver_name
        self.location = location
        self.driver_status = DRIVER_STATUS.OFFLINE



class Ride:
    def __init__(
        self,
        ride_id: str,
        rider_id: str,
        pickup: Location,
        dropoff: Location
    ):
        self.id = ride_id
        self.rider_id = rider_id
        self.driver_id = None
        self.source = pickup
        self.destination = dropoff
        self.ride_status = RIDE_STATUS.REQUESTED
        self.fare = 0


def distance(loc1: Location, loc2: Location) -> float:
    """Calculate Manhattan distance between two locations."""
    return abs(loc1.lat - loc2.lat) + abs(loc1.lon - loc2.lon)


class PricingService:
    @staticmethod
    def calculate(distance: float, base_fare: float, rate_per_km: float) -> float:
        return base_fare + (distance * rate_per_km)


class DriverService:
    def __init__(self):
        self.drivers = {}
        self.lock = Lock()

    def add_driver(self, driver: Driver):
        with self.lock:
            self.drivers[driver.driver_id] = driver


    def set_driver_status(self, driver_id: str, status: DRIVER_STATUS):
        with self.lock:
            if driver_id not in self.drivers:
                raise ValueError(f"Driver {driver_id} not found")
            self.drivers[driver_id].driver_status = status


    def update_driver_location(self, driver_id: str, loc: Location):
        with self.lock:
            if driver_id not in self.drivers:
                raise ValueError(f"Driver {driver_id} not found")
            self.drivers[driver_id].location = loc

    def get_available_drivers(self):
        with self.lock:
            return [driver for driver in self.drivers.values() if driver.driver_status == DRIVER_STATUS.ONLINE]


class MatchingService:
    def __init__(self, driver_service: DriverService):
        self.driver_service = driver_service

    def find_nearest_driver(self, pickup_loc: Location) -> Driver | None:
        drivers = self.driver_service.get_available_drivers()
        if not drivers:
            return None
        drivers.sort(key=lambda d: distance(d.location, pickup_loc))
        return drivers[0]  


class RideService:
    def __init__(self, driver_service: DriverService, match_service: MatchingService):
        self.driver_service = driver_service
        self.match_service = match_service
        self.rides: dict[str, Ride] = {}
        self.lock = Lock()

    def request_ride(self, rider: Rider, pickup: Location, dropoff: Location):
        with self.lock:
            if rider.active_ride_id:
                return "Rider already in a ride"

            ride_id = str(uuid.uuid4())
            ride = Ride(ride_id, rider.user_id, pickup, dropoff)

            driver = self.match_service.find_nearest_driver(pickup)
            if not driver:
                return 'drivers not available'

            driver.driver_status = DRIVER_STATUS.BUSY
            ride.driver_id = driver.driver_id
            ride.ride_status = RIDE_STATUS.ASSIGNED

            dist = distance(pickup, dropoff)
            ride.fare = PricingService.calculate(dist, 100, 10)

            self.rides[ride.id] = ride
            rider.active_ride_id = ride.id

            return ride

    def start_ride(self, ride_id: str):
        with self.lock:
            if ride_id not in self.rides:
                raise ValueError(f"Ride {ride_id} not found")
            self.rides[ride_id].ride_status = RIDE_STATUS.STARTED


    def complete_ride(self, ride_id: str, rider: Rider, driver: Driver):
        with self.lock:
            if ride_id not in self.rides:
                raise ValueError(f"Ride {ride_id} not found")
            self.rides[ride_id].ride_status = RIDE_STATUS.COMPLETED
            rider.active_ride_id = None
            self.driver_service.set_driver_status(driver.driver_id, DRIVER_STATUS.ONLINE)

    def cancel_ride(self, ride_id: str, rider: Rider):
        with self.lock:
            if ride_id not in self.rides:
                raise ValueError(f"Ride {ride_id} not found")
            ride = self.rides[ride_id]
            if ride.rider_id != rider.user_id:
                raise ValueError("Rider can only cancel their own ride")
            
            ride.ride_status = RIDE_STATUS.CANCELED
            rider.active_ride_id = None
            
            if ride.driver_id:
                self.driver_service.set_driver_status(ride.driver_id, DRIVER_STATUS.ONLINE)
        
if __name__ == "__main__":
    # Setup driver
    driver = Driver(driver_id="1", driver_name="John", location=Location(lat=10.0, lon=10.0))
    driver_service = DriverService()
    driver_service.add_driver(driver)
    driver_service.set_driver_status(driver.driver_id, DRIVER_STATUS.ONLINE)
    driver_service.update_driver_location(driver.driver_id, Location(lat=10.0, lon=10.0))
    
    # Setup services
    matching_service = MatchingService(driver_service)
    ride_service = RideService(driver_service, matching_service)
    
    # Create rider
    rider = Rider(user_id="1")
    
    # Request a ride
    pickup = Location(lat=10.0, lon=10.0)
    dropoff = Location(lat=20.0, lon=20.0)
    ride = ride_service.request_ride(rider, pickup, dropoff)
    
    if isinstance(ride, str):
        print(f"Error: {ride}")
    else:
        print(f"Ride requested: {ride.id}, Status: {ride.ride_status}, Fare: {ride.fare}")
        
        # Start the ride
        ride_service.start_ride(ride.id)
        print(f"Ride started: {ride.id}")
        
        # Complete the ride
        # Use the same driver instance (we know it's driver_id="1")
        ride_service.complete_ride(ride.id, rider, driver)
        print(f"Ride completed: {ride.id}")
        
        # Uncomment to test cancel ride
        # ride2 = ride_service.request_ride(rider, pickup, dropoff)
        # if isinstance(ride2, str):
        #     print(f"Error: {ride2}")
        # else:
        #     ride_service.cancel_ride(ride2.id, rider)
        #     print(f"Ride canceled: {ride2.id}")
















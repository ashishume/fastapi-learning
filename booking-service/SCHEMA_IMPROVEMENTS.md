# Booking & Seats Schema - Better Approach Analysis

## Current Issues Identified

### 1. **Model-Schema Mismatch** ⚠️

- **Problem**: `Booking` model has `seats_id` as a **single UUID** (one-to-one), but schema expects `List[UUID]` (one-to-many)
- **Location**:
  - Model: `models/bookings.py:39` - `seats_id = Column(UUID(...))`
  - Schema: `schemas/bookings.py:26` - `seats_id: List[UUID]`
- **Impact**: Cannot create bookings with multiple seats

### 2. **Incorrect Relationship Type** ⚠️

- **Problem**: Current relationship is one-to-one (Booking → Seat), but should support one-to-many (Booking → Multiple Seats)
- **Location**: `models/bookings.py:39` and `models/bookings.py:57`
- **Impact**: A booking can only have one seat, which is unrealistic for real-world scenarios

### 3. **Broken Booking Logic** 🐛

- **Lines 22-25**: Logic is inverted - raises error if seat EXISTS (should check if already BOOKED)
- **Lines 27-37**: Creates NEW seats instead of using existing seats (seats should already exist)
- **Line 39**: Tries to compare `List[UUID]` with single `UUID` field
- **Line 56**: Only queries for ONE seat, not multiple
- **Line 71**: Tries to assign `List[UUID]` to single `UUID` field

### 4. **Schema Duplication** 🐛

- **Problem**: `BookingResponse` has duplicate fields (`total_price` and `status` appear twice)
- **Location**: `schemas/bookings.py:27-31`
- **Impact**: Schema validation errors

### 5. **No Proper Seat Availability Tracking** ⚠️

- **Problem**: No clear way to check if a seat is already booked
- **Current approach**: Checks if seat exists, not if it's booked
- **Impact**: Race conditions, double bookings possible

---

## Better Approaches

### **Approach 1: Many-to-Many with Junction Table** ⭐ RECOMMENDED

This is the most flexible and normalized approach.

#### Database Model:

```python
# models/bookings.py
class Booking(Base):
    __tablename__ = "bookings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    movie_id = Column(UUID(as_uuid=True), ForeignKey("movies.id"), nullable=False)
    theater_id = Column(UUID(as_uuid=True), ForeignKey("theaters.id"), nullable=False)
    showing_id = Column(UUID(as_uuid=True), ForeignKey("showings.id"), nullable=False)
    booking_number = Column(String(255), nullable=False, unique=True)
    total_price = Column(Float, nullable=False)
    status = Column(SQLEnum(BookingStatus), nullable=False, default=BookingStatus.PENDING)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    movie = relationship("Movie", back_populates="bookings")
    theater = relationship("Theater", back_populates="bookings")
    showing = relationship("Showing", back_populates="bookings")
    seats = relationship("Seat", secondary="booking_seats", back_populates="bookings")  # Many-to-Many

# New junction table
class BookingSeat(Base):
    __tablename__ = "booking_seats"
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), primary_key=True)
    seat_id = Column(UUID(as_uuid=True), ForeignKey("seats.id"), primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    # Optional: Add seat-specific booking info (e.g., price per seat)
    price = Column(Float, nullable=True)

# models/seats.py
class Seat(Base):
    __tablename__ = "seats"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    showing_id = Column(UUID(as_uuid=True), ForeignKey("showings.id"), nullable=False)
    seat_number = Column(String(255), nullable=False)
    row = Column(String(255), nullable=False)
    column = Column(String(255), nullable=False)
    seat_type = Column(SQLEnum(SeatType), nullable=False, default=SeatType.REGULAR)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    showing = relationship("Showing", back_populates="seats")
    bookings = relationship("Booking", secondary="booking_seats", back_populates="seats")  # Many-to-Many
```

#### Schema:

```python
# schemas/bookings.py
class BookingCreate(BaseModel):
    movie_id: UUID
    theater_id: UUID
    showing_id: UUID
    seat_ids: List[UUID]  # Note: plural 'seat_ids'
    total_price: float

class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    movie_id: UUID
    theater_id: UUID
    showing_id: UUID
    booking_number: str
    total_price: float
    status: BookingStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime

    # Relationships
    movie: Optional[MovieResponse] = None
    theater: Optional[TheaterResponse] = None
    showing: Optional[ShowingResponse] = None
    seats: Optional[List[SeatResponse]] = None  # List of seats
```

#### API Logic:

```python
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_booking(booking: BookingCreate, request: Request, db: Session = Depends(get_db)):
    # 1. Validate showing exists and is not expired
    showing = db.execute(
        select(Showing).where(
            Showing.id == booking.showing_id,
            Showing.expires_at > datetime.datetime.utcnow()
        )
    ).scalar_one_or_none()

    if not showing:
        raise HTTPException(status_code=404, detail="Showing not found or expired")

    # 2. Validate all seats exist and belong to this showing
    seats = db.execute(
        select(Seat).where(
            Seat.id.in_(booking.seat_ids),
            Seat.showing_id == booking.showing_id
        )
    ).scalars().all()

    if len(seats) != len(booking.seat_ids):
        raise HTTPException(status_code=404, detail="One or more seats not found")

    # 3. Check if any seat is already booked (for this showing)
    existing_bookings = db.execute(
        select(BookingSeat).join(Booking).where(
            BookingSeat.seat_id.in_(booking.seat_ids),
            Booking.showing_id == booking.showing_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        )
    ).scalars().all()

    if existing_bookings:
        booked_seat_ids = [b.seat_id for b in existing_bookings]
        raise HTTPException(
            status_code=400,
            detail=f"Seats {booked_seat_ids} are already booked"
        )

    # 4. Create booking
    new_booking = Booking(
        user_id=request.state.user_id,
        movie_id=booking.movie_id,
        theater_id=booking.theater_id,
        showing_id=booking.showing_id,
        booking_number=str(uuid.uuid4()),
        total_price=booking.total_price,
        status=BookingStatus.CONFIRMED
    )
    db.add(new_booking)
    db.flush()  # Get the booking ID

    # 5. Link seats to booking
    for seat in seats:
        booking_seat = BookingSeat(
            booking_id=new_booking.id,
            seat_id=seat.id
        )
        db.add(booking_seat)

    db.commit()
    db.refresh(new_booking)

    return BookingResponse.model_validate(new_booking)
```

**Pros:**

- ✅ Normalized database design
- ✅ Supports multiple seats per booking
- ✅ Easy to query which seats are booked
- ✅ Can track booking history per seat
- ✅ Flexible for future features (e.g., seat-specific pricing)

**Cons:**

- ⚠️ Requires migration to create junction table
- ⚠️ Slightly more complex queries

---

### **Approach 2: One-to-Many with Separate BookingSeat Table**

Similar to Approach 1, but with explicit foreign key from BookingSeat to Booking.

```python
class BookingSeat(Base):
    __tablename__ = "booking_seats"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)
    seat_id = Column(UUID(as_uuid=True), ForeignKey("seats.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    booking = relationship("Booking", back_populates="booking_seats")
    seat = relationship("Seat", back_populates="booking_seats")

class Booking(Base):
    # ... other fields ...
    booking_seats = relationship("BookingSeat", back_populates="booking", cascade="all, delete-orphan")

    @property
    def seats(self):
        return [bs.seat for bs in self.booking_seats]
```

**Pros:**

- ✅ More explicit relationship
- ✅ Can add metadata per booking-seat pair easily

**Cons:**

- ⚠️ Extra table with extra ID column
- ⚠️ Slightly more verbose

---

### **Approach 3: Add `is_booked` Flag to Seat** (Not Recommended)

```python
class Seat(Base):
    # ... existing fields ...
    is_booked = Column(Boolean, nullable=False, default=False)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=True)
```

**Pros:**

- ✅ Simple queries for availability
- ✅ Fast seat availability checks

**Cons:**

- ❌ Cannot track booking history
- ❌ Harder to handle cancellations/refunds
- ❌ Race conditions on concurrent bookings
- ❌ Not normalized (seat can only belong to one booking ever)

---

## Recommended Migration Path

1. **Create junction table** (`booking_seats`)
2. **Update Booking model** - Remove `seats_id`, add many-to-many relationship
3. **Update Seat model** - Change relationship to many-to-many
4. **Fix BookingResponse schema** - Remove duplicates, change `seats` to `List[SeatResponse]`
5. **Update booking API logic** - Proper validation and seat linking
6. **Add database migration** using Alembic

---

## Additional Improvements

### 1. **Add Seat Availability Helper**

```python
def is_seat_available(seat_id: UUID, showing_id: UUID, db: Session) -> bool:
    """Check if a seat is available for booking"""
    existing_booking = db.execute(
        select(BookingSeat).join(Booking).where(
            BookingSeat.seat_id == seat_id,
            Booking.showing_id == showing_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        )
    ).scalar_one_or_none()
    return existing_booking is None
```

### 2. **Add Transaction Support**

Use database transactions to prevent race conditions:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

@router.post("/")
def create_booking(...):
    with db.begin():  # Start transaction
        # All validation and creation in transaction
        # If any step fails, entire transaction rolls back
        pass
```

### 3. **Add Seat Status Enum**

```python
class SeatStatus(str, Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    RESERVED = "reserved"  # For temporary holds
    MAINTENANCE = "maintenance"
```

### 4. **Fix Schema Duplicates**

Remove duplicate fields in `BookingResponse`:

```python
class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    movie_id: UUID
    theater_id: UUID
    showing_id: UUID
    booking_number: str
    total_price: float  # Only once
    status: BookingStatus  # Only once
    created_at: datetime.datetime
    updated_at: datetime.datetime

    movie: Optional[MovieResponse] = None
    theater: Optional[TheaterResponse] = None
    showing: Optional[ShowingResponse] = None
    seats: Optional[List[SeatResponse]] = None  # List, not single
```

---

## Summary

**Best Approach**: Use **Approach 1 (Many-to-Many with Junction Table)** because:

1. ✅ Properly models real-world relationship (bookings have multiple seats)
2. ✅ Normalized database design
3. ✅ Supports booking history
4. ✅ Prevents data inconsistencies
5. ✅ Scalable for future features

The current implementation has fundamental design flaws that prevent it from working correctly with multiple seats. The recommended approach fixes all these issues while maintaining data integrity.

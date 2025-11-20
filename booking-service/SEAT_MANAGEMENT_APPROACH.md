# Seat Management - Better Approach

## Current Problem ❌

**Current Model**: Seats are tied to `showing_id`

- If you have 180 seats and 10 showings, you'd need to create **1,800 seat records** (180 × 10)
- Seats are duplicated for each showing
- Wasteful and doesn't make logical sense (seats are physical entities)

## Better Approach ✅

**Seats belong to Theater** (physical seats), **Bookings link seats to Showings** (availability per showing)

### Architecture:

```
Theater (1) ──→ (M) Seats
  │
  └──→ (M) Showings ──→ (M) Bookings ──→ (M) Seats (through junction table)
```

### Key Changes:

1. **Seats belong to Theater** (not Showing)

   - Create 180 seats **once** per theater
   - Seats are physical entities that don't change

2. **Bookings link Seats to Showings**
   - When booking, you link specific seats to a specific showing
   - Availability is checked through the booking_seats junction table

---

## Updated Model Structure

### 1. Seat Model (Updated)

```python
class Seat(Base):
    __tablename__ = "seats"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    theater_id = Column(UUID(as_uuid=True), ForeignKey("theaters.id"), nullable=False)  # ✅ Changed from showing_id
    seat_number = Column(String(255), nullable=False)  # e.g., "A1", "A2", "P20"
    row = Column(String(255), nullable=False)  # e.g., "A", "B", "P"
    column = Column(String(255), nullable=False)  # e.g., "1", "2", "20"
    seat_type = Column(SQLEnum(SeatType), nullable=False, default=SeatType.REGULAR)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    theater = relationship("Theater", back_populates="seats")
    bookings = relationship("Booking", secondary="booking_seats", back_populates="seats")
```

### 2. Theater Model (Updated)

```python
class Theater(Base):
    __tablename__ = "theaters"
    # ... existing fields ...

    # Relationships
    seats = relationship("Seat", back_populates="theater", cascade="all, delete-orphan")  # ✅ Add this
    showings = relationship("Showing", back_populates="theater")
    bookings = relationship("Booking", back_populates="theater")
```

### 3. Booking Model (Updated - with junction table)

```python
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

# Junction Table
class BookingSeat(Base):
    __tablename__ = "booking_seats"
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), primary_key=True)
    seat_id = Column(UUID(as_uuid=True), ForeignKey("seats.id"), primary_key=True)
    showing_id = Column(UUID(as_uuid=True), ForeignKey("showings.id"), nullable=False)  # For quick availability checks
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
```

### 4. Showing Model (No seats relationship)

```python
class Showing(Base):
    __tablename__ = "showings"
    # ... existing fields ...

    # Relationships
    theater = relationship("Theater", back_populates="showings")
    movie = relationship("Movie", back_populates="showings")
    bookings = relationship("Booking", back_populates="showing")
    # ❌ Remove: seats relationship (seats belong to theater, not showing)
```

---

## Seat Creation Workflow

### Step 1: Create Seats for a Theater (One-time setup)

When you set up a new theater, create all seats **once**:

```python
def create_theater_seats(theater_id: UUID, rows: int = 20, seats_per_row: int = 9, db: Session):
    """
    Create seats for a theater

    Example: 20 rows (A-P), 9 seats per row = 180 seats
    """
    seats = []
    rows_list = [chr(65 + i) for i in range(rows)]  # A, B, C, ..., P

    for row in rows_list:
        for col in range(1, seats_per_row + 1):
            seat = Seat(
                theater_id=theater_id,
                seat_number=f"{row}{col}",  # A1, A2, ..., P9
                row=row,
                column=str(col),
                seat_type=SeatType.REGULAR  # Or determine based on row
            )
            seats.append(seat)

    db.add_all(seats)
    db.commit()
    return seats
```

**Result**: 180 seat records created **once** for the theater.

### Step 2: Query Available Seats for a Showing

When someone wants to see available seats for a showing:

```python
def get_available_seats_for_showing(showing_id: UUID, theater_id: UUID, db: Session):
    """
    Get all available seats for a specific showing
    """
    # Get all seats for this theater
    all_seats = db.execute(
        select(Seat).where(Seat.theater_id == theater_id)
    ).scalars().all()

    # Get booked seats for this showing
    booked_seat_ids = db.execute(
        select(BookingSeat.seat_id).join(Booking).where(
            BookingSeat.showing_id == showing_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        )
    ).scalars().all()

    # Filter available seats
    available_seats = [seat for seat in all_seats if seat.id not in booked_seat_ids]

    return available_seats
```

### Step 3: Create Booking

When someone books seats:

```python
@router.post("/bookings/")
def create_booking(booking: BookingCreate, request: Request, db: Session = Depends(get_db)):
    # 1. Validate showing
    showing = db.execute(
        select(Showing).where(
            Showing.id == booking.showing_id,
            Showing.theater_id == booking.theater_id,
            Showing.expires_at > datetime.datetime.utcnow()
        )
    ).scalar_one_or_none()

    if not showing:
        raise HTTPException(404, "Showing not found or expired")

    # 2. Validate seats belong to this theater
    seats = db.execute(
        select(Seat).where(
            Seat.id.in_(booking.seat_ids),
            Seat.theater_id == booking.theater_id
        )
    ).scalars().all()

    if len(seats) != len(booking.seat_ids):
        raise HTTPException(404, "One or more seats not found in this theater")

    # 3. Check if seats are already booked for this showing
    booked_seats = db.execute(
        select(BookingSeat).join(Booking).where(
            BookingSeat.seat_id.in_(booking.seat_ids),
            BookingSeat.showing_id == booking.showing_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        )
    ).scalars().all()

    if booked_seats:
        raise HTTPException(400, "One or more seats are already booked")

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
    db.flush()

    # 5. Link seats to booking
    for seat in seats:
        booking_seat = BookingSeat(
            booking_id=new_booking.id,
            seat_id=seat.id,
            showing_id=booking.showing_id
        )
        db.add(booking_seat)

    db.commit()
    return BookingResponse.model_validate(new_booking)
```

---

## API Endpoints

### 1. Create Seats for Theater (Admin/Setup)

```python
@router.post("/theaters/{theater_id}/seats/initialize")
def initialize_theater_seats(
    theater_id: UUID,
    rows: int = 20,
    seats_per_row: int = 9,
    db: Session = Depends(get_db)
):
    """Create all seats for a theater (one-time setup)"""
    theater = db.execute(select(Theater).where(Theater.id == theater_id)).scalar_one_or_none()
    if not theater:
        raise HTTPException(404, "Theater not found")

    # Check if seats already exist
    existing_seats = db.execute(select(Seat).where(Seat.theater_id == theater_id)).scalars().all()
    if existing_seats:
        raise HTTPException(400, "Seats already initialized for this theater")

    seats = create_theater_seats(theater_id, rows, seats_per_row, db)
    return {"message": f"Created {len(seats)} seats", "count": len(seats)}
```

### 2. Get Available Seats for Showing

```python
@router.get("/showings/{showing_id}/seats/available")
def get_available_seats(showing_id: UUID, db: Session = Depends(get_db)):
    """Get all available seats for a specific showing"""
    showing = db.execute(select(Showing).where(Showing.id == showing_id)).scalar_one_or_none()
    if not showing:
        raise HTTPException(404, "Showing not found")

    available_seats = get_available_seats_for_showing(showing_id, showing.theater_id, db)
    return [SeatResponse.model_validate(seat) for seat in available_seats]
```

### 3. Get All Seats for Theater (with availability for a showing)

```python
@router.get("/theaters/{theater_id}/seats")
def get_theater_seats(
    theater_id: UUID,
    showing_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """Get all seats for a theater, optionally filtered by availability for a showing"""
    seats = db.execute(
        select(Seat).where(Seat.theater_id == theater_id)
    ).scalars().all()

    if showing_id:
        # Mark which seats are booked
        booked_seat_ids = db.execute(
            select(BookingSeat.seat_id).join(Booking).where(
                BookingSeat.showing_id == showing_id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
            )
        ).scalars().all()

        # Add availability status
        for seat in seats:
            seat.is_available = seat.id not in booked_seat_ids

    return [SeatResponse.model_validate(seat) for seat in seats]
```

---

## Data Flow Example

### Scenario: Theater with 180 seats, 3 showings per day

**Current Approach (WRONG)**:

```
Showing 1 → Create 180 seats
Showing 2 → Create 180 seats
Showing 3 → Create 180 seats
Total: 540 seat records ❌
```

**Better Approach (CORRECT)**:

```
Theater → Create 180 seats (once) ✅

Showing 1 → Book seats A1, A2, A3 (through booking_seats)
Showing 2 → Book seats B1, B2, B3 (through booking_seats)
Showing 3 → Book seats C1, C2, C3 (through booking_seats)

Total: 180 seat records + 9 booking_seat records ✅
```

---

## Benefits

1. ✅ **Efficient**: Create seats once per theater, not per showing
2. ✅ **Logical**: Seats are physical entities that belong to theaters
3. ✅ **Scalable**: Works with any number of showings
4. ✅ **Maintainable**: Update seat info (e.g., type, maintenance) in one place
5. ✅ **Queryable**: Easy to find available seats for any showing

---

## Migration Steps

1. Add `theater_id` to `seats` table
2. Remove `showing_id` from `seats` table (or keep for migration period)
3. Create `booking_seats` junction table
4. Migrate existing data (if any)
5. Update all API endpoints

┌─────────────────────────────────────────────────────────────────────────┐
│ BOOKING SERVICE MODELS │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │    Movie     │
                    │  (movies)    │
                    └──────┬───────┘
                           │
                    showings (1:M)
                    cascade delete
                           │
                           ▼
            ┌──────────────────────────────┐
            │          Showing              │
            │        (showings)             │
            └───┬───────────────────────┬───┘
                │                       │
                │                       │
    bookings (1:M)              booking_seats (1:M)
    cascade delete              cascade delete
                │                       │
                │                       │
                ▼                       │
        ┌──────────────┐               │
        │   Booking    │               │
        │  (bookings)  │               │
        └──────┬───────┘               │
               │                       │
    booking_seats (1:M)                │
    cascade delete                      │
               │                       │
               │                       │
               └───────┬───────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │    BookingSeat        │
            │  (booking_seats)     │
            │  [Junction Table]    │
            └───┬───────────────┬──┘
                │               │
    seat (M:1)  │               │  showing (M:1)
                │               │
                ▼               │
        ┌──────────────┐        │
        │     Seat     │        │
        │   (seats)    │        │
        └──────┬───────┘        │
               │                │
    theater (M:1)               │
               │                │
               │                │
               ▼                │
        ┌──────────────┐        │
        │   Theater    │        │
        │  (theaters)  │        │
        └───┬──────────┘        │
            │                   │
            │                   │
    showings (1:M)              │
    seats (1:M)                 │
    cascade delete              │
            │                   │
            └───────────────────┘
              (both link to Theater)

Relationships Summary:
├─ Movie (1:M) → Showings (cascade delete)
├─ Theater (1:M) → Showings (cascade delete)
├─ Theater (1:M) → Seats (cascade delete)
├─ Showing (1:M) → Bookings (cascade delete)
├─ Showing (1:M) → BookingSeats (cascade delete)
├─ Booking (1:M) → BookingSeats (cascade delete)
├─ Seat (1:M) → BookingSeats (cascade delete)
└─ BookingSeat (M:1) → Booking, Showing, Seat

Legend:
├─► One-to-Many (1:M)
├─► Many-to-One (M:1)
└─► Cascade operations propagate deletes

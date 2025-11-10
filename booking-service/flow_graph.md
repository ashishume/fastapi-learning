┌─────────────────────────────────────────────────────────────────────────┐
│ BOOKING SERVICE MODELS │
└─────────────────────────────────────────────────────────────────────────┘

                            ┌──────────────┐
                            │    Movie     │
                            │  (movies)    │
                            └──────┬───────┘
                                   │
                        ┌──────────┴──────────┐
                        │ showings (1:M)      │ bookings (1:M)
                        │ cascade delete      │ cascade delete
                        ▼                     ▼
            ┌──────────────┐           ┌──────────────┐
            │   Showing    │           │   Booking    │
            │  (showings)  │◄──────────┤  (bookings)  │
            └───┬──────┬───┘  showing  └──┬───────┬───┘
                │      │      (M:1)       │       │
    seats (1:M) │      │ bookings (1:M)   │       │
    cascade del │      │ cascade delete   │       │
                │      │                  │       │
                │      │         ┌────────┘       │
                │      │         │                │
                ▼      │         │                │
        ┌──────────┐  │         │                │
        │   Seat   │  │         │                │
        │ (seats)  │  │         │                │
        └────┬─────┘  │         │                │
             │        │         │                │
             │        │         │                │
    showing  │        │         │                │
     (M:1)   │        │         │ theater (M:1)  │
             │        │         │                │
             │        │         │                │
             │   ┌────▼─────────▼────────┐       │
             │   │      Theater          │       │
             └───┤     (theaters)        │       │
                 └───────────────────────┘       │
                         ▲                       │
                         │                       │
                         └───────────────────────┘
                           seats (1:M), showings (1:M)
                           bookings (1:M), cascade delete

Legend:
├─► One-to-Many (1:M)
├─► Many-to-One (M:1)
└─► Cascade operations propagate deletes

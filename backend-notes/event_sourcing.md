# Event Sourcing in Python

## What is Event Sourcing?

• **Event Sourcing** is a design pattern where the state of an application is determined by a sequence of events
• Instead of storing the current state, you store all events that have occurred
• The current state is reconstructed by replaying events from the beginning
• Events are immutable - once created, they cannot be changed or deleted

## Core Concepts

### Events

• **Immutable records** of something that happened in the system
• Represent facts that occurred at a specific point in time
• Examples: `UserCreated`, `OrderPlaced`, `PaymentProcessed`, `AccountDebited`
• Should be named in past tense (something that already happened)

### Event Store

• **Database** that stores all events in chronological order
• Events are append-only (no updates or deletes)
• Each event typically contains:

- Event ID (unique identifier)
- Event type/name
- Aggregate ID (what entity this event belongs to)
- Timestamp
- Event data/payload
- Version number (for optimistic locking)

### Aggregates

• **Domain entities** that are the source of events
• Represent a consistency boundary
• All events for an aggregate are stored together
• Current state is derived by applying events in sequence

### Snapshots

• **Periodic state captures** to avoid replaying all events
• Store the current state at a point in time
• When loading, start from the latest snapshot and replay events after it
• Reduces load time for aggregates with many events

## Benefits

• **Complete Audit Trail**: Every change is recorded as an event
• **Time Travel**: Can reconstruct state at any point in time
• **Debugging**: Easy to see what happened and when
• **Scalability**: Events can be processed asynchronously
• **Flexibility**: Can create new read models from existing events
• **Compliance**: Meets requirements for financial/healthcare systems
• **Event Replay**: Can reprocess events for new features or bug fixes

## Challenges

• **Eventual Consistency**: Read models may be slightly behind
• **Storage Growth**: Events accumulate over time (need retention policies)
• **Complexity**: More complex than traditional CRUD
• **Performance**: Replaying many events can be slow (mitigated by snapshots)
• **Schema Evolution**: Events may change over time (need versioning)
• **Debugging**: Can be harder to understand current state without tooling

## Implementation in Python

### Basic Event Structure

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from uuid import UUID

@dataclass
class Event:
    event_id: UUID
    aggregate_id: UUID
    event_type: str
    event_data: Dict[str, Any]
    timestamp: datetime
    version: int
```

### Event Store Interface

```python
from abc import ABC, abstractmethod
from typing import List

class EventStore(ABC):
    @abstractmethod
    def save_events(self, aggregate_id: UUID, events: List[Event], expected_version: int):
        """Save events for an aggregate with optimistic locking"""
        pass

    @abstractmethod
    def get_events(self, aggregate_id: UUID, from_version: int = 0) -> List[Event]:
        """Retrieve all events for an aggregate"""
        pass
```

### Aggregate Base Class

```python
class Aggregate:
    def __init__(self, aggregate_id: UUID):
        self.aggregate_id = aggregate_id
        self.version = 0
        self._uncommitted_events = []

    def apply_event(self, event: Event):
        """Apply event to change state"""
        handler = getattr(self, f"handle_{event.event_type}", None)
        if handler:
            handler(event.event_data)
        self.version += 1

    def raise_event(self, event_type: str, event_data: Dict[str, Any]):
        """Create and store a new event"""
        event = Event(
            event_id=UUID(),
            aggregate_id=self.aggregate_id,
            event_type=event_type,
            event_data=event_data,
            timestamp=datetime.now(),
            version=self.version + 1
        )
        self.apply_event(event)
        self._uncommitted_events.append(event)

    def get_uncommitted_events(self) -> List[Event]:
        """Get events that haven't been persisted"""
        return self._uncommitted_events

    def mark_events_as_committed(self):
        """Clear uncommitted events after persistence"""
        self._uncommitted_events = []
```

### Example: Bank Account Aggregate

```python
class BankAccount(Aggregate):
    def __init__(self, aggregate_id: UUID, account_number: str):
        super().__init__(aggregate_id)
        self.account_number = account_number
        self.balance = 0.0
        self.is_closed = False

    def open_account(self, initial_deposit: float):
        if self.version > 0:
            raise ValueError("Account already exists")
        self.raise_event("AccountOpened", {
            "account_number": self.account_number,
            "initial_deposit": initial_deposit
        })

    def handle_AccountOpened(self, event_data: Dict):
        self.balance = event_data["initial_deposit"]

    def deposit(self, amount: float):
        if self.is_closed:
            raise ValueError("Cannot deposit to closed account")
        self.raise_event("MoneyDeposited", {"amount": amount})

    def handle_MoneyDeposited(self, event_data: Dict):
        self.balance += event_data["amount"]

    def withdraw(self, amount: float):
        if self.is_closed:
            raise ValueError("Cannot withdraw from closed account")
        if self.balance < amount:
            raise ValueError("Insufficient funds")
        self.raise_event("MoneyWithdrawn", {"amount": amount})

    def handle_MoneyWithdrawn(self, event_data: Dict):
        self.balance -= event_data["amount"]

    def close_account(self):
        if self.is_closed:
            raise ValueError("Account already closed")
        self.raise_event("AccountClosed", {})

    def handle_AccountClosed(self, event_data: Dict):
        self.is_closed = True
```

### Repository Pattern

```python
class Repository:
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self._cache = {}  # In-memory cache for loaded aggregates

    def save(self, aggregate: Aggregate):
        """Save aggregate by persisting its uncommitted events"""
        events = aggregate.get_uncommitted_events()
        if events:
            self.event_store.save_events(
                aggregate.aggregate_id,
                events,
                aggregate.version - len(events)
            )
            aggregate.mark_events_as_committed()
            self._cache[aggregate.aggregate_id] = aggregate

    def get(self, aggregate_id: UUID, aggregate_class) -> Aggregate:
        """Load aggregate by replaying all events"""
        # Check cache first
        if aggregate_id in self._cache:
            return self._cache[aggregate_id]

        # Load events from store
        events = self.event_store.get_events(aggregate_id)

        # Create aggregate and replay events
        aggregate = aggregate_class(aggregate_id)
        for event in events:
            aggregate.apply_event(event)

        self._cache[aggregate_id] = aggregate
        return aggregate
```

## Python Libraries for Event Sourcing

### EventStore (Python Client)

• Official client for EventStore DB
• Provides async/await support
• Built-in connection pooling
• Example: `pip install eventstore`

### Eventsourcing

• Full-featured event sourcing library
• Includes event store, snapshots, projections
• Supports PostgreSQL, SQLite, DynamoDB
• Example: `pip install eventsourcing`

### AggregateRoot (Custom)

• Can build your own using dataclasses and ABC
• More control but more work
• Good for learning the concepts

## CQRS (Command Query Responsibility Segregation)

• **Often used with Event Sourcing**
• Separates read and write operations
• **Commands**: Change state (write side) - use event sourcing
• **Queries**: Read data (read side) - use optimized read models
• Read models are updated by processing events
• Allows independent scaling of read/write operations

### CQRS with Event Sourcing Flow

1. **Command** arrives → Aggregate processes it → Events generated
2. Events saved to **Event Store**
3. Events published to **Event Bus**
4. **Projections** (read model updaters) consume events
5. **Read Models** updated asynchronously
6. **Queries** read from optimized read models

## Best Practices

• **Event Versioning**: Always version your events for schema evolution
• **Idempotency**: Ensure event handlers are idempotent (safe to replay)
• **Event Naming**: Use clear, past-tense names (`OrderShipped` not `ShipOrder`)
• **Snapshot Strategy**: Create snapshots periodically (every N events or time interval)
• **Event Size**: Keep events small; store references to large data
• **Optimistic Locking**: Use version numbers to prevent concurrent modification
• **Event Validation**: Validate events before storing
• **Error Handling**: Have strategies for handling failed event processing
• **Monitoring**: Track event processing metrics and lag

## Use Cases

• **Financial Systems**: Banking, trading, accounting (audit requirements)
• **E-commerce**: Order processing, inventory management
• **Healthcare**: Patient records, treatment history
• **IoT Systems**: Sensor data, device state changes
• **Collaboration Tools**: Document editing, version control
• **Gaming**: Player actions, game state
• **Compliance-Heavy Industries**: Where audit trails are mandatory

## Event Schema Evolution

• **Additive Changes**: Add new optional fields (backward compatible)
• **Versioning**: Use event version numbers for breaking changes
• **Upcasters**: Transform old event versions to new format
• **Deprecation**: Mark old event types as deprecated, don't delete

```python
# Example: Versioned Event
@dataclass
class EventV1:
    user_id: UUID
    email: str

@dataclass
class EventV2:
    user_id: UUID
    email: str
    phone: str  # New field

def upcast_v1_to_v2(event_v1: EventV1) -> EventV2:
    return EventV2(
        user_id=event_v1.user_id,
        email=event_v1.email,
        phone=""  # Default value
    )
```

## Performance Optimization

• **Snapshots**: Reduce replay time for aggregates with many events
• **Event Streaming**: Use Kafka/RabbitMQ for high-throughput scenarios
• **Read Models**: Pre-compute queries instead of replaying events
• **Caching**: Cache frequently accessed aggregates
• **Partitioning**: Partition events by aggregate ID for parallel processing
• **Compression**: Compress old events that are rarely accessed

## Testing Event Sourcing

• **Unit Tests**: Test aggregate behavior by applying events
• **Integration Tests**: Test event store persistence and retrieval
• **Replay Tests**: Verify events can be replayed correctly
• **Snapshot Tests**: Ensure snapshots work correctly
• **Event Handler Tests**: Test that event handlers produce correct state changes

## Common Patterns

### Event Sourcing + CQRS

• Write side uses event sourcing
• Read side uses optimized databases (PostgreSQL, MongoDB, Elasticsearch)
• Events bridge the two sides

### Event Sourcing + Message Queue

• Events published to message queue (Kafka, RabbitMQ)
• Multiple consumers process events for different purposes
• Enables microservices communication

### Event Sourcing + Snapshots

• Periodic snapshots for performance
• Load from snapshot + replay recent events
• Balance between storage and performance

## When NOT to Use Event Sourcing

• **Simple CRUD applications** with no audit requirements
• **High write throughput** with no need for history
• **Small teams** without event sourcing expertise
• **Simple domains** where traditional approach is sufficient
• **Real-time consistency** requirements (event sourcing is eventually consistent)

## Example: Complete Implementation

```python
# Simple in-memory event store
class InMemoryEventStore(EventStore):
    def __init__(self):
        self._events = {}  # aggregate_id -> List[Event]

    def save_events(self, aggregate_id: UUID, events: List[Event], expected_version: int):
        existing = self._events.get(aggregate_id, [])
        if len(existing) != expected_version:
            raise ValueError("Concurrent modification detected")
        self._events[aggregate_id] = existing + events

    def get_events(self, aggregate_id: UUID, from_version: int = 0) -> List[Event]:
        events = self._events.get(aggregate_id, [])
        return events[from_version:]

# Usage
event_store = InMemoryEventStore()
repository = Repository(event_store)

# Create account
account_id = UUID()
account = BankAccount(account_id, "ACC-001")
account.open_account(1000.0)
repository.save(account)

# Load and modify
account = repository.get(account_id, BankAccount)
account.deposit(500.0)
account.withdraw(200.0)
repository.save(account)

# Replay all events to get current state
account = repository.get(account_id, BankAccount)
print(f"Balance: {account.balance}")  # 1300.0
```

## Resources

• **Greg Young**: Original proponent of Event Sourcing
• **Martin Fowler**: Articles on Event Sourcing and CQRS
• **EventStore**: Open-source event store database
• **Eventsourcing Python Library**: Full implementation
• **Domain-Driven Design**: Event Sourcing fits well with DDD

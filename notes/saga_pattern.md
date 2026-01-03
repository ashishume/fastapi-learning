# Saga Pattern in Distributed Systems

## What is the Saga Pattern?

• Design pattern for managing distributed transactions across microservices
• Breaks transaction into series of local transactions (one per service)
• If any step fails, compensating actions (rollbacks) undo completed steps
• Eventually consistent (not immediately consistent like ACID)

## The Problem It Solves

**Traditional ACID transactions don't work across services:**

- Each service has its own database
- Distributed transactions (2PC/3PC) have performance/availability issues
- Services need coordination without tight coupling

**Example: E-commerce Order Processing**

1. Create order → 2. Reserve inventory → 3. Process payment → 4. Send notification

If payment fails, need to: cancel order, release inventory, notify user → **Saga handles this!**

## Core Concepts

### Saga Transaction

Sequence of local transactions that form a distributed transaction. Each:

- Updates data in one service
- Publishes event/message
- Can be compensated if needed

### Compensating Actions

- Operations that undo effects of completed local transactions
- Not exact inverse (e.g., marking order as cancelled vs deleting it)
- Must be **idempotent** (safe to execute multiple times)

## Two Orchestration Styles

### 1. Choreography-Based (Event-Driven)

- Services communicate through events
- No central coordinator
- Decentralized, loosely coupled

**Flow:**

```
Order Service → OrderCreated event
    ↓
Inventory Service (listens) → ReserveInventory → InventoryReserved event
    ↓
Payment Service (listens) → ProcessPayment → PaymentProcessed event
```

**On failure:**

```
Payment Service → PaymentFailed event
    ↓
Inventory Service → ReleaseInventory (compensate)
    ↓
Order Service → CancelOrder (compensate)
```

### 2. Orchestration-Based (Centralized)

- Central orchestrator coordinates saga
- Orchestrator tells each service what to do
- More control, easier to understand/debug

**Flow:**

```
Orchestrator → Order Service: CreateOrder()
Orchestrator → Inventory Service: ReserveInventory()
Orchestrator → Payment Service: ProcessPayment()
```

**On failure:**

```
Orchestrator → Payment Service: RefundPayment() (compensate)
Orchestrator → Inventory Service: ReleaseInventory() (compensate)
Orchestrator → Order Service: CancelOrder() (compensate)
```

## Comparison

| Aspect         | Choreography          | Orchestration         |
| -------------- | --------------------- | --------------------- |
| **Coupling**   | Loose                 | Tighter               |
| **Complexity** | Distributed logic     | Centralized logic     |
| **Debugging**  | Harder (trace events) | Easier (single place) |
| **Use Case**   | Simple workflows      | Complex workflows     |

## Code Example: Orchestration-Based Saga

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Callable
import uuid

class SagaStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class SagaStep:
    step_id: str
    service_name: str
    action: Callable
    compensate: Callable
    status: SagaStatus = SagaStatus.PENDING

class SagaOrchestrator:
    def __init__(self):
        self.sagas = {}

    def execute_saga(self, saga_id: str, steps: List[SagaStep]):
        saga = self.sagas.get(saga_id)
        completed_steps = []

        for step in steps:
            try:
                # Execute step
                step.status = SagaStatus.IN_PROGRESS
                result = step.action()
                step.status = SagaStatus.COMPLETED
                completed_steps.append(step)
            except Exception as e:
                # Compensate in reverse order
                self._compensate(completed_steps, str(e))
                return

        saga.status = SagaStatus.COMPLETED

    def _compensate(self, completed_steps: List[SagaStep], error: str):
        # Compensate in reverse order
        for step in reversed(completed_steps):
            try:
                step.compensate()
            except Exception as e:
                # Log compensation failure
                print(f"Compensation failed for {step.service_name}: {e}")

# Services
class OrderService:
    def create_order(self, order_data: dict):
        print(f"Creating order: {order_data}")
        return {"order_id": str(uuid.uuid4())}

    def cancel_order(self, order_id: str):
        print(f"Cancelling order: {order_id}")

class InventoryService:
    def reserve_inventory(self, product_id: str, quantity: int):
        print(f"Reserving {quantity} units of {product_id}")
        return {"reservation_id": str(uuid.uuid4())}

    def release_inventory(self, reservation_id: str):
        print(f"Releasing inventory: {reservation_id}")

class PaymentService:
    def process_payment(self, amount: float):
        print(f"Processing payment: {amount}")
        return {"payment_id": str(uuid.uuid4())}

    def refund_payment(self, payment_id: str):
        print(f"Refunding payment: {payment_id}")

# Usage
orchestrator = SagaOrchestrator()
order_service = OrderService()
inventory_service = InventoryService()
payment_service = PaymentService()

saga_id = str(uuid.uuid4())
order_data = {"user_id": "user123", "items": [{"product_id": "prod1", "quantity": 2}]}

steps = [
    SagaStep("1", "order",
             lambda: order_service.create_order(order_data),
             lambda: order_service.cancel_order(order_data.get("order_id", ""))),
    SagaStep("2", "inventory",
             lambda: inventory_service.reserve_inventory("prod1", 2),
             lambda: inventory_service.release_inventory("reservation_id")),
    SagaStep("3", "payment",
             lambda: payment_service.process_payment(100.0),
             lambda: payment_service.refund_payment("payment_id"))
]

orchestrator.execute_saga(saga_id, steps)
```

## Best Practices

### 1. Idempotency

All saga steps and compensating actions must be idempotent:

```python
def process_payment(payment_id: str, amount: float):
    existing = get_payment(payment_id)
    if existing and existing.status == "completed":
        return existing  # Idempotent
    return create_payment(payment_id, amount)
```

### 2. Saga State Management

- Store saga state in database
- Track completed steps
- Enable recovery after crashes

### 3. Timeout Handling

- Set timeouts for each step
- Trigger compensation on timeout
- Prevent sagas from hanging

### 4. Eventual Consistency

- Accept temporary inconsistency
- Use version numbers/timestamps
- Implement conflict resolution

### 5. Monitoring

- Log all saga events
- Track duration and success rates
- Alert on compensation frequency

## Saga vs Two-Phase Commit (2PC)

| Aspect           | Saga                             | 2PC                                    |
| ---------------- | -------------------------------- | -------------------------------------- |
| **Consistency**  | Eventually consistent            | Immediately consistent                 |
| **Performance**  | Better (no blocking)             | Worse (blocks resources)               |
| **Availability** | High                             | Lower (coordinator SPOF)               |
| **Use Case**     | Microservices, long transactions | Short transactions, strong consistency |

## Common Use Cases

1. **E-commerce**: Create order → Reserve inventory → Process payment → Ship
2. **Hotel Booking**: Book room → Charge payment → Send confirmation
3. **Travel**: Book flight → Book hotel → Book car rental
4. **Payment**: Debit account → Credit merchant → Update ledger
5. **Food Delivery**: Create order → Reserve restaurant → Assign driver → Process payment

## Challenges & Solutions

### Challenge 1: Partial Failures

**Problem**: Compensation itself fails  
**Solution**: Retry mechanisms, dead letter queues, manual intervention

### Challenge 2: Long-Running Sagas

**Problem**: Sagas taking hours/days  
**Solution**: Break into sub-sagas, use timeouts/checkpoints, store state persistently

### Challenge 3: Concurrent Sagas

**Problem**: Multiple sagas modifying same resource  
**Solution**: Optimistic locking (version numbers), conflict resolution, distributed locks

## Interview Q&A

### Q: What is the Saga pattern and when would you use it?

**A**: Saga pattern manages distributed transactions across microservices by breaking them into local transactions with compensating actions. Use when:

- Building microservices with distributed transactions
- Need to coordinate multiple services
- Can accept eventual consistency
- Services have their own databases

### Q: What's the difference between choreography and orchestration?

**A**:

- **Choreography**: Services communicate via events, no central coordinator, loosely coupled
- **Orchestration**: Central orchestrator coordinates all steps, more control, easier to debug

Choose choreography for simple workflows, orchestration for complex ones.

### Q: How do you handle failures in a saga?

**A**:

1. When a step fails, execute compensating actions in reverse order of completed steps
2. Compensating actions must be idempotent
3. Store saga state to enable recovery
4. Use timeouts to prevent hanging sagas

### Q: What makes compensating actions different from rollbacks?

**A**: Compensating actions restore system to consistent state but aren't exact inverse:

- Rollback: Delete created record
- Compensate: Mark order as cancelled (preserves audit trail)

### Q: How do you ensure idempotency in saga steps?

**A**:

- Use unique IDs for operations
- Check if operation already completed before executing
- Return existing result if already processed
- Store operation state in database

### Q: What are the trade-offs of using Saga vs 2PC?

**A**:

- **Saga**: Eventually consistent, better performance/availability, but more complex (compensation logic)
- **2PC**: Immediately consistent, simpler conceptually, but blocks resources and has single point of failure

## When to Use

✅ **Use When:**

- Microservices with distributed transactions
- Can accept eventual consistency
- Long-running business processes
- Services have independent databases

❌ **Don't Use When:**

- Simple CRUD within single service
- Need immediate consistency (use 2PC)
- Can't implement proper compensation
- Very short transactions (overhead not worth it)

## Key Takeaways

✅ Saga breaks distributed transactions into local transactions with compensation  
✅ Two styles: Choreography (event-driven) vs Orchestration (centralized)  
✅ Compensating actions must be idempotent  
✅ Eventually consistent (not immediately consistent)  
✅ Use for microservices, long transactions, eventual consistency acceptable  
✅ Store saga state for recovery

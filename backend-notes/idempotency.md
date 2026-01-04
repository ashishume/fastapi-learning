# Idempotency in Distributed Systems

## What is Idempotency?

• Performing the same operation multiple times produces the same result as performing it once
• Critical for handling network failures, retries, and duplicate messages in distributed systems
• Without it: duplicate charges, multiple orders, data corruption

## Why It Matters

**Problem**: Network timeouts, automatic retries, duplicate messages, and race conditions can cause operations to execute multiple times.

**Solution**: Make operations idempotent so retries are safe.

```
Without idempotency:
Client → "Charge $100" → Timeout → Retry → "Charge $100" → User charged twice! ❌

With idempotency:
Client → "Charge $100" (key: abc123) → Timeout → Retry → "Charge $100" (key: abc123)
→ Service recognizes duplicate → Returns same result → User charged once! ✅
```

## HTTP Methods

**Idempotent**: GET, PUT, DELETE, HEAD  
**Not Idempotent**: POST, PATCH (require explicit implementation)

## Implementation Strategies

### 1. Idempotency Keys

- Client sends unique key with request (`Idempotency-Key` header)
- Server checks cache: if exists → return cached response, else → process & cache

### 2. Natural Idempotency

- Use SET operations: `SET status = 'paid'` ✅ vs `INCREMENT balance` ❌
- Use UPSERT with unique constraints
- Conditional updates based on current state

### 3. Database Unique Constraints

- Store idempotency key as unique column
- Handle `IntegrityError` to return existing record

## Code Examples

### Example 1: Payment Service with Idempotency Key

```python
from fastapi import FastAPI, Header
from typing import Optional
import redis
import json
import uuid
from datetime import timedelta

app = FastAPI()
redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.post("/payments/charge")
async def charge_payment(
    request: PaymentRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    if not idempotency_key:
        idempotency_key = str(uuid.uuid4())

    # Check cache
    cached = redis_client.get(f"idempotency:{idempotency_key}")
    if cached:
        return json.loads(cached)

    # Process payment
    payment_id = str(uuid.uuid4())
    result = {
        "payment_id": payment_id,
        "status": "completed",
        "amount": request.amount
    }

    # Cache for 24 hours
    redis_client.setex(
        f"idempotency:{idempotency_key}",
        timedelta(hours=24),
        json.dumps(result)
    )

    return result
```

### Example 2: Database-Level Idempotency

```python
from sqlalchemy import Column, String, Float, UniqueConstraint
from sqlalchemy.exc import IntegrityError

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(UUID, primary_key=True)
    idempotency_key = Column(String(255), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)

def create_payment(session, idempotency_key: str, amount: float):
    try:
        payment = Payment(idempotency_key=idempotency_key, amount=amount, status='completed')
        session.add(payment)
        session.commit()
        return payment
    except IntegrityError:
        # Key exists - return existing
        session.rollback()
        return session.query(Payment).filter_by(idempotency_key=idempotency_key).first()
```

### Example 3: Natural Idempotency

```python
# NOT Idempotent ❌
def update_balance(user_id: str, amount: float):
    user.balance += amount  # Adds every time!

# Idempotent ✅
def set_balance(user_id: str, balance: float):
    user.balance = balance  # Same result every time

# Idempotent with check ✅
def add_balance_if_new(user_id: str, transaction_id: str, amount: float):
    if transaction_exists(transaction_id):
        return get_transaction(transaction_id)
    user.balance += amount
    save_transaction(transaction_id, amount)
```

## Best Practices

1. **Use idempotency keys** for critical operations (payments, orders, account updates)
2. **Client generates key** (UUID recommended): `idempotency_key = str(uuid.uuid4())`
3. **Store in shared cache** (Redis with TTL) - not in-memory
4. **Cache entire response** with appropriate TTL (24 hours for payments)
5. **Handle race conditions** with database unique constraints or distributed locks
6. **Don't cache errors** (except 4xx with short TTL)

## Common Patterns

### Idempotency Middleware

```python
class IdempotencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        idempotency_key = request.headers.get("Idempotency-Key")

        if idempotency_key and request.method in ["POST", "PATCH"]:
            cached = redis_client.get(f"idempotency:{idempotency_key}")
            if cached:
                return Response(content=cached, status_code=200)

        response = await call_next(request)

        if idempotency_key and response.status_code < 400:
            redis_client.setex(f"idempotency:{idempotency_key}", 86400, response.body)

        return response
```

### Idempotent Decorator

```python
def idempotent(key_func=None, ttl=86400):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = key_func(*args, **kwargs) if key_func else generate_key(func, args, kwargs)

            cached = redis_client.get(f"idempotency:{key}")
            if cached:
                return json.loads(cached)

            result = func(*args, **kwargs)
            redis_client.setex(f"idempotency:{key}", ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

# Usage
@idempotent(key_func=lambda user_id, amount: f"payment:{user_id}:{amount}")
def process_payment(user_id: str, amount: float):
    return {"status": "success", "payment_id": "123"}
```

## Interview Q&A

### Q: What is idempotency and why is it important?

**A**: Idempotency means an operation can be safely retried with the same result. Critical because:

- Network failures cause retries
- Message queues deliver duplicates
- Race conditions cause duplicate operations

Without it: users charged twice, duplicate orders, data corruption.

### Q: How do you implement idempotency in a payment service?

**A**:

1. Client sends unique `Idempotency-Key` header
2. Server checks Redis cache for key
3. If exists → return cached response
4. If not → process payment, cache result with TTL (24h), return result

```python
if redis.exists(f"idempotency:{key}"):
    return cached_response
result = process_payment()
redis.setex(f"idempotency:{key}", 86400, result)
return result
```

### Q: How do you handle simultaneous requests with the same idempotency key?

**A**: Race condition! Solutions:

1. **Database unique constraint** - second insert fails, return existing
2. **Distributed lock** - Redis lock to serialize processing
3. **Optimistic locking** - check-and-set operations

```python
try:
    payment = create_payment(idempotency_key, ...)
except IntegrityError:
    payment = get_existing_payment(idempotency_key)
```

### Q: Should you cache error responses?

**A**: Generally no - errors might be transient. Exception: cache 4xx errors with short TTL since they won't succeed on retry.

### Q: How long to store idempotency keys?

**A**:

- Payments: 24-72 hours
- Orders: 7-30 days
- General APIs: 24 hours

Consider retry windows, business requirements, and storage costs.

## Key Takeaways

✅ Use idempotency keys for POST/PATCH operations  
✅ Store in shared cache (Redis) with TTL  
✅ Handle race conditions with unique constraints or locks  
✅ Design naturally idempotent operations when possible (SET vs INCREMENT)  
✅ Test by sending duplicate requests

# Circuit Breaker Pattern in Distributed Systems

## What is the Circuit Breaker Pattern?

• **Circuit Breaker** is a design pattern that prevents cascading failures in distributed systems
• Acts as a safety mechanism that stops calling a failing service after a threshold of failures
• Provides fast failure responses instead of waiting for timeouts
• Automatically attempts to recover after a cooldown period
• Named after electrical circuit breakers that protect electrical systems from overload

## The Problem It Solves

**Without Circuit Breaker:**
- Service A calls Service B repeatedly
- Service B is down or slow
- Service A waits for timeouts (30s each)
- Service A's threads/resources get exhausted
- Service A becomes unresponsive
- Cascading failure spreads to other services

**With Circuit Breaker:**
- Service A calls Service B
- After N failures, circuit opens
- Subsequent calls fail immediately (no timeout wait)
- Service A stays responsive
- Circuit attempts recovery after cooldown
- Prevents cascading failures

## Circuit Breaker States

### 1. CLOSED (Normal Operation)
- Requests flow through normally
- Monitors failure rate
- Transitions to OPEN when failure threshold exceeded

### 2. OPEN (Failing Fast)
- All requests fail immediately (no actual call made)
- Returns error immediately or cached response
- Prevents further load on failing service
- Transitions to HALF_OPEN after timeout period

### 3. HALF_OPEN (Testing Recovery)
- Allows limited requests to test if service recovered
- If successful → transitions to CLOSED
- If failed → transitions back to OPEN
- Usually allows 1-3 test requests

## Core Concepts

### Failure Threshold
- Number of consecutive failures before opening circuit
- Example: Open circuit after 5 consecutive failures

### Timeout/Cooldown Period
- How long circuit stays OPEN before attempting recovery
- Example: Wait 60 seconds before trying HALF_OPEN

### Success Threshold (Half-Open)
- Number of successful calls needed to close circuit
- Example: Close circuit after 2 successful calls in HALF_OPEN

### Failure Rate
- Percentage of failed requests over time window
- Example: Open circuit if >50% failures in last 60 seconds

## Implementation in Python

### Basic Circuit Breaker Class

```python
from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, Any, Optional
import threading
import time

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.success_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time: Optional[datetime] = None
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self.lock:
            # Check if circuit should transition from OPEN to HALF_OPEN
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise CircuitBreakerOpenError("Circuit breaker is OPEN")
            
            # Attempt the call
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        else:
            # Reset failure count on success in CLOSED state
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            # Failed in half-open, go back to open
            self.state = CircuitState.OPEN
            self.success_count = 0
        elif self.failure_count >= self.failure_threshold:
            # Too many failures, open the circuit
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.timeout
    
    def get_state(self) -> CircuitState:
        """Get current circuit breaker state"""
        return self.state
    
    def reset(self):
        """Manually reset circuit breaker to CLOSED state"""
        with self.lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is OPEN"""
    pass
```

### Usage Example

```python
import requests
from circuit_breaker import CircuitBreaker, CircuitBreakerOpenError

# Create circuit breaker for external API
api_breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=60,
    success_threshold=2,
    expected_exception=requests.RequestException
)

def call_external_api(url: str) -> dict:
    """Call external API with circuit breaker"""
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()

# Use circuit breaker
try:
    result = api_breaker.call(call_external_api, "https://api.example.com/data")
    print(f"Success: {result}")
except CircuitBreakerOpenError:
    print("Circuit breaker is OPEN - service unavailable")
except requests.RequestException as e:
    print(f"API call failed: {e}")
```

### Decorator Pattern

```python
from functools import wraps
from typing import Dict

class CircuitBreakerManager:
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
    
    def get_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """Get or create circuit breaker for a service"""
        if name not in self.breakers:
            self.breakers[name] = CircuitBreaker(**kwargs)
        return self.breakers[name]
    
    def circuit_breaker(self, name: str, **breaker_kwargs):
        """Decorator to add circuit breaker to a function"""
        def decorator(func):
            breaker = self.get_breaker(name, **breaker_kwargs)
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                return breaker.call(func, *args, **kwargs)
            
            return wrapper
        return decorator

# Global manager
breaker_manager = CircuitBreakerManager()

# Usage
@breaker_manager.circuit_breaker("payment_service", failure_threshold=5, timeout=60)
def process_payment(amount: float):
    # Call payment service
    response = requests.post("http://payment-service/charge", json={"amount": amount})
    response.raise_for_status()
    return response.json()
```

### Async Circuit Breaker

```python
import asyncio
from datetime import datetime, timedelta
from typing import Callable, Any, Optional
from enum import Enum

class AsyncCircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.success_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time: Optional[datetime] = None
        self.lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection"""
        async with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise CircuitBreakerOpenError("Circuit breaker is OPEN")
            
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise
    
    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        else:
            self.failure_count = 0
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.success_count = 0
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return True
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.timeout
```

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()

# Create circuit breaker for external service
external_api_breaker = AsyncCircuitBreaker(
    failure_threshold=5,
    timeout=60,
    success_threshold=2,
    expected_exception=httpx.HTTPError
)

async def call_external_service(url: str) -> dict:
    """Call external service with circuit breaker"""
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

@app.get("/data")
async def get_data():
    """Endpoint that uses circuit breaker"""
    try:
        data = await external_api_breaker.call(
            call_external_service,
            "https://external-api.example.com/data"
        )
        return {"status": "success", "data": data}
    except CircuitBreakerOpenError:
        # Circuit is open - return cached data or error
        return JSONResponse(
            status_code=503,
            content={
                "status": "service_unavailable",
                "message": "External service is temporarily unavailable",
                "circuit_state": "open"
            }
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"External service error: {str(e)}")
```

## Advanced Features

### Time Window Based Failure Rate

```python
from collections import deque
from datetime import datetime, timedelta

class TimeWindowCircuitBreaker:
    def __init__(
        self,
        failure_rate_threshold: float = 0.5,  # 50% failure rate
        time_window: int = 60,  # 60 seconds
        min_requests: int = 10,  # Minimum requests to evaluate
        timeout: int = 60
    ):
        self.failure_rate_threshold = failure_rate_threshold
        self.time_window = time_window
        self.min_requests = min_requests
        self.timeout = timeout
        
        self.requests = deque()  # (timestamp, success)
        self.state = CircuitState.CLOSED
        self.last_failure_time: Optional[datetime] = None
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        with self.lock:
            # Clean old requests outside time window
            self._clean_old_requests()
            
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise CircuitBreakerOpenError("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                self.requests.append((datetime.now(), True))
                self._on_success()
                return result
            except Exception as e:
                self.requests.append((datetime.now(), False))
                self._on_failure()
                raise
    
    def _clean_old_requests(self):
        """Remove requests outside time window"""
        cutoff = datetime.now() - timedelta(seconds=self.time_window)
        while self.requests and self.requests[0][0] < cutoff:
            self.requests.popleft()
    
    def _calculate_failure_rate(self) -> float:
        """Calculate failure rate in time window"""
        if len(self.requests) < self.min_requests:
            return 0.0
        
        failures = sum(1 for _, success in self.requests if not success)
        return failures / len(self.requests)
    
    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
        elif self.state == CircuitState.CLOSED:
            failure_rate = self._calculate_failure_rate()
            if failure_rate >= self.failure_rate_threshold:
                self.state = CircuitState.OPEN
```

### Fallback Response

```python
from typing import Callable, Any, Optional

class CircuitBreakerWithFallback:
    def __init__(self, breaker: CircuitBreaker, fallback_func: Optional[Callable] = None):
        self.breaker = breaker
        self.fallback_func = fallback_func
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        try:
            return self.breaker.call(func, *args, **kwargs)
        except CircuitBreakerOpenError:
            if self.fallback_func:
                return self.fallback_func(*args, **kwargs)
            raise

# Usage
def get_cached_data():
    """Fallback to cached data"""
    return {"data": "cached", "source": "cache"}

breaker_with_fallback = CircuitBreakerWithFallback(
    api_breaker,
    fallback_func=get_cached_data
)

result = breaker_with_fallback.call(call_external_api, "https://api.example.com/data")
```

### Monitoring and Metrics

```python
from dataclasses import dataclass
from typing import List

@dataclass
class CircuitBreakerMetrics:
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    circuit_open_count: int = 0
    state_changes: List[tuple] = None  # (timestamp, old_state, new_state)
    
    def __post_init__(self):
        if self.state_changes is None:
            self.state_changes = []
    
    @property
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.successful_calls / self.total_calls

class MonitoredCircuitBreaker(CircuitBreaker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = CircuitBreakerMetrics()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        old_state = self.state
        self.metrics.total_calls += 1
        
        try:
            result = super().call(func, *args, **kwargs)
            self.metrics.successful_calls += 1
            
            if old_state != self.state:
                self.metrics.state_changes.append((
                    datetime.now(),
                    old_state,
                    self.state
                ))
            
            return result
        except CircuitBreakerOpenError:
            self.metrics.circuit_open_count += 1
            if old_state != self.state:
                self.metrics.state_changes.append((
                    datetime.now(),
                    old_state,
                    self.state
                ))
            raise
        except Exception:
            self.metrics.failed_calls += 1
            raise
```

## Best Practices

### 1. Configure Thresholds Appropriately

- **Failure Threshold**: Too low → opens too easily, too high → slow to protect
- **Timeout**: Too short → constant retries, too long → slow recovery
- **Success Threshold**: Usually 1-3 successful calls to close circuit

### 2. Use Different Breakers for Different Services

```python
# Different services may need different configurations
payment_breaker = CircuitBreaker(failure_threshold=3, timeout=30)  # Critical, fast failure
analytics_breaker = CircuitBreaker(failure_threshold=10, timeout=120)  # Less critical
```

### 3. Implement Fallback Strategies

- Return cached data
- Return default values
- Use alternative service
- Queue requests for later processing

### 4. Monitor Circuit Breaker State

- Log state changes
- Track metrics (success rate, open count)
- Alert when circuit opens frequently
- Dashboard to visualize circuit states

### 5. Handle Half-Open State Carefully

- Limit concurrent requests in HALF_OPEN
- Use single request or small batch
- Don't overwhelm recovering service

### 6. Distinguish Between Failure Types

```python
# Don't open circuit for client errors (4xx)
# Only open for server errors (5xx) or timeouts
class SmartCircuitBreaker(CircuitBreaker):
    def _on_failure(self, exception):
        # Only count server errors, not client errors
        if isinstance(exception, requests.HTTPError):
            if 400 <= exception.response.status_code < 500:
                return  # Don't count client errors
        super()._on_failure(exception)
```

## Python Libraries

### circuitbreaker

```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
def call_external_api():
    response = requests.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()
```

### pybreaker

```python
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(fail_max=5, timeout_duration=60)

@breaker
def call_external_api():
    response = requests.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()
```

## Use Cases

1. **External API Calls**: Protect against third-party service failures
2. **Database Connections**: Prevent database overload
3. **Microservices Communication**: Prevent cascading failures
4. **File System Operations**: Handle disk failures gracefully
5. **Network Operations**: Handle network timeouts and failures

## Circuit Breaker vs Retry

| Aspect | Circuit Breaker | Retry |
|--------|----------------|-------|
| **Purpose** | Prevent calls to failing service | Attempt call multiple times |
| **When** | Service is known to be failing | Transient failures expected |
| **Behavior** | Fail fast, stop calling | Keep trying with backoff |
| **Use Together** | Yes - retry with circuit breaker | Yes - circuit breaker prevents retry storms |

## Interview Q&A

### Q: What is the Circuit Breaker pattern and why is it important?

**A**: Circuit Breaker is a design pattern that prevents cascading failures by stopping calls to a failing service after a threshold. It's important because:

- Prevents resource exhaustion from waiting on timeouts
- Provides fast failure responses
- Allows services to recover without constant load
- Prevents failures from spreading across system

### Q: What are the three states of a circuit breaker?

**A**:

1. **CLOSED**: Normal operation, requests flow through, monitors failures
2. **OPEN**: Circuit is open, requests fail immediately, no actual calls made
3. **HALF_OPEN**: Testing recovery, allows limited requests to check if service recovered

### Q: How do you configure a circuit breaker?

**A**: Key parameters:

- **Failure Threshold**: Number of failures before opening (e.g., 5)
- **Timeout**: How long to stay OPEN before trying HALF_OPEN (e.g., 60 seconds)
- **Success Threshold**: Successful calls needed to close from HALF_OPEN (e.g., 2)
- **Expected Exception**: Which exceptions count as failures

### Q: What happens when a circuit breaker is OPEN?

**A**: When OPEN:

- All requests fail immediately (no timeout wait)
- Returns error or fallback response
- No actual calls made to failing service
- After timeout period, transitions to HALF_OPEN to test recovery

### Q: How do you handle fallback responses?

**A**: Common fallback strategies:

- Return cached data
- Return default/empty response
- Use alternative service
- Queue request for later processing
- Return user-friendly error message

### Q: Should you use circuit breaker with retry?

**A**: Yes, but carefully:

- Use retry for transient failures (network blips)
- Use circuit breaker to stop retrying when service is down
- Circuit breaker prevents retry storms
- Retry with exponential backoff, circuit breaker stops after threshold

### Q: How do you monitor circuit breakers?

**A**: Track:

- State changes (CLOSED → OPEN → HALF_OPEN)
- Success/failure rates
- Time spent in each state
- Number of requests blocked when OPEN
- Alert when circuit opens frequently

## Key Takeaways

✅ Circuit Breaker prevents cascading failures by stopping calls to failing services  
✅ Three states: CLOSED (normal), OPEN (failing fast), HALF_OPEN (testing recovery)  
✅ Configure thresholds appropriately (failure count, timeout, success threshold)  
✅ Implement fallback strategies (cached data, default values, alternative services)  
✅ Monitor circuit breaker state and metrics  
✅ Use different breakers for different services based on criticality  
✅ Distinguish between failure types (don't open for client errors)  
✅ Works well with retry patterns (circuit breaker prevents retry storms)


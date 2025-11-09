import time
import logging
from typing import Optional, Tuple
from functools import wraps

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

from core.redis_client import redis_client

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, redis_client, enabled: bool = True):
        self.redis = redis_client
        self.enabled = enabled
    def _get_redis_key(self, identifier: str, endpoint: str, window_start: int) -> str:
        return f"rate_limit:{identifier}:{endpoint}:{window_start}"
    
    def _get_window_start(self, timestamp: float, window_seconds: int) -> int:
        return int(timestamp // window_seconds * window_seconds)
    
    async def _get_counter(self, key: str) -> int:
        try:
            count = await self.redis.get(key)
            return int(count) if count else 0
        except Exception as e:
            logger.error(f"Error getting counter from Redis: {e}")
            # Return 0 to fail open (allow requests) if Redis is down
            return 0
    
    async def _increment_counter(self, key: str, window_seconds: int) -> int:
        try:
            # INCR is atomic - no race conditions
            count = await self.redis.incr(key)
            
            # Set expiration only on first increment (when count == 1)
            if count == 1:
                # Keep data for 2 windows (current + previous)
                await self.redis.expire(key, window_seconds * 2)
            
            return count
        except Exception as e:
            logger.error(f"Error incrementing counter in Redis: {e}")
            # Return 0 to fail open if Redis is down
            return 0
    
    async def check_rate_limit(
        self,
        identifier: str,
        endpoint: str,
        limit: int,
        window_seconds: int = 60
    ) -> Tuple[bool, dict]:
        
        # If rate limiting is disabled globally, allow all requests
        if not self.enabled:
            return True, {
                "limit": limit,
                "remaining": limit,
                "reset": int(time.time() + window_seconds)
            }
        
        try:
            # Get current timestamp
            now = time.time()
            
            # Calculate window boundaries
            current_window = self._get_window_start(now, window_seconds)
            previous_window = current_window - window_seconds
            
            # Calculate how much time has elapsed in the current window
            elapsed_in_current = now - current_window
            
            # Generate Redis keys for both windows
            current_key = self._get_redis_key(identifier, endpoint, current_window)
            previous_key = self._get_redis_key(identifier, endpoint, previous_window)
            
            # Get request counts from Redis
            current_count = await self._get_counter(current_key)
            previous_count = await self._get_counter(previous_key)
            
            # ===== SLIDING WINDOW ALGORITHM =====
            # Calculate the weight of the previous window
            # As time passes in current window, previous window matters less
            previous_weight = 1 - (elapsed_in_current / window_seconds)
            
            # Estimate total requests in the sliding window
            estimated_count = (previous_count * previous_weight) + current_count
            
            logger.debug(
                f"Rate limit check - Identifier: {identifier}, Endpoint: {endpoint}, "
                f"Current: {current_count}, Previous: {previous_count}, "
                f"Estimated: {estimated_count:.2f}, Limit: {limit}"
            )
            
            # Check if limit is exceeded
            is_allowed = estimated_count < limit
            
            # If allowed, increment the current window counter
            if is_allowed:
                await self._increment_counter(current_key, window_seconds)
                current_count += 1  # Update local count
                estimated_count += 1  # Update estimated count
            
            # Calculate remaining requests and reset time
            remaining = max(0, int(limit - estimated_count))
            reset_time = current_window + window_seconds
            
            # Return result with metadata
            return is_allowed, {
                "limit": limit,
                "remaining": remaining,
                "reset": int(reset_time),
                "retry_after": int(reset_time - now) if not is_allowed else 0
            }
            
        except Exception as e:
            logger.error(f"Error in rate limit check: {e}")
            # Fail open: allow request if there's an error
            return True, {
                "limit": limit,
                "remaining": limit,
                "reset": int(time.time() + window_seconds)
            }
    
    def _get_client_identifier(self, request: Request) -> str:
        # Try to get user ID from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Try to get API key from headers
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"apikey:{api_key}"
        
        # Fallback to IP address
        # Check for forwarded IP first (if behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            ip = forwarded_for.split(",")[0].strip()
        else:
            # Get direct client IP
            ip = request.client.host if request.client else "unknown"
        
        return f"ip:{ip}"
    
    async def __call__(
        self,
        request: Request,
        limit: int,
        window: int = 60
    ) -> None:
        # Extract client identifier
        identifier = self._get_client_identifier(request)
        
        # Get endpoint path
        endpoint = request.url.path
        
        # Check rate limit
        is_allowed, info = await self.check_rate_limit(
            identifier, endpoint, limit, window
        )
        
        # Add rate limit headers to response (will be added by middleware)
        request.state.rate_limit_info = info
        
        # If not allowed, raise 429 error
        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded - Identifier: {identifier}, "
                f"Endpoint: {endpoint}, Limit: {limit}/{window}s"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please try again in {info['retry_after']} seconds.",
                    "limit": info["limit"],
                    "window": window,
                    "reset": info["reset"],
                    "retry_after": info["retry_after"]
                },
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(info["reset"]),
                    "Retry-After": str(info["retry_after"])
                }
            )


# ===== Global rate limiter instance =====
# This will be used across the application
rate_limiter = RateLimiter(redis_client, enabled=True)


# ===== FastAPI Dependency Factory =====
def create_rate_limit_dependency(limit: int, window: int = 60):
    async def rate_limit_dependency(request: Request) -> None:
        await rate_limiter(request, limit, window)
    
    return rate_limit_dependency


# ===== Decorator for Rate Limiting =====
def rate_limit(limit: int, window: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args or kwargs
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if not request:
                logger.error(
                    f"Rate limit decorator: Could not find Request object in {func.__name__}"
                )
                # If no request found, just call the function
                return await func(*args, **kwargs)
            
            # Check rate limit
            await rate_limiter(request, limit, window)
            
            # Call the original function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# ===== Middleware for Adding Rate Limit Headers =====
async def add_rate_limit_headers(request: Request, call_next):
    # Process the request
    response = await call_next(request)
    
    # Add rate limit info to headers if available
    rate_limit_info = getattr(request.state, "rate_limit_info", None)
    if rate_limit_info:
        response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_limit_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_limit_info["reset"])
    
    return response


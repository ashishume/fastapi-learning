import time
import uuid
from typing import Optional
import redis.asyncio as redis
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, redis_client: Optional[redis.Redis], max_requests: int, window_seconds: int):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window = window_seconds

    async def check_rate_limit(self, key: str) -> bool:
        """Check if request is within rate limit. Returns True if allowed, False if exceeded."""
        if self.redis is None:
            # If Redis is not available, allow the request (graceful degradation)
            logger.warning(f"Rate limiter: Redis not available, allowing request for key: {key}")
            return True
            
        try:
            current_time = int(time.time())   
            window_start = current_time - self.window 

            # Remove old entries outside the time window
            await self.redis.zremrangebyscore(key, 0, window_start)

            # Get current request count
            request_count = await self.redis.zcard(key)

            if request_count >= self.max_requests:
                return False

            # Add current request with unique identifier (timestamp + UUID to avoid collisions)
            unique_request_id = f"{current_time}:{uuid.uuid4().hex[:8]}"
            await self.redis.zadd(key, {unique_request_id: current_time})
            await self.redis.expire(key, self.window)

            return True
        except Exception as e:
            # If Redis operation fails, log error and allow request (graceful degradation)
            logger.error(f"Rate limiter error for key {key}: {e}. Allowing request as fallback.")
            return True

    async def get_remaining_requests(self, key: str) -> int:
        """Get the number of remaining requests in the current window."""
        if self.redis is None:
            return self.max_requests
        
        try:
            current_time = int(time.time())
            window_start = current_time - self.window
            
            # Remove old entries
            await self.redis.zremrangebyscore(key, 0, window_start)
            
            # Get current request count
            request_count = await self.redis.zcard(key)
            
            return max(0, self.max_requests - request_count)
        except Exception as e:
            logger.error(f"Error getting remaining requests for key {key}: {e}")
            return self.max_requests


async def add_rate_limit_headers(request, call_next):
    """
    Middleware to add rate limit headers to all responses.
    
    This adds X-RateLimit-* headers to inform clients about rate limit status.
    Note: This doesn't enforce rate limiting, it just adds informational headers.
    For actual rate limiting, use the RateLimiter class in route handlers.
    """
    from core.rate_limit_config import RateLimitConfig
    from core.redis_client import get_redis_client
    
    response = await call_next(request)
    
    # Only add headers if rate limiting is enabled
    if not RateLimitConfig.ENABLED:
        return response
    
    try:
        # Try to get Redis client to calculate remaining requests
        redis_client = get_redis_client()
        
        # Get client IP for rate limit key
        client_ip = request.client.host if request.client else "unknown"
        rate_limit_key = f"rate_limit:global:{client_ip}"
        
        # Calculate remaining requests
        current_time = int(time.time())
        window_start = current_time - RateLimitConfig.DEFAULT_WINDOW_SECONDS
        
        # Remove old entries
        await redis_client.zremrangebyscore(rate_limit_key, 0, window_start)
        
        # Get current request count
        request_count = await redis_client.zcard(rate_limit_key)
        remaining = max(0, RateLimitConfig.DEFAULT_MAX_REQUESTS - request_count)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(RateLimitConfig.DEFAULT_MAX_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(RateLimitConfig.DEFAULT_WINDOW_SECONDS)
        response.headers["X-RateLimit-Reset"] = str(current_time + RateLimitConfig.DEFAULT_WINDOW_SECONDS)
        
    except (RuntimeError, Exception) as e:
        # If Redis is not available or there's an error, still add basic headers
        logger.debug(f"Could not calculate rate limit headers: {e}")
        response.headers["X-RateLimit-Limit"] = str(RateLimitConfig.DEFAULT_MAX_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(RateLimitConfig.DEFAULT_MAX_REQUESTS)
    
    return response






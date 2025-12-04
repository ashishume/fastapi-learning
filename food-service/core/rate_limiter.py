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
            

        current_time = int(time.time())   
        window_start = current_time - self.window 

        # Remove old entries outside the time window
        await self.redis.zremrangebyscore(key, 0, window_start)

        # Get current request count
        request_count = await self.redis.zcard(key)

        if request_count >= self.max_requests:
            return False

        # Add current request timestamp

        unique_request_id = f"{current_time}:{uuid.uuid4().hex[:8]}"
        await self.redis.zadd(key, {unique_request_id: current_time})
        await self.redis.expire(key, self.window)

        return True

    async def get_remaining_requests(self, key: str) -> int:
        """Get the number of remaining requests in the current window."""
        if self.redis is None:
            return self.max_requests
            
        current_time = int(time.time())
        window_start = current_time - self.window
        
        # Remove old entries
        await self.redis.zremrangebyscore(key, 0, window_start)
        
        # Get current request count
        request_count = await self.redis.zcard(key)
        
        return max(0, self.max_requests - request_count)






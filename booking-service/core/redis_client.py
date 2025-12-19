from redis.asyncio import Redis
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

redis_client: Optional[Redis] = None


async def get_redis() -> Optional[Redis]:
    """Get the Redis client instance. Returns None if not connected."""
    return redis_client


async def connect_redis():
    """Initialize and test Redis connection at startup.
    
    This function will attempt to connect to Redis but will not raise an exception
    if the connection fails. The application will continue to run without Redis.
    """
    global redis_client
    try:
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            logger.warning("⚠️  REDIS_URL not set. Redis will not be available.")
            redis_client = None
            return
        
        redis_client = Redis.from_url(redis_url, decode_responses=True, encoding="utf-8")
        
        # Test the connection (ping() is async, needs await)
        pong = await redis_client.ping()
        if pong:
            logger.info("✅ Connected to Redis successfully")
        else:
            logger.warning("⚠️  Redis ping failed. Application will continue without Redis caching.")
            redis_client = None
    except Exception as e:
        logger.warning(f"⚠️  Redis connection failed: {e}. Application will continue without Redis caching.")
        redis_client = None
        # Don't raise the exception - allow the app to start without Redis


async def close_redis():
    """Close Redis connection pool gracefully on shutdown."""
    global redis_client
    if redis_client is None:
        logger.info("Redis client is not initialized, skipping close")
        return
    
    try:
        await redis_client.close()
        redis_client = None
        logger.info("🧹 Redis connection closed")
    except Exception as e:
        logger.warning(f"Error closing Redis connection: {e}")
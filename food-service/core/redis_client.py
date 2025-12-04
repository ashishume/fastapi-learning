import redis.asyncio as redis
import redis as redis_sync
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Get Redis URL from environment variable (defaults to localhost for local dev)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Async Redis client instance (initialized in connect_redis)
redis_client: Optional[redis.Redis] = None

# Sync Redis client instance (for use in synchronous code like repositories)
sync_redis_client: Optional[redis_sync.Redis] = None


async def connect_redis():
    """Initialize and test Redis connection at startup.
    
    This function will attempt to connect to Redis but will not raise an exception
    if the connection fails. The application will continue to run without Redis.
    """
    global redis_client, sync_redis_client
    try:
        # Create async Redis client instance (connection pool is managed internally)
        redis_client = redis.from_url(
            REDIS_URL, decode_responses=True, encoding="utf-8"
        )
        # Test the connection
        pong = await redis_client.ping()
        if pong:
            logger.info("✅ Connected to Redis successfully")
            
        # Also create sync Redis client for use in synchronous code
        sync_redis_client = redis_sync.from_url(
            REDIS_URL, decode_responses=True, encoding="utf-8"
        )
        sync_redis_client.ping()
        logger.info("✅ Synchronous Redis client initialized")
    except Exception as e:
        logger.warning(f"⚠️  Redis connection failed: {e}. Application will continue without Redis caching.")
        redis_client = None
        sync_redis_client = None
        # Don't raise the exception - allow the app to start without Redis


async def close_redis():
    """Close Redis connection pool gracefully on shutdown."""
    global redis_client, sync_redis_client
    if redis_client is None and sync_redis_client is None:
        logger.warning("Redis client is not initialized, skipping close")
        return
    
    try:
        if redis_client:
            await redis_client.close()
            redis_client = None
        if sync_redis_client:
            sync_redis_client.close()
            sync_redis_client = None
        logger.info("🧹 Redis connections closed")
    except Exception as e:
        logger.warning(f"Error closing Redis connection: {e}")


def get_redis_client() -> redis.Redis:
    """Get the async Redis client instance. Raises error if not connected."""
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized. Call connect_redis() first.")
    return redis_client


def get_sync_redis_client() -> Optional[redis_sync.Redis]:
    """Get the synchronous Redis client instance. Returns None if not connected.
    
    This is safe to use in synchronous code like repositories. Returns None
    if Redis is not available, allowing the code to gracefully fall back to database.
    """
    return sync_redis_client

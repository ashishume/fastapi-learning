import redis.asyncio as redis
import logging
import os

logger = logging.getLogger(__name__)

# Get Redis URL from environment variable (defaults to localhost for local dev)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create a single Redis client instance (connection pool is managed internally)
redis_client = redis.from_url(
    REDIS_URL, decode_responses=True, encoding="utf-8"
)


async def connect_redis():
    """Test Redis connection at startup."""
    try:
        pong = await redis_client.ping()
        if pong:
            logger.info("✅ Connected to Redis successfully")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        raise e


async def close_redis():
    """Close Redis connection pool gracefully on shutdown."""
    try:
        await redis_client.close()
        logger.info("🧹 Redis connection closed")
    except Exception as e:
        logger.warning(f"Error closing Redis connection: {e}")

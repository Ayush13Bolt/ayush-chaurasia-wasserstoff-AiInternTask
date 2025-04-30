import redis.asyncio as redis
import os
import logging

logger = logging.getLogger(__name__)

# Initialize and return a Redis client instance
async def init_redis():
    try:
        redis_client = redis.from_url(os.getenv("REDIS_URL"))
        await redis_client.ping()  # Check if the connection is successful
        logger.info("Successfully connected to Redis.")
        return redis_client  # Return the initialized client
    except redis.exceptions.ConnectionError as e:
        # Log and handle connection error gracefully
        logger.error(f"Error connecting to Redis: {e}")
        return None

# Cache or retrieve verdict for a given seed and guess
async def cache_verdict(redis_client, seed, guess, verdict=None):
    if redis_client is None:
        # Skip caching if Redis client isn't available
        logger.warning("Redis client is not initialized. Cache operations will be skipped.")
        return None

    key = f"{seed.lower()}:{guess.lower()}"
    try:
        # Retrieve verdict if none is provided
        if verdict is None:
            return await redis_client.get(key)
        # Cache verdict with a 1-day expiration
        await redis_client.set(key, verdict, ex=86400)  # Cache for 1 day
        return None
    except redis.exceptions.RedisError as e:
        # Handle Redis-related errors during cache access
        logger.error(f"Redis error during cache operation: {e}")
        return None

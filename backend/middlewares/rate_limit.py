from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
import time
import logging

logger = logging.getLogger(__name__)

# Middleware class to limit the number of requests per IP
class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        redis_client = request.app.state.redis_client

        # If Redis isn't available, log and skip rate limiting
        if redis_client is None:
            logger.warning("Redis client not initialized. Rate limiting will be skipped.")
            return await call_next(request)

        # Generate a rate limit key based on IP and timestamp
        ip = request.client.host
        now = int(time.time())
        key = f"rate-limit:{ip}:{now}"

        try:
            # Increment the request count in Redis
            current = await redis_client.incr(key)

            # Set a 1-second expiration for the rate window
            if current == 1:
                await redis_client.expire(key, 1)

            if current > 5:
                raise HTTPException(status_code=429, detail="Too many requests, slow down!")

            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Error during rate limiting: {e}")
            return await call_next(request)

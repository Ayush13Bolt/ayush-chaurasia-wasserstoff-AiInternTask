from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.api.routes import router
from backend.db.db import init_db, engine  
from backend.db.models import Base 
from backend.core.cache import init_redis 
from backend.middlewares.rate_limit import RateLimiterMiddleware
import os
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

__version__ = "0.1.0"

app = FastAPI(title="What Beats Rock?")

# Register API routes from the router
app.include_router(router)

# Mount static frontend files at root
app.mount("/", StaticFiles(directory="./frontend", html=True), name="frontend")

# Function to create tables in the database
async def create_db_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# FastAPI startup event to initialize services
@app.on_event("startup")
async def startup_event():
    await asyncio.sleep(5)  # Delay startup slightly to wait for services

    await create_db_tables()

    # Initialize the DB connection
    await init_db()

    # Initialize Redis and store client in app state
    app.state.redis_client = await init_redis()

    # Initialize in-memory session storage
    app.state.user_sessions = {}

# Add the rate limiter middleware to the app
app.add_middleware(RateLimiterMiddleware)

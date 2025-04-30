import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Load the database connection URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create an async engine for connecting to the database
engine = create_async_engine(DATABASE_URL)

# Set up the async session maker for handling DB sessions
async_session = async_sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Declare a base class for the ORM models
Base = declarative_base()

# Dependency function to get an async database session
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

# Initialize the database and create tables based on models
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)   

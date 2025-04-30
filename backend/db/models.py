from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Define the declarative base for ORM model classes
Base = declarative_base()

# Define the GuessCount model mapped to the 'guess_counts' table
class GuessCount(Base):
    __tablename__ = "guess_counts"

    # Primary key ID for each record
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, index=True)
    count = Column(Integer, default=0)

"""
Database connection and session management for SQLModel.
Uses Neon Serverless Postgres.
"""

import os
from typing import Generator
from dotenv import load_dotenv
from sqlmodel import create_engine, Session

# Load environment variables
load_dotenv()

# Neon Serverless Postgres connection string
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create SQLModel engine
# echo=False to avoid leaking sensitive data in logs
engine = create_engine(DATABASE_URL, echo=False)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Ensures proper cleanup after each request.
    """
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """Initialize database tables."""
    from src.models.task import Task
    from src.models.user import User

    # Create tables for both models
    Task.metadata.create_all(engine)
    User.metadata.create_all(engine)

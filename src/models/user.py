"""
SQLModel User model for database storage.
"""

from typing import Optional
from sqlmodel import Field, SQLModel
import uuid


class User(SQLModel, table=True):
    """
    User model for storing user details in the database.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    password: str = Field(nullable=False)
    name: str = Field(nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"

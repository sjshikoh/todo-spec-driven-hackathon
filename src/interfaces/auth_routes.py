"""
Temporary authentication routes for development.
These will be replaced by Better Auth integration.
"""

import secrets
from fastapi import APIRouter, HTTPException, status, Header, Depends
from typing import Optional
from pydantic import BaseModel
from sqlmodel import Session, select
import uuid

from src.auth.temp_jwt import create_temp_token
from src.db.database import get_session
from src.models.user import User
from src.core.security import hash_password, verify_password


# ============ Pydantic Models ============

class SignUpRequest(BaseModel):
    email: str
    password: str
    name: str


class SignInRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    message: str
    token: str
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    name: str


# ============ Router ============

router = APIRouter(prefix="/auth", tags=["auth"])


# ============ Routes ============

@router.post("/sign-up", response_model=AuthResponse)
async def sign_up(data: SignUpRequest, session: Session = Depends(get_session)):
    """Temporary sign-up endpoint for development."""
    # Check if user already exists
    statement = select(User).where(User.email == data.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = hash_password(data.password)

    # Create new user
    user = User(
        email=data.email,
        name=data.name,
        password=hashed_password
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    token = create_temp_token(user.id, user.email, user.name)

    return AuthResponse(
        message="User registered successfully",
        token=token,
        user={"id": user.id, "email": user.email, "name": user.name}
    )


@router.post("/sign-in", response_model=AuthResponse)
async def sign_in(data: SignInRequest, session: Session = Depends(get_session)):
    """Temporary sign-in endpoint for development."""
    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_temp_token(user.id, user.email, user.name)

    return AuthResponse(
        message="Login successful",
        token=token,
        user={"id": user.id, "email": user.email, "name": user.name}
    )


@router.get("/me", response_model=UserResponse)
async def get_me(authorization: Optional[str] = Header(None), session: Session = Depends(get_session)):
    """Temporary endpoint to get current user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing or invalid"
        )

    token = authorization.split(" ")[1]
    from src.auth.temp_jwt import verify_temp_token
    payload = verify_temp_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")

    if user_id:
        user = session.get(User, user_id)
        if user:
            return UserResponse(
                id=user.id,
                email=user.email,
                name=user.name
            )

    # Fallback to JWT payload if user not found in DB (should theoretically not happen if consistent)
    # or to handle cases where we want to trust the token temporarily
    return UserResponse(
        id=payload.get("sub", ""),
        email=payload.get("email", ""),
        name=payload.get("name", "")
    )

"""
Temporary authentication routes for development.
These will be replaced by Better Auth integration.
"""

import secrets
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.auth.temp_jwt import create_temp_token


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


# ============ In-memory user storage ============
_users_db = {}


# ============ Password Utilities ============

def hash_password(password: str) -> str:
    """Simple password hashing for development."""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == hashed


# ============ Routes ============

@router.post("/sign-up", response_model=AuthResponse)
async def sign_up(data: SignUpRequest):
    """Temporary sign-up endpoint for development."""
    # Check if user already exists
    for user in _users_db.values():
        if user["email"] == data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    user_id = secrets.token_hex(16)
    hashed_password = hash_password(data.password)

    user = {
        "id": user_id,
        "email": data.email,
        "name": data.name,
        "password": hashed_password,
    }

    _users_db[user_id] = user
    token = create_temp_token(user_id, data.email, data.name)

    return AuthResponse(
        message="User registered successfully",
        token=token,
        user={"id": user_id, "email": data.email, "name": data.name}
    )


@router.post("/sign-in", response_model=AuthResponse)
async def sign_in(data: SignInRequest):
    """Temporary sign-in endpoint for development."""
    user = None
    user_id = None

    for uid, u in _users_db.items():
        if u["email"] == data.email:
            user = u
            user_id = uid
            break

    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_temp_token(user_id, user["email"], user["name"])

    return AuthResponse(
        message="Login successful",
        token=token,
        user={"id": user_id, "email": user["email"], "name": user["name"]}
    )


@router.get("/me", response_model=UserResponse)
async def get_me(authorization: str):
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
    if not user_id or user_id not in _users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    user = _users_db[user_id]
    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"]
    )
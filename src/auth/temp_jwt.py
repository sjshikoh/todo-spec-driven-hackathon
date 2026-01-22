"""
Temporary JWT implementation for development.
This will be replaced by Better Auth JWKS verification.
"""

import os
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional

# Temporary secret key for development
JWT_SECRET = os.environ.get("JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def create_temp_token(user_id: str, email: str, name: str) -> str:
    """Create a temporary JWT token for development."""
    payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_temp_token(token: str) -> Optional[dict]:
    """Verify a temporary JWT token and return the payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.InvalidTokenError:
        return None


def get_user_id_from_temp_token(token: str) -> Optional[str]:
    """Extract user_id from temporary JWT token."""
    payload = verify_temp_token(token)
    if payload:
        return payload.get("sub")
    return None
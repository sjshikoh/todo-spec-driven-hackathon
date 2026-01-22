"""
Temporary authentication for task routes.
This will be replaced by Better Auth JWKS verification.
"""

from fastapi import HTTPException, Request, status
from src.auth.temp_jwt import get_user_id_from_temp_token


def get_current_user_id_temp(request: Request) -> str:
    """
    Temporary authentication for task routes.
    Uses HS256 tokens instead of RS256 JWKS.
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
        )

    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>",
        )

    token = auth_header[7:]  # Remove "Bearer " prefix

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is empty",
        )

    user_id = get_user_id_from_temp_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return user_id
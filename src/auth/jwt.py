"""
JWT verification using JWKS (JSON Web Key Set).
Verifies JWTs issued by Better Auth using RS256 algorithm.
"""

import os
import json
import jwt
from typing import Optional
from fastapi import HTTPException, Request, status
from jwt import PyJWKClient

# Better Auth configuration
BETTER_AUTH_URL = os.environ.get("BETTER_AUTH_URL", "http://localhost:3000")
BETTER_AUTH_JWKS_PATH = os.environ.get("BETTER_AUTH_JWKS_PATH", "/api/auth/sign-in")

_jwks_client: Optional[PyJWKClient] = None


def get_jwks_client() -> PyJWKClient:
    """Get or create the JWKS client."""
    global _jwks_client
    if _jwks_client is None:
        jwks_url = f"{BETTER_AUTH_URL}{BETTER_AUTH_JWKS_PATH}"
        _jwks_client = PyJWKClient(jwks_url)
    return _jwks_client


def verify_jwt(token: str) -> dict:
    """
    Verify a JWT token using JWKS and return the decoded payload.

    Args:
        token: The JWT token to verify

    Returns:
        The decoded JWT payload

    Raises:
        HTTPException: If token verification fails
    """
    try:
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require": ["sub", "exp"],
            },
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )


def get_current_user_id(request: Request) -> str:
    """
    Extract and verify the JWT from request headers and return the user_id.

    Args:
        request: The FastAPI request object

    Returns:
        The user_id from the JWT "sub" claim

    Raises:
        HTTPException: If authentication fails
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

    payload = verify_jwt(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain 'sub' claim",
        )

    return user_id

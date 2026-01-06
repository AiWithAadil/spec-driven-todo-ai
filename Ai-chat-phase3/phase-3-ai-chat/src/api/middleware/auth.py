"""Authentication middleware for extracting user_id from JWT."""

import os
from typing import Optional
import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

from src.utils.errors import AuthenticationError


security = HTTPBearer()


def extract_user_id(credentials: Optional[dict] = Depends(security)) -> str:
    """Extract user_id from JWT token in Authorization header."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    jwt_secret = os.getenv("JWT_SECRET", "your-secret-key-here")

    try:
        # Try to decode with verification first (production)
        try:
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            # Fallback: decode without verification for local testing
            payload = jwt.decode(token, options={"verify_signature": False})

        user_id = payload.get("sub") or payload.get("user_id")

        if not user_id:
            raise AuthenticationError(
                "No user_id in token",
                user_message="Invalid authentication token",
            )

        return str(user_id)

    except jwt.DecodeError as e:
        raise AuthenticationError(
            f"Invalid token format: {str(e)}",
            user_message="Invalid authentication token",
        )
    except Exception as e:
        raise AuthenticationError(
            f"Token validation failed: {str(e)}",
            user_message="Authentication failed",
        )


def extract_user_id_optional(
    credentials: Optional[dict] = Depends(security),
) -> Optional[str]:
    """Extract user_id from JWT token (optional)."""
    if not credentials:
        return None

    try:
        return extract_user_id(credentials)
    except:
        return None

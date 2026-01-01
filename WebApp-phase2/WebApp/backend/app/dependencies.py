"""Dependency injection for FastAPI routes"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .utils.security import decode_token
from .utils.errors import InvalidTokenException


async def get_current_user(
    token: str = Depends(lambda: None),
    db: Session = Depends(get_db),
) -> User:
    """Get current user from JWT token"""
    if not token:
        raise InvalidTokenException()

    try:
        payload = decode_token(token)
        user_id: int = payload.get("sub")
        if user_id is None:
            raise InvalidTokenException()
    except Exception:
        raise InvalidTokenException()

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise InvalidTokenException()

    return user

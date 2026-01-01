"""Security utilities for JWT and password hashing"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from .errors import InvalidTokenException
from ..config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Truncate to 72 bytes as per bcrypt limitation
    password_bytes = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    # Truncate to 72 bytes as per bcrypt limitation
    password_bytes = plain_password[:72].encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    import logging
    from datetime import timezone
    logger = logging.getLogger(__name__)

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.access_token_expire_hours)

    # JWT exp should be Unix timestamp (seconds)
    to_encode.update({"exp": expire})
    logger.info(f"[SECURITY] Creating token for user: {data.get('email')} with expiry: {expire}")
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    logger.info(f"[SECURITY] Token created successfully: {encoded_jwt[:30]}...")
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token"""
    import logging
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"[SECURITY] Decoding token with algorithm: {settings.algorithm}")
        logger.info(f"[SECURITY] Using secret key length: {len(settings.secret_key)}")
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        logger.info(f"[SECURITY] Token decoded successfully. Payload: {payload}")
        return payload
    except JWTError as e:
        logger.error(f"[SECURITY] JWT decode error: {str(e)}")
        raise InvalidTokenException()

"""Authentication utilities."""

import secrets
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_token(token: str) -> str:
    """Hash a token."""
    return pwd_context.hash(token)


def verify_token(token: str, hashed: str) -> bool:
    """Verify a token against its hash."""
    return pwd_context.verify(token, hashed)


def create_magic_link_token() -> str:
    """Create a magic link token."""
    return secrets.token_urlsafe(32)


def create_invite_token() -> str:
    """Create an invite token."""
    return secrets.token_urlsafe(32)


def create_api_key() -> str:
    """Create an API key."""
    return f"sk_{secrets.token_urlsafe(32)}"


def create_jwt_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)

    to_encode = {"sub": str(user_id), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_jwt_token(token: str) -> Optional[str]:
    """Decode a JWT token and return user_id."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


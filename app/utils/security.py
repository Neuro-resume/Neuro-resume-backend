"""Security utilities: password hashing and JWT tokens."""

import logging
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password to verify against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.
    
    Args:
        user_id: User ID to encode in token
        expires_delta: Optional custom expiration time
        
    Returns:
        JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=settings.jwt_expiration)

    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """Decode and verify a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        User ID from token, or None if invalid
    """
    try:
        logger.debug(f"Attempting to decode token: {token[:20]}...")
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        logger.debug(f"Token decoded successfully. Payload: {payload}")
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token payload does not contain 'sub' field")
            return None
        logger.debug(f"Extracted user_id: {user_id}")
        return user_id
    except ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except (DecodeError, InvalidTokenError) as e:
        logger.error(f"JWT decode error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {e}", exc_info=True)
        return None


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Dependency to get current authenticated user ID from token.
    
    Args:
        credentials: HTTP Bearer credentials from request
        
    Returns:
        User ID
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    token = credentials.credentials
    logger.debug(f"Received credentials. Token length: {len(token)}")
    user_id = decode_access_token(token)

    if user_id is None:
        logger.warning("Failed to extract user_id from token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"Successfully authenticated user: {user_id}")
    return user_id

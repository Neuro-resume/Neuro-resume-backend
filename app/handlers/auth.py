"""Authentication handlers."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_db
from app.models.common import (ErrorResponse, conflict_error_response,
                               unauthorized_error_response)
from app.models.user import (ChangePasswordRequest, TokenResponse, UserCreate,
                             UserLogin, UserResponse)
from app.repository.user import UserRepository
from app.utils.security import (create_access_token, get_current_user_id,
                                hash_password, verify_password)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Token response with user data

    Raises:
        HTTPException: If username or email already exists
    """
    repo = UserRepository(db)

    # Check if username exists
    existing_user = await repo.get_user_by_username(user_data.username)
    if existing_user:
        logger.warning(
            f"Registration attempt with existing username: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=conflict_error_response(
                f"Username '{user_data.username}' already exists"
            ).dict(),
        )

    # Check if email exists
    existing_email = await repo.get_user_by_email(user_data.email)
    if existing_email:
        logger.warning(
            f"Registration attempt with existing email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=conflict_error_response(
                f"Email '{user_data.email}' already exists").dict(),
        )

    # Create user
    password_hash = hash_password(user_data.password)
    user = await repo.create_user(
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
    )

    # Generate token
    token = create_access_token(str(user.id))

    logger.info(
        f"User registered successfully: {user.username} (ID: {user.id})")

    return TokenResponse(
        token=token,
        user=UserResponse.model_validate(user),
        expires_in=86400,  # 24 hours
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate user and return token.

    Args:
        credentials: Login credentials
        db: Database session

    Returns:
        Token response with user data

    Raises:
        HTTPException: If credentials are invalid
    """
    repo = UserRepository(db)

    # Find user by username
    user = await repo.get_user_by_username(credentials.username)
    if not user:
        logger.warning(
            f"Login attempt with non-existent username: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=unauthorized_error_response(
                "Invalid username or password").dict(),
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        logger.warning(
            f"Failed login attempt for user: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=unauthorized_error_response(
                "Invalid username or password").dict(),
        )

    # Generate token
    token = create_access_token(str(user.id))

    logger.info(
        f"User logged in successfully: {user.username} (ID: {user.id})")

    return TokenResponse(
        token=token,
        user=UserResponse.model_validate(user),
        expires_in=86400,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user_id: str = Depends(get_current_user_id),
) -> None:
    """Logout user (invalidate token).

    Note: In a stateless JWT implementation, actual token invalidation
    would require a token blacklist or short-lived tokens with refresh tokens.
    This endpoint is mainly for client-side token removal.

    Args:
        current_user_id: Current authenticated user ID
    """
    logger.info(f"User logged out: {current_user_id}")
    return None


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh access token.

    Args:
        current_user_id: Current authenticated user ID
        db: Database session

    Returns:
        New token response

    Raises:
        HTTPException: If user not found
    """
    repo = UserRepository(db)

    # Get user
    user = await repo.get_user_by_id(uuid.UUID(current_user_id))
    if not user:
        logger.error(f"Token refresh failed: user not found {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=unauthorized_error_response("User not found").dict(),
        )

    # Generate new token
    token = create_access_token(str(user.id))

    logger.info(f"Token refreshed for user: {user.username} (ID: {user.id})")

    return TokenResponse(
        token=token,
        user=UserResponse.model_validate(user),
        expires_in=86400,
    )

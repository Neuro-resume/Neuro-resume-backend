"""User profile handlers."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_db
from app.models.common import not_found_error_response, unauthorized_error_response
from app.models.user import ChangePasswordRequest, UserResponse, UserUpdate
from app.repository.user import UserRepository
from app.utils.security import get_current_user_id, hash_password, verify_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Get current user profile.
    
    Args:
        current_user_id: Current authenticated user ID
        db: Database session
        
    Returns:
        User profile data
        
    Raises:
        HTTPException: If user not found
    """
    repo = UserRepository(db)
    user = await repo.get_user_by_id(uuid.UUID(current_user_id))

    if not user:
        logger.error(f"User profile not found: {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_error_response("User not found").dict(),
        )

    logger.info(f"User profile retrieved: {user.username} (ID: {user.id})")
    return UserResponse.model_validate(user)


@router.patch("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_data: UserUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Update user profile.
    
    Args:
        profile_data: Profile update data
        current_user_id: Current authenticated user ID
        db: Database session
        
    Returns:
        Updated user profile
        
    Raises:
        HTTPException: If user not found or email already exists
    """
    repo = UserRepository(db)

    # Check if email is being updated and already exists
    if profile_data.email:
        existing_email = await repo.get_user_by_email(profile_data.email)
        if existing_email and str(existing_email.id) != current_user_id:
            logger.warning(f"Attempt to update to existing email: {profile_data.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": {"code": "CONFLICT", "message": f"Email '{profile_data.email}' already exists"}},
            )

    # Update user
    user = await repo.update_user(
        user_id=uuid.UUID(current_user_id),
        first_name=profile_data.first_name,
        last_name=profile_data.last_name,
        email=profile_data.email,
        phone=profile_data.phone,
        location=profile_data.location,
        full_name=profile_data.full_name,
    )

    if not user:
        logger.error(f"User not found during profile update: {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_error_response("User not found").dict(),
        )

    logger.info(f"User profile updated: {user.username} (ID: {user.id})")
    return UserResponse.model_validate(user)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Change user password.
    
    Args:
        password_data: Password change data
        current_user_id: Current authenticated user ID
        db: Database session
        
    Raises:
        HTTPException: If user not found or current password is incorrect
    """
    repo = UserRepository(db)
    user = await repo.get_user_by_id(uuid.UUID(current_user_id))

    if not user:
        logger.error(f"User not found during password change: {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_error_response("User not found").dict(),
        )

    # Verify current password
    current_pwd = password_data.get_current_password()
    if not current_pwd:
        logger.warning(f"No current/old password provided for user: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": {"code": "VALIDATION_ERROR", "message": "Current or old password is required"}},
        )
    
    if not verify_password(current_pwd, user.password_hash):
        logger.warning(f"Failed password change attempt for user: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_PASSWORD", "message": "Current password is incorrect"}},
        )

    # Update password
    new_password_hash = hash_password(password_data.new_password)
    await repo.update_password(uuid.UUID(current_user_id), new_password_hash)

    logger.info(f"Password changed for user: {user.username} (ID: {user.id})")
    return None

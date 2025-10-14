"""User repository for database operations."""

import logging
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for User database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
    ) -> User:
        """Create a new user.

        Args:
            username: Username
            email: Email address
            password_hash: Hashed password
            first_name: First name (optional)
            last_name: Last name (optional)
            phone: Phone number (optional)

        Returns:
            Created user
        """
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        logger.info(f"Created user: {user.username} (ID: {user.id})")
        return user

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User if found, None otherwise
        """
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username.

        Args:
            username: Username

        Returns:
            User if found, None otherwise
        """
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email.

        Args:
            email: Email address

        Returns:
            User if found, None otherwise
        """
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def update_user(
        self,
        user_id: uuid.UUID,
        username: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Optional[User]:
        """Update user profile.

        Args:
            user_id: User ID
            username: Username (optional)
            email: Email (optional)

        Returns:
            Updated user if found, None otherwise
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        if username is not None:
            user.username = username
        if email is not None:
            user.email = email

        await self.session.commit()
        await self.session.refresh(user)
        logger.info(f"Updated user: {user.username} (ID: {user.id})")
        return user

    async def update_password(self, user_id: uuid.UUID, password_hash: str) -> bool:
        """Update user password.

        Args:
            user_id: User ID
            password_hash: New hashed password

        Returns:
            True if updated, False if user not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        user.password_hash = password_hash
        await self.session.commit()
        logger.info(
            f"Updated password for user: {user.username} (ID: {user.id})")
        return True

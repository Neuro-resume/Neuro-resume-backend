"""Interview session and message repository."""

import logging
import uuid
from typing import List, Optional, Union

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.session import (InterviewSession, Language, Message,
                                MessageRole, SessionStatus)

logger = logging.getLogger(__name__)


class SessionRepository:
    """Repository for InterviewSession and Message operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create_session(
        self, user_id: uuid.UUID, language: Language = Language.RU
    ) -> InterviewSession:
        """Create a new interview session.

        Args:
            user_id: User ID
            language: Session language

        Returns:
            Created session
        """
        logger.info(f"here is create sess")
        session_obj = InterviewSession(
            user_id=user_id,
            language=language,
            status="in_progress",
            progress={"percentage": 0, "completedSections": [],
                      "currentSection": None},
            message_count=0,
        )
        self.session.add(session_obj)
        await self.session.commit()
        await self.session.refresh(session_obj)
        logger.info(f"Created session: {session_obj.id} for user {user_id}")
        return session_obj

    async def get_session_by_id(
        self, session_id: uuid.UUID, user_id: Optional[uuid.UUID] = None
    ) -> Optional[InterviewSession]:
        """Get session by ID, optionally filtered by user.

        Args:
            session_id: Session ID
            user_id: Optional user ID for authorization check

        Returns:
            Session if found, None otherwise
        """
        query = select(InterviewSession).where(
            InterviewSession.id == session_id)
        if user_id:
            query = query.where(InterviewSession.user_id == user_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_sessions(
        self,
        user_id: uuid.UUID,
        status: Optional[SessionStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[List[InterviewSession], int]:
        """Get user's sessions with pagination.

        Args:
            user_id: User ID
            status: Optional status filter
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip

        Returns:
            Tuple of (sessions list, total count)
        """
        # Base query
        query = select(InterviewSession).where(
            InterviewSession.user_id == user_id)
        count_query = select(func.count()).select_from(InterviewSession).where(
            InterviewSession.user_id == user_id
        )

        # Add status filter
        if status:
            status_enum = self._normalize_status_filter(status)
            query = query.where(InterviewSession.status == status_enum)
            count_query = count_query.where(
                InterviewSession.status == status_enum)

        # Get total count
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Get sessions with pagination
        query = query.order_by(InterviewSession.created_at.desc()).offset(
            offset).limit(limit)
        result = await self.session.execute(query)
        sessions = result.scalars().all()

        return list(sessions), total

    @staticmethod
    def _normalize_status_filter(status: Union[SessionStatus, str]) -> SessionStatus:
        """Convert incoming status filter to SessionStatus enum.

        Args:
            status: Status provided by handler or caller.

        Returns:
            Normalized SessionStatus value.

        Raises:
            ValueError: If status cannot be mapped to a valid SessionStatus.
        """

        if isinstance(status, SessionStatus):
            return status

        if isinstance(status, str):
            raw_value = status.strip()
            if not raw_value:
                raise ValueError("Empty status filter is not allowed")

            normalized_key = raw_value.replace("-", "_")

            # Try matching by enum name (upper case)
            try:
                return SessionStatus[normalized_key.upper()]
            except KeyError:
                pass

            # Try matching by enum value (lower case)
            try:
                return SessionStatus(normalized_key.lower())
            except ValueError:
                pass

        logger.warning("Unexpected session status filter received: %s", status)
        raise ValueError(f"Unsupported session status filter: {status}")

    async def update_session_progress(
        self,
        session_id: uuid.UUID,
        percentage: Optional[int] = None,
        completed_sections: Optional[List[str]] = None,
        current_section: Optional[str] = None,
    ) -> Optional[InterviewSession]:
        """Update session progress.

        Args:
            session_id: Session ID
            percentage: Completion percentage (0-100)
            completed_sections: List of completed sections
            current_section: Current section name

        Returns:
            Updated session if found, None otherwise
        """
        session_obj = await self.get_session_by_id(session_id)
        if not session_obj:
            return None

        progress = session_obj.progress or {}
        if percentage is not None:
            progress["percentage"] = percentage
        if completed_sections is not None:
            progress["completedSections"] = completed_sections
        if current_section is not None:
            progress["currentSection"] = current_section

        session_obj.progress = progress
        await self.session.commit()
        await self.session.refresh(session_obj)
        return session_obj

    async def complete_session(self, session_id: uuid.UUID) -> Optional[InterviewSession]:
        """Mark session as completed.

        Args:
            session_id: Session ID

        Returns:
            Updated session if found, None otherwise
        """
        session_obj = await self.get_session_by_id(session_id)
        if not session_obj:
            return None

        session_obj.status = SessionStatus.COMPLETED
        from datetime import datetime
        session_obj.completed_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(session_obj)
        logger.info(f"Completed session: {session_id}")
        return session_obj

    async def delete_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete a session.

        Args:
            session_id: Session ID
            user_id: User ID for authorization

        Returns:
            True if deleted, False if not found
        """
        session_obj = await self.get_session_by_id(session_id, user_id)
        if not session_obj:
            return False

        await self.session.delete(session_obj)
        await self.session.commit()
        logger.info(f"Deleted session: {session_id}")
        return True

    # Message operations
    async def create_message(
        self,
        session_id: uuid.UUID,
        role: MessageRole,
        content: str,
        message_metadata: Optional[dict] = None,
    ) -> Message:
        """Create a new message in session.

        Args:
            session_id: Session ID
            role: Message role (user or AI)
            content: Message content
            message_metadata: Optional metadata

        Returns:
            Created message
        """
        message = Message(
            session_id=session_id, role=role, content=content, message_metadata=message_metadata
        )
        self.session.add(message)

        # Increment message count
        session_obj = await self.get_session_by_id(session_id)
        if session_obj:
            session_obj.message_count += 1

        await self.session.commit()
        await self.session.refresh(message)
        logger.info(f"Created message: {message.id} in session {session_id}")
        return message

    async def get_session_messages(
        self, session_id: uuid.UUID
    ) -> List[Message]:
        """Get all messages in a session.

        Args:
            session_id: Session ID

        Returns:
            List of messages ordered by creation time
        """
        query = (
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

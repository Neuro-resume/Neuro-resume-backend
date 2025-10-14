"""Interview session and message repository."""

import logging
import uuid
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

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
        session_obj = InterviewSession(
            user_id=user_id,
            language=language,
            status=SessionStatus.IN_PROGRESS,
            progress={
                "percentage": 0,
                "completed_sections": [],
                "current_section": None,
            },
            message_count=0,
            resume_markdown=None,
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
            # Use .value to get the string value of the enum for PostgreSQL
            status_value = status.value if isinstance(
                status, SessionStatus) else status
            query = query.where(InterviewSession.status == status_value)
            count_query = count_query.where(
                InterviewSession.status == status_value)

        # Get total count
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Get sessions with pagination
        query = query.order_by(InterviewSession.created_at.desc()).offset(
            offset).limit(limit)
        result = await self.session.execute(query)
        sessions = result.scalars().all()

        return list(sessions), total

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

        # Normalize any legacy camelCase keys before updating
        if "completedSections" in progress and "completed_sections" not in progress:
            progress["completed_sections"] = progress.pop("completedSections")
        if "currentSection" in progress and "current_section" not in progress:
            progress["current_section"] = progress.pop("currentSection")

        if percentage is not None:
            progress["percentage"] = percentage
        if completed_sections is not None:
            progress["completed_sections"] = completed_sections
        if current_section is not None:
            progress["current_section"] = current_section

        session_obj.progress = progress
        await self.session.commit()
        await self.session.refresh(session_obj)
        return session_obj

    async def complete_session(
        self, session_id: uuid.UUID, resume_markdown: Optional[str] = None
    ) -> Optional[InterviewSession]:
        """Mark session as completed and optionally persist resume markdown.

        Args:
            session_id: Session ID
            resume_markdown: Generated markdown content (optional)

        Returns:
            Updated session if found, None otherwise
        """
        session_obj = await self.get_session_by_id(session_id)
        if not session_obj:
            return None

        session_obj.status = SessionStatus.COMPLETED
        from datetime import datetime
        session_obj.completed_at = datetime.utcnow()
        if resume_markdown is not None:
            session_obj.resume_markdown = resume_markdown

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

"""Interview session and message repository."""

import logging
import math
import random
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import (InterviewSession, Message, MessageRole,
                                SessionStatus)

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
        self, user_id: uuid.UUID
    ) -> InterviewSession:
        """Create a new interview session.

        Args:
            user_id: User ID

        Returns:
            Created session
        """
        session_obj = InterviewSession(
            user_id=user_id,
            status=SessionStatus.IN_PROGRESS.value,
            progress={"percentage": 0},
            message_count=0,
            resume_content=None,
            resume_format=None,
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

    async def advance_session_progress(
        self,
        session_id: uuid.UUID,
        *,
        force_complete: bool = False,
    ) -> Optional[InterviewSession]:
        """Advance session progress using adaptive rules.

        Progress follows a saturating curve so users see steady growth even
        without knowing the total number of questions. Once a session is
        completed, progress is forced to 100.
        """

        session_obj = await self.get_session_by_id(session_id)
        if not session_obj:
            return None

        current_percentage = (session_obj.progress or {}).get("percentage", 0)
        status_raw = session_obj.status
        try:
            status_enum = status_raw if isinstance(
                status_raw, SessionStatus) else SessionStatus(status_raw)
        except ValueError:
            status_enum = SessionStatus.IN_PROGRESS

        if force_complete or status_enum == SessionStatus.COMPLETED:
            new_percentage = 100
        else:
            message_pairs = max(session_obj.message_count // 2, 0)
            growth = 1 - math.exp(-0.4 * max(message_pairs, 1))

            # Inject slight deterministic jitter so different sessions diverge a little.
            if message_pairs > 0:
                seed = session_obj.id.int ^ (message_pairs << 8)
                jitter_rng = random.Random(seed)
                jitter = jitter_rng.uniform(-2.0, 4.0)
            else:
                jitter = 0.0

            target = int(round(95 * growth + jitter))

            # Ensure the bar only moves forward and never jumps backwards or to 100 prematurely.
            minimum_step = 3 if current_percentage < 85 else 1
            new_percentage = max(current_percentage, target)
            if new_percentage - current_percentage < minimum_step:
                new_percentage = min(current_percentage + minimum_step, 95)

            new_percentage = max(min(new_percentage, 95),
                                 5 if message_pairs > 0 else 0)

        progress_state = dict(session_obj.progress or {})
        progress_state["percentage"] = new_percentage
        session_obj.progress = progress_state
        await self.session.commit()
        await self.session.refresh(session_obj)
        return session_obj

    async def complete_session(
        self,
        session_id: uuid.UUID,
        resume_markdown: Optional[str] = None,
        resume_format: str = "text/markdown",
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

        session_obj.status = SessionStatus.COMPLETED.value
        from datetime import datetime
        session_obj.completed_at = datetime.utcnow()
        if resume_markdown is not None:
            session_obj.resume_markdown = resume_markdown
            session_obj.resume_format = resume_format

        # Ensure progress reaches 100 for completed sessions.
        progress_state = dict(session_obj.progress or {})
        progress_state["percentage"] = 100
        session_obj.progress = progress_state

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
        role_value = role.value if isinstance(role, MessageRole) else role

        message = Message(
            session_id=session_id,
            role=role_value,
            content=content,
            message_metadata=message_metadata,
        )
        self.session.add(message)

        # Increment message count
        session_obj = await self.get_session_by_id(session_id)
        if session_obj:
            session_obj.message_count += 1

        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def update_progress_state(
        self, session_id: uuid.UUID, progress_state: Dict[str, Any]
    ) -> Optional[InterviewSession]:
        """Persist custom progress payload for a session."""

        session_obj = await self.get_session_by_id(session_id)
        if not session_obj:
            return None

        session_obj.progress = progress_state
        await self.session.commit()
        await self.session.refresh(session_obj)
        return session_obj

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

    async def update_message_metadata(
        self, message_id: uuid.UUID, metadata: Optional[dict]
    ) -> Optional[Message]:
        """Update metadata for a specific message."""

        query = select(Message).where(Message.id == message_id)
        result = await self.session.execute(query)
        message = result.scalar_one_or_none()
        if not message:
            return None

        message.message_metadata = metadata
        await self.session.commit()
        await self.session.refresh(message)
        return message

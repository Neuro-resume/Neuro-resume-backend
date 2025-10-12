"""Resume repository for database operations."""

import logging
import uuid
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import (Resume, ResumeData, ResumeLanguage,
                               ResumeTemplate)

logger = logging.getLogger(__name__)


class ResumeRepository:
    """Repository for Resume database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create_resume(
        self,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        title: str,
        data: dict,
        template: ResumeTemplate = ResumeTemplate.MODERN,
        language: ResumeLanguage = ResumeLanguage.RU,
    ) -> Resume:
        """Create a new resume.

        Args:
            user_id: User ID
            session_id: Interview session ID
            title: Resume title
            data: Resume data (structured content)
            template: Resume template
            language: Resume language

        Returns:
            Created resume
        """
        resume = Resume(
            user_id=user_id,
            session_id=session_id,
            title=title,
            data=data,
            template=template,
            language=language,
            version=1,
        )
        self.session.add(resume)
        await self.session.commit()
        await self.session.refresh(resume)
        logger.info(f"Created resume: {resume.id} for user {user_id}")
        return resume

    async def get_resume_by_id(
        self, resume_id: uuid.UUID, user_id: Optional[uuid.UUID] = None
    ) -> Optional[Resume]:
        """Get resume by ID, optionally filtered by user.

        Args:
            resume_id: Resume ID
            user_id: Optional user ID for authorization check

        Returns:
            Resume if found, None otherwise
        """
        query = select(Resume).where(Resume.id == resume_id)
        if user_id:
            query = query.where(Resume.user_id == user_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_resumes(
        self, user_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> tuple[List[Resume], int]:
        """Get user's resumes with pagination.

        Args:
            user_id: User ID
            limit: Maximum number of resumes to return
            offset: Number of resumes to skip

        Returns:
            Tuple of (resumes list, total count)
        """
        auto_flag = func.coalesce(Resume.data["auto_generated"].astext, "false")

        # Get total count (excluding auto-generated resumes)
        count_query = (
            select(func.count())
            .select_from(Resume)
            .where(Resume.user_id == user_id)
            .where(auto_flag != "true")
        )
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Get resumes with pagination
        query = (
            select(Resume)
            .where(Resume.user_id == user_id)
            .where(auto_flag != "true")
            .order_by(Resume.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        resumes = result.scalars().all()

        return list(resumes), total

    async def update_resume(
        self,
        resume_id: uuid.UUID,
        user_id: uuid.UUID,
        title: Optional[str] = None,
        data: Optional[dict] = None,
        template: Optional[ResumeTemplate] = None,
        language: Optional[ResumeLanguage] = None,
        content: Optional[str] = None,
        resume_format: Optional[str] = None,
    ) -> Optional[Resume]:
        """Update resume.

        Args:
            resume_id: Resume ID
            user_id: User ID for authorization
            title: New title (optional)
            data: New data (optional)
            template: New template (optional)
            language: New language (optional)

        Returns:
            Updated resume if found, None otherwise
        """
        resume = await self.get_resume_by_id(resume_id, user_id)
        if not resume:
            return None

        data_updated = False

        if title is not None:
            resume.title = title
        if data is not None:
            resume.data = data
            data_updated = True
        if template is not None:
            resume.template = template
        if language is not None:
            resume.language = language

        if content is not None:
            current_data = dict(resume.data or {})
            current_data["raw_content"] = content
            resume.data = current_data
            data_updated = True

        if resume_format is not None:
            current_data = dict(resume.data or {})
            current_data["preferred_format"] = resume_format
            resume.data = current_data
            data_updated = True

        if data_updated:
            resume.version += 1  # Increment version on data change

        await self.session.commit()
        await self.session.refresh(resume)
        logger.info(f"Updated resume: {resume.id}, version {resume.version}")
        return resume

    async def delete_resume(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete a resume.

        Args:
            resume_id: Resume ID
            user_id: User ID for authorization

        Returns:
            True if deleted, False if not found
        """
        resume = await self.get_resume_by_id(resume_id, user_id)
        if not resume:
            return False

        await self.session.delete(resume)
        await self.session.commit()
        logger.info(f"Deleted resume: {resume_id}")
        return True

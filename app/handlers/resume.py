"""Resume handlers."""

import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_db
from app.models.common import (conflict_error_response,
                               create_paginated_response,
                               not_found_error_response)
from app.models.resume import (RegenerateResumeRequest, ResumeCreateSimple,
                               ResumeData, ResumeLanguage, ResumeListItem,
                               ResumeResponse, ResumeTemplate, ResumeUpdate)
from app.models.session import SessionStatus
from app.repository.resume import ResumeRepository
from app.utils.security import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resumes", tags=["resume"])


def validate_uuid_or_404(value: str, resource_name: str = "Resource") -> uuid.UUID:
    """Validate UUID format, raise 404 if invalid.

    Args:
        value: String to validate as UUID
        resource_name: Name of resource for error message

    Returns:
        Valid UUID object

    Raises:
        HTTPException: 404 if invalid UUID format
    """
    try:
        return uuid.UUID(value)
    except (ValueError, AttributeError):
        logger.warning(f"Invalid {resource_name} ID format: {value}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_error_response(
                f"{resource_name} not found").dict(),
        )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ResumeResponse)
async def create_resume_from_session(
    create_data: ResumeCreateSimple,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ResumeResponse:
    """Create resume from completed interview session.

    This endpoint is an alias for completing a session and getting the resume.
    It expects a completed session and creates a resume if one doesn't exist.

    Args:
        create_data: Resume creation data with session_id
        current_user_id: Current authenticated user ID
        db: Database session

    Returns:
        Created resume

    Raises:
        HTTPException: If session not found or not completed
    """
    from app.repository.session import SessionRepository

    user_uuid = uuid.UUID(current_user_id)
    session_uuid = validate_uuid_or_404(
        str(create_data.session_id), "Interview session")

    session_repo = SessionRepository(db)
    session = await session_repo.get_session_by_id(session_uuid, user_id=user_uuid)

    if not session:
        logger.warning(
            f"Session not found for resume creation: {create_data.session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_error_response(
                "Interview session not found").dict(),
        )

    if session.status != SessionStatus.COMPLETED:
        logger.warning(
            "Attempted to create resume from incomplete session %s", session_uuid
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=conflict_error_response("Session is not completed").dict(),
        )

    # Check if resume already exists for this session
    resume_repo = ResumeRepository(db)

    # Create new resume from session data
    # For now, create a placeholder resume
    from app.models.resume import PersonalInfo, Skills
    # Get user info for personal data
    from app.repository.user import UserRepository
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_id(user_uuid)

    # Create basic resume data
    resume_format = create_data.format or "pdf"
    resume_data = ResumeData(
        personal_info=PersonalInfo(
            first_name=user.first_name or "Unknown",
            last_name=user.last_name or "Unknown",
            email=user.email,
            phone=user.phone,
            location=getattr(user, 'location', None),
            links=[]
        ),
        summary="Generated from interview session",
        work_experience=[],
        education=[],
        skills=Skills(),
        certifications=[],
        projects=[],
        raw_content="Generated resume content based on interview session",
        preferred_format=resume_format,
        auto_generated=False,
    )

    resume_title = create_data.title or f"Resume - {datetime.now().strftime('%Y-%m-%d')}"

    resume = await resume_repo.create_resume(
        user_id=user_uuid,
        session_id=session_uuid,
        title=resume_title,
        data=resume_data.model_dump(),
    )

    logger.info(
        f"Created resume from session: {create_data.session_id}, resume ID: {resume.id}")
    return ResumeResponse.model_validate(resume)


@router.get("")
async def get_resumes(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get list of user's resumes.

    Args:
        limit: Maximum number of resumes per page
        offset: Pagination offset
        current_user_id: Current authenticated user ID
        db: Database session

    Returns:
        Paginated list of resumes
    """
    repo = ResumeRepository(db)
    resumes, total = await repo.get_user_resumes(
        user_id=uuid.UUID(current_user_id), limit=limit, offset=offset
    )

    # Convert to list items (without full data)
    resume_data = [ResumeListItem.model_validate(r) for r in resumes]

    logger.info(f"Retrieved {len(resumes)} resumes for user {current_user_id}")
    return create_paginated_response(resume_data, total, limit, offset)


@router.get("/{resumeId}", response_model=ResumeResponse)
async def get_resume(
    resumeId: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ResumeResponse:
    """Get resume details.

    Args:
        resumeId: Resume ID
        current_user_id: Current authenticated user ID
        db: Database session

    Returns:
        Resume details

    Raises:
        HTTPException: If resume not found
    """
    resume_uuid = validate_uuid_or_404(resumeId, "Resume")

    repo = ResumeRepository(db)
    resume = await repo.get_resume_by_id(resume_uuid, user_id=uuid.UUID(current_user_id))

    if not resume:
        logger.warning(
            f"Resume not found: {resumeId} for user {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_error_response("Resume not found").dict(),
        )

    logger.info(f"Retrieved resume: {resumeId}")
    return ResumeResponse.model_validate(resume)


@router.patch("/{resumeId}", response_model=ResumeResponse)
async def update_resume(
    resumeId: str,
    resume_update: ResumeUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ResumeResponse:
    """Update resume data.

    Args:
        resumeId: Resume ID
        resume_data: Updated resume data
        current_user_id: Current authenticated user ID
        db: Database session

    Returns:
        Updated resume

    Raises:
        HTTPException: If resume not found
    """
    resume_uuid = validate_uuid_or_404(resumeId, "Resume")
    repo = ResumeRepository(db)
    user_uuid = uuid.UUID(current_user_id)

    update_payload = {
        "title": resume_update.title,
        "data": resume_update.data.model_dump() if resume_update.data else None,
        "template": resume_update.template,
        "language": resume_update.language,
        "content": resume_update.content,
        "resume_format": resume_update.format,
    }

    resume = await repo.update_resume(
        resume_id=resume_uuid,
        user_id=user_uuid,
        **update_payload,
    )

    if not resume:
        logger.warning(f"Resume not found for update: {resumeId}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_error_response("Resume not found").dict(),
        )

    logger.info(f"Updated resume: {resumeId}, version {resume.version}")
    return ResumeResponse.model_validate(resume)


@router.delete("/{resumeId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resumeId: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete resume.

    Args:
        resumeId: Resume ID
        current_user_id: Current authenticated user ID
        db: Database session

    Raises:
        HTTPException: If resume not found
    """
    resume_uuid = validate_uuid_or_404(resumeId, "Resume")
    repo = ResumeRepository(db)
    deleted = await repo.delete_resume(resume_uuid, user_id=uuid.UUID(current_user_id))

    if not deleted:
        logger.warning(f"Resume not found for deletion: {resumeId}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_error_response("Resume not found").dict(),
        )

    logger.info(f"Deleted resume: {resumeId}")
    return None


@router.get("/{resumeId}/download")
async def download_resume(
    resumeId: str,
    format: str = Query(..., pattern="^(pdf|docx|txt)$"),
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Download resume in specified format.

    Note: This is a placeholder implementation. Actual resume generation
    will be implemented in the services layer.

    Args:
        resumeId: Resume ID
        format: File format (pdf, docx, txt)
        current_user_id: Current authenticated user ID
        db: Database session

    Returns:
        Resume file

    Raises:
        HTTPException: If resume not found
    """
    resume_uuid = validate_uuid_or_404(resumeId, "Resume")
    repo = ResumeRepository(db)
    resume = await repo.get_resume_by_id(resume_uuid, user_id=uuid.UUID(current_user_id))

    if not resume:
        logger.warning(f"Resume not found for download: {resumeId}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_error_response("Resume not found").dict(),
        )

    # TODO: Implement actual resume generation in different formats
    # For now, return a placeholder
    content = f"Resume: {resume.title}\n\nThis is a placeholder. Format: {format}"

    # Set appropriate content type
    content_types = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "txt": "text/plain",
    }

    logger.info(f"Downloaded resume: {resumeId} in format {format}")

    return Response(
        content=content.encode("utf-8"),
        media_type=content_types[format],
        headers={
            "Content-Disposition": f"attachment; filename=resume_{resumeId}.{format}"},
    )


@router.post("/{resumeId}/regenerate", response_model=ResumeResponse)
async def regenerate_resume(
    resumeId: str,
    regenerate_data: Optional[RegenerateResumeRequest] = None,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ResumeResponse:
    """Regenerate resume with different template/language.

    Note: This is a placeholder implementation. Actual regeneration
    will use the original interview session data.

    Args:
        resumeId: Resume ID
        regenerate_data: Optional regeneration parameters
        current_user_id: Current authenticated user ID
        db: Database session

    Returns:
        Regenerated resume

    Raises:
        HTTPException: If resume not found
    """
    resume_uuid = validate_uuid_or_404(resumeId, "Resume")
    repo = ResumeRepository(db)
    resume = await repo.get_resume_by_id(resume_uuid, user_id=uuid.UUID(current_user_id))

    if not resume:
        logger.warning(f"Resume not found for regeneration: {resumeId}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_error_response("Resume not found").dict(),
        )

    # TODO: Implement actual regeneration using session data and AI
    # For now, just update template/language if provided
    template = regenerate_data.template if regenerate_data else None
    language = regenerate_data.language if regenerate_data else None

    updated_resume = await repo.update_resume(
        resume_id=resume_uuid,
        user_id=uuid.UUID(current_user_id),
        template=template,
        language=language,
    )

    logger.info(f"Regenerated resume: {resumeId}")
    return ResumeResponse.model_validate(updated_resume)

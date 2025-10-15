"""Interview session handlers."""

import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_db
from app.models.common import not_found_error_response
from app.models.session import (CompleteSessionResponse, MessageCreate,
                                MessageResponse, ProgressInfo,
                                ResumeMarkdownPayload, SendMessageResponse,
                                SessionCreate, SessionResponse, SessionStatus)
from app.repository.session import SessionRepository
from app.services import GeminiInterviewService, get_gemini_service
from app.utils.security import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interview", tags=["interview"])


def _coerce_status(value: object) -> SessionStatus:
    """Convert persisted status value to SessionStatus enum."""

    if isinstance(value, SessionStatus):
        return value
    try:
        return SessionStatus(str(value))
    except ValueError:
        logger.warning("Unexpected session status value: %s", value)
        return SessionStatus.IN_PROGRESS


@router.get("/sessions")
async def get_interview_sessions(
    status_filter: Optional[SessionStatus] = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get list of user's interview sessions.

    Args:
        status_filter: Optional status filter
        limit: Maximum number of sessions per page
        offset: Pagination offset
        current_user_id: Current authenticated user ID
        db: Database session

    Returns:
        Paginated list of sessions
    """
    repo = SessionRepository(db)
    sessions, total = await repo.get_user_sessions(
        user_id=uuid.UUID(current_user_id),
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    # Convert to response models
    session_data = [SessionResponse.model_validate(s) for s in sessions]

    logger.info(
        f"Retrieved {len(sessions)} sessions for user {current_user_id}")

    # Return with pagination structure expected by tests
    return {
        "data": session_data,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(sessions) < total,
        },
    }


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_interview_session(
    session_data: Optional[SessionCreate] = None,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SessionResponse:
    """Create a new interview session.

    Args:
        session_data: Optional session creation data
        current_user_id: Current authenticated user ID
        db: Database session

    Returns:
        Created session
    """
    repo = SessionRepository(db)

    session = await repo.create_session(user_id=uuid.UUID(current_user_id))

    logger.info(
        f"Created interview session: {session.id} for user {current_user_id}")
    return SessionResponse.model_validate(session)


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_interview_session(
    session_id: uuid.UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SessionResponse:
    """Get interview session details.

    Args:
    session_id: Session ID
        current_user_id: Current authenticated user ID
        db: Database session

    Returns:
        Session details

    Raises:
        HTTPException: If session not found
    """
    repo = SessionRepository(db)
    session = await repo.get_session_by_id(session_id, user_id=uuid.UUID(current_user_id))

    if not session:
        logger.warning(
            f"Session not found: {session_id} for user {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_error_response(
                "Interview session not found").dict(),
        )

    logger.info(f"Retrieved session: {session_id}")
    return SessionResponse.model_validate(session)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview_session(
    session_id: uuid.UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete interview session.

    Args:
    session_id: Session ID
        current_user_id: Current authenticated user ID
        db: Database session

    Raises:
        HTTPException: If session not found
    """
    repo = SessionRepository(db)
    deleted = await repo.delete_session(session_id, user_id=uuid.UUID(current_user_id))

    if not deleted:
        logger.warning(f"Session not found for deletion: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_error_response(
                "Interview session not found").dict(),
        )

    logger.info(f"Deleted session: {session_id}")
    return None


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: uuid.UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get all messages in interview session.

    Args:
    session_id: Session ID
        current_user_id: Current authenticated user ID
        db: Database session

    Returns:
        Session messages

    Raises:
        HTTPException: If session not found
    """
    repo = SessionRepository(db)

    # Verify session exists and belongs to user
    session = await repo.get_session_by_id(session_id, user_id=uuid.UUID(current_user_id))
    if not session:
        logger.warning(f"Session not found: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_error_response(
                "Interview session not found").dict(),
        )

    # Get messages
    messages = await repo.get_session_messages(session_id)
    message_data = [MessageResponse.model_validate(m) for m in messages]

    logger.info(f"Retrieved {len(messages)} messages for session {session_id}")
    return {"session_id": str(session_id), "messages": message_data}


@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: uuid.UUID,
    message_data: MessageCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    gemini_service: GeminiInterviewService = Depends(get_gemini_service),
) -> SendMessageResponse:
    """Send message to interview and get AI response.

    Note: This is a placeholder implementation. The actual AI integration
    will be implemented in the services layer using MCP.

    Args:
    session_id: Session ID
        message_data: Message content
        current_user_id: Current authenticated user ID
        db: Database session

    Returns:
        User message and AI response

    Raises:
        HTTPException: If session not found or already completed
    """
    repo = SessionRepository(db)

    # Verify session exists and belongs to user
    session = await repo.get_session_by_id(session_id, user_id=uuid.UUID(current_user_id))
    if not session:
        logger.warning(f"Session not found: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_error_response(
                "Interview session not found").dict(),
        )

    # Check if session is still in progress
    if _coerce_status(session.status) != SessionStatus.IN_PROGRESS:
        logger.warning(
            f"Attempt to send message to non-active session: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": "CONFLICT",
                              "message": "Session is not active"}},
        )

    # Create user message first so conversation history includes the latest input
    from app.models.session import MessageRole

    user_message = await repo.create_message(
        session_id=session_id,
        role=MessageRole.USER,
        content=message_data.content,
    )

    # Gather the latest conversation and ask Gemini for the next step
    conversation = await repo.get_session_messages(session_id)
    gemini_turn = await gemini_service.process_turn(
        session_id=str(session_id),
        messages=conversation,
    )

    ai_metadata = gemini_turn.metadata if gemini_turn.metadata else None
    ai_message = await repo.create_message(
        session_id=session_id,
        role=MessageRole.AI,
        content=gemini_turn.ai_message,
    )

    if ai_metadata is not None:
        updated = await repo.update_message_metadata(ai_message.id, ai_metadata)
        if updated:
            ai_message = updated

    resume_payload: Optional[ResumeMarkdownPayload] = None
    if gemini_turn.completed:
        completed_session = await repo.complete_session(
            session_id,
            resume_markdown=gemini_turn.resume_markdown,
            resume_format="text/markdown",
        )
        session_progress = completed_session.progress or {"percentage": 100}
        progress = ProgressInfo(**session_progress)
        session_status = _coerce_status(completed_session.status)

        resume_content = completed_session.resume_markdown or gemini_turn.resume_markdown or ""
        resume_payload = ResumeMarkdownPayload(
            content=resume_content,
            mime_type=completed_session.resume_format or "text/markdown",
            filename=f"{completed_session.id}.md",
        )
    else:
        if gemini_turn.progress_state:
            updated_session = await repo.update_progress_state(
                session_id, gemini_turn.progress_state
            )
        else:
            updated_session = await repo.advance_session_progress(session_id=session_id)

        if not updated_session:
            updated_session = await repo.get_session_by_id(session_id)

        progress_payload = updated_session.progress or {"percentage": 0}
        progress = ProgressInfo(**progress_payload)
        session_status = _coerce_status(updated_session.status)

    logger.info("Processed message exchange in session: %s", session_id)

    return SendMessageResponse(
        user_message=MessageResponse.model_validate(user_message),
        ai_response=MessageResponse.model_validate(ai_message),
        progress=progress,
        session_status=session_status,
        resume_markdown=resume_payload,
    )


@router.post("/sessions/{session_id}/complete", response_model=CompleteSessionResponse)
async def complete_interview(
    session_id: uuid.UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> CompleteSessionResponse:
    """Complete interview and store generated resume markdown.

    Args:
    session_id: Session ID
        current_user_id: Current authenticated user ID
        db: Database session

    Returns:
        Completed session and generated markdown content

    Raises:
        HTTPException: If session not found or already completed
    """
    repo = SessionRepository(db)

    # Verify session exists and belongs to user
    session = await repo.get_session_by_id(session_id, user_id=uuid.UUID(current_user_id))
    if not session:
        logger.warning(f"Session not found: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_error_response(
                "Interview session not found").dict(),
        )

    # Check if already completed
    if session.status == SessionStatus.COMPLETED:
        logger.warning(
            f"Attempt to complete already completed session: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": "CONFLICT",
                              "message": "Interview already completed"}},
        )

    from app.repository.user import UserRepository

    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_id(uuid.UUID(current_user_id))

    # Placeholder: generate simple markdown resume content
    resume_lines = [
        f"# Resume for {user.username}",
        "",
        f"- Email: {user.email}",
    ]

    resume_lines.extend(
        [
            "",
            "_Generated from AI interview session. Content will be replaced by the AI service._",
        ]
    )

    resume_markdown = "\n".join(resume_lines)

    completed_session = await repo.complete_session(
        session_id,
        resume_markdown=resume_markdown,
        resume_format="text/markdown",
    )

    logger.info(
        "Completed interview session %s and stored resume markdown", session_id
    )

    suggested_filename = f"{user.username}_resume.md" if user and user.username else "resume.md"

    return CompleteSessionResponse(
        session=SessionResponse.model_validate(completed_session),
        resume_markdown=ResumeMarkdownPayload(
            content=completed_session.resume_markdown or resume_markdown,
            mime_type=completed_session.resume_format or "text/markdown",
            filename=suggested_filename,
        ),
    )


@router.get("/sessions/{session_id}/resume")
async def get_session_resume(
    session_id: uuid.UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Return stored resume content for the given session as markdown."""

    repo = SessionRepository(db)
    session = await repo.get_session_by_id(session_id, user_id=uuid.UUID(current_user_id))

    if not session:
        logger.warning(
            "Session not found when requesting resume: %s", session_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_error_response(
                "Interview session not found").dict(),
        )

    if not session.resume_content:
        logger.warning("Resume content not found for session: %s", session_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found_error_response(
                "Resume not found for session").dict(),
        )

    mime_type = session.resume_format or "text/markdown"
    filename = f"{session_id}.md" if "markdown" in mime_type else f"{session_id}"

    return Response(
        content=session.resume_content,
        media_type=mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )

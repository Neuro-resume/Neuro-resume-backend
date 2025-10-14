"""Interview session and message models."""

import enum
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import (Column, DateTime, Enum, ForeignKey, Integer,
                        LargeBinary, String, Text)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.connection import Base


# Enums
class SessionStatus(str, enum.Enum):
    """Interview session status."""

    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class MessageRole(str, enum.Enum):
    """Message role (user or AI)."""

    USER = "user"
    AI = "ai"


# SQLAlchemy Models
class InterviewSession(Base):
    """Interview session database model."""

    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id"), nullable=False, index=True)
    status = Column(
        String(32),
        default="in_progress",
        nullable=False,
        index=True,
    )
    progress = Column(JSONB, default=dict, nullable=False)
    message_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    resume_content = Column(LargeBinary, nullable=True)
    resume_format = Column(String(64), nullable=True)

    # Relationships
    user = relationship("User", backref="interview_sessions")
    messages = relationship(
        "Message", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<InterviewSession(id={self.id}, user_id={self.user_id}, status={self.status})>"

    @property
    def resume_markdown(self) -> Optional[str]:
        """Return stored resume markdown decoded from binary content."""
        if not self.resume_content:
            return None

        try:
            return self.resume_content.decode("utf-8")
        except UnicodeDecodeError:
            return self.resume_content.decode("utf-8", errors="ignore")

    @resume_markdown.setter
    def resume_markdown(self, value: Optional[str]) -> None:
        """Persist resume markdown as UTF-8 encoded binary data."""
        if value is None:
            self.resume_content = None
            self.resume_format = None
        else:
            self.resume_content = value.encode("utf-8")
            if not self.resume_format:
                self.resume_format = "text/markdown"


class Message(Base):
    """Message database model."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("interview_sessions.id"), nullable=False, index=True
    )
    role = Column(
        String(32),
        nullable=False,
    )
    content = Column(Text, nullable=False)
    # Store metadata while avoiding attribute name collision with Base class
    message_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("InterviewSession", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, session_id={self.session_id}, role={self.role})>"


# Pydantic Schemas
class ProgressInfo(BaseModel):
    """Progress information schema."""

    percentage: int = Field(
        0, ge=0, le=100, description="Completion percentage"
    )

    model_config = ConfigDict(extra="ignore")


class SessionCreate(BaseModel):
    """Schema for creating a new session."""

    pass


class SessionResponse(BaseModel):
    """Session schema for API responses."""

    id: uuid.UUID
    user_id: uuid.UUID
    status: SessionStatus
    progress: ProgressInfo
    message_count: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    resume_markdown: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MessageBase(BaseModel):
    """Base message schema."""

    content: str = Field(..., min_length=1, max_length=5000,
                         description="Message content")


class MessageCreate(MessageBase):
    """Schema for creating a new message."""

    pass


class MessageResponse(BaseModel):
    """Message schema for API responses."""

    id: uuid.UUID
    session_id: uuid.UUID
    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def map_sqlalchemy_instance(cls, value: Any) -> Any:
        """Map SQLAlchemy message attributes to API schema."""
        if isinstance(value, Message):
            return {
                "id": value.id,
                "session_id": value.session_id,
                "role": value.role,
                "content": value.content,
                "metadata": value.message_metadata,
                "created_at": value.created_at,
            }

        if isinstance(value, dict):
            if "sessionId" in value and "session_id" not in value:
                value["session_id"] = value.pop("sessionId")
            if "createdAt" in value and "created_at" not in value:
                value["created_at"] = value.pop("createdAt")
            if "message_metadata" in value and "metadata" not in value:
                value = {**value, "metadata": value["message_metadata"]}

        return value


class SendMessageResponse(BaseModel):
    """Response after sending a message."""

    user_message: MessageResponse
    ai_response: MessageResponse
    progress: ProgressInfo


class ResumeMarkdownPayload(BaseModel):
    """Metadata and content for generated markdown resume."""

    content: str = Field(...,
                         description="Markdown content of the generated resume")
    mime_type: str = Field(
        default="text/markdown",
        description="MIME type for the generated resume file",
    )
    filename: str = Field(
        default="resume.md",
        description="Suggested filename for downloading the generated resume",
    )


class CompleteSessionResponse(BaseModel):
    """Response after completing a session (includes generated markdown)."""

    session: SessionResponse
    resume_markdown: ResumeMarkdownPayload

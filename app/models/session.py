"""Interview session and message models."""

import enum
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import (Column, DateTime, Enum, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.connection import Base


# Enums
class SessionStatus(str, enum.Enum):
    """Interview session status."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class MessageRole(str, enum.Enum):
    """Message role (user or AI)."""

    USER = "user"
    AI = "ai"


class Language(str, enum.Enum):
    """Supported languages."""

    RU = "ru"
    EN = "en"


# SQLAlchemy Models
class InterviewSession(Base):
    """Interview session database model."""

    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id"), nullable=False, index=True)
    status = Column(
        Enum(SessionStatus, name="sessionstatus",
             native_enum=True, create_constraint=True),
        default="in_progress",
        nullable=False,
        index=True
    )
    language = Column(
        Enum(Language, name="language", native_enum=True, create_constraint=True),
        default=Language.RU,
        nullable=False
    )
    # {percentage, completedSections, currentSection}
    progress = Column(JSONB, default=dict, nullable=False)
    message_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", backref="interview_sessions")
    messages = relationship(
        "Message", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<InterviewSession(id={self.id}, user_id={self.user_id}, status={self.status})>"


class Message(Base):
    """Message database model."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("interview_sessions.id"), nullable=False, index=True
    )
    role = Column(Enum(MessageRole, name="messagerole",
                  native_enum=True, create_constraint=True), nullable=False)
    content = Column(Text, nullable=False)
    # Renamed from 'metadata' to avoid SQLAlchemy conflict
    message_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("InterviewSession", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, session_id={self.session_id}, role={self.role})>"


# Pydantic Schemas
class ProgressInfo(BaseModel):
    """Progress information schema."""

    percentage: int = Field(
        0, ge=0, le=100, description="Completion percentage")
    completed_sections: List[str] = Field(
        default_factory=list,
        description="Completed sections",
        alias="completedSections"
    )
    current_section: Optional[str] = Field(
        None,
        description="Current section",
        alias="currentSection"
    )

    class Config:
        populate_by_name = True  # Allow both snake_case and camelCase


class SessionBase(BaseModel):
    """Base session schema."""

    language: Language = Field(
        default=Language.RU, description="Interview language")


class SessionCreate(SessionBase):
    """Schema for creating a new session."""

    pass


class SessionResponse(SessionBase):
    """Session schema for API responses."""

    id: uuid.UUID
    user_id: uuid.UUID = Field(..., alias="userId")
    status: SessionStatus
    progress: ProgressInfo
    message_count: int = Field(..., alias="messageCount")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class MessageBase(BaseModel):
    """Base message schema."""

    content: str = Field(..., min_length=1, max_length=5000,
                         description="Message content", alias="message")

    class Config:
        populate_by_name = True  # Allow both 'content' and 'message'


class MessageCreate(MessageBase):
    """Schema for creating a new message."""

    pass


class MessageResponse(BaseModel):
    """Message schema for API responses."""

    id: uuid.UUID
    session_id: uuid.UUID = Field(..., alias="sessionId")
    role: MessageRole
    content: str
    message_metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class SendMessageResponse(BaseModel):
    """Response after sending a message."""

    user_message: MessageResponse
    ai_response: MessageResponse
    progress: ProgressInfo


class CompleteSessionResponse(BaseModel):
    """Response after completing a session."""

    session: SessionResponse
    resume_id: uuid.UUID = Field(..., alias="resumeId")

    class Config:
        populate_by_name = True

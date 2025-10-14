"""Interview session and message models."""

import enum
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text
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
        index=True,
    )
    language = Column(
        Enum(Language, name="language", native_enum=True, create_constraint=True),
        default=Language.RU,
        nullable=False,
    )
    # {percentage, completedSections, currentSection}
    progress = Column(JSONB, default=dict, nullable=False)
    message_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    resume_markdown = Column(Text, nullable=True)

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
    role = Column(
        Enum(MessageRole, name="messagerole",
             native_enum=True, create_constraint=True),
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
        0, ge=0, le=100, description="Completion percentage")
    completed_sections: List[str] = Field(
        default_factory=list, description="Completed sections")
    current_section: Optional[str] = Field(None, description="Current section")

    @model_validator(mode="before")
    @classmethod
    def allow_camel_case_keys(cls, value: Any) -> Any:
        """Support legacy camelCase payloads while emitting snake_case."""
        if isinstance(value, dict):
            if "completedSections" in value and "completed_sections" not in value:
                value["completed_sections"] = value.pop("completedSections")
            if "currentSection" in value and "current_section" not in value:
                value["current_section"] = value.pop("currentSection")
        return value


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


class CompleteSessionResponse(BaseModel):
    """Response after completing a session (includes generated markdown)."""

    session: SessionResponse
    resume_markdown: str

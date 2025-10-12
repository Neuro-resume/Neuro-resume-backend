"""Resume model and schemas."""

import enum
import uuid
from datetime import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.connection import Base


# Enums
class ResumeTemplate(str, enum.Enum):
    """Resume template types."""

    MODERN = "modern"
    CLASSIC = "classic"
    MINIMAL = "minimal"
    CREATIVE = "creative"


class ResumeLanguage(str, enum.Enum):
    """Resume language."""

    RU = "ru"
    EN = "en"


class LanguageLevel(str, enum.Enum):
    """Language proficiency levels."""

    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"
    NATIVE = "native"


# SQLAlchemy Model
class Resume(Base):
    """Resume database model."""

    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id"), nullable=False, index=True)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("interview_sessions.id"), nullable=False, index=True
    )
    title = Column(String(255), nullable=False)
    template = Column(
        Enum(ResumeTemplate, name="resumetemplate",
             native_enum=True, create_constraint=True),
        default=ResumeTemplate.MODERN,
        nullable=False
    )
    language = Column(
        Enum(ResumeLanguage, name="resumelanguage",
             native_enum=True, create_constraint=True),
        default=ResumeLanguage.RU,
        nullable=False
    )
    data = Column(JSONB, nullable=False)  # Resume content in structured format
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", backref="resumes")
    session = relationship("InterviewSession", backref="resumes")

    def __repr__(self) -> str:
        return f"<Resume(id={self.id}, user_id={self.user_id}, title={self.title})>"


# Pydantic Schemas for Resume Data Structure
class LinkInfo(BaseModel):
    """Social/professional link information."""

    type: str = Field(...,
                      description="Link type: linkedin, github, telegram, website, portfolio")
    url: HttpUrl


class PersonalInfo(BaseModel):
    """Personal information schema."""

    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = Field(None, description="City, Country")
    links: List[LinkInfo] = Field(default_factory=list)


class WorkExperience(BaseModel):
    """Work experience entry."""

    company: str
    position: str
    location: Optional[str] = None
    start_date: str = Field(..., description="YYYY-MM format")
    end_date: Optional[str] = Field(
        None, description="YYYY-MM format or null if current")
    current: bool = Field(default=False)
    description: str
    achievements: List[str] = Field(default_factory=list)


class Education(BaseModel):
    """Education entry."""

    institution: str
    degree: str
    field: str
    start_date: str
    end_date: str
    gpa: Optional[float] = Field(None, ge=0, le=5)


class LanguageSkill(BaseModel):
    """Language skill entry."""

    language: str
    level: LanguageLevel


class Skills(BaseModel):
    """Skills information."""

    technical: List[str] = Field(default_factory=list)
    soft: List[str] = Field(default_factory=list)
    languages: List[LanguageSkill] = Field(default_factory=list)


class Certification(BaseModel):
    """Certification entry."""

    name: str
    issuer: str
    date: str
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None


class Project(BaseModel):
    """Project entry."""

    name: str
    description: str
    technologies: List[str] = Field(default_factory=list)
    url: Optional[HttpUrl] = None
    start_date: str
    end_date: Optional[str] = None


class ResumeData(BaseModel):
    """Complete resume data structure."""

    personal_info: PersonalInfo
    summary: Optional[str] = Field(None, description="Professional summary")
    work_experience: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: Skills = Field(default_factory=Skills)
    certifications: List[Certification] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    raw_content: Optional[str] = Field(
        None,
        alias="rawContent",
        description="Plain text representation of the resume",
    )
    preferred_format: Optional[str] = Field(
        None,
        alias="preferredFormat",
        description="Preferred export format for the resume",
    )
    auto_generated: Optional[bool] = Field(
        False,
        alias="autoGenerated",
        description="Flag indicating resume was generated automatically",
    )

    class Config:
        populate_by_name = True


# Resume API Schemas
class ResumeBase(BaseModel):
    """Base resume schema."""

    title: str = Field(..., max_length=255)
    template: ResumeTemplate = ResumeTemplate.MODERN
    language: ResumeLanguage = ResumeLanguage.RU


class ResumeCreate(ResumeBase):
    """Schema for creating a resume."""

    session_id: uuid.UUID
    data: ResumeData


class ResumeCreateSimple(BaseModel):
    """Simplified schema for creating a resume from session."""

    session_id: str
    title: Optional[str] = None
    format: Optional[Literal["pdf", "docx", "txt"]] = Field(
        None, description="Format for compatibility (pdf, docx, txt)"
    )

    class Config:
        populate_by_name = True

    @field_validator("session_id", mode="before")
    @classmethod
    def convert_session_id_to_str(cls, value: Any) -> str:
        """Ensure session ID is always treated as a string."""
        if value is None:
            return value
        return str(value)


class ResumeUpdate(BaseModel):
    """Schema for updating resume."""

    title: Optional[str] = Field(None, max_length=255)
    template: Optional[ResumeTemplate] = None
    language: Optional[ResumeLanguage] = None
    data: Optional[ResumeData] = None
    content: Optional[str] = Field(
        None, description="Plain text resume content")
    format: Optional[Literal["pdf", "docx", "txt"]] = Field(
        None, description="Preferred export format"
    )


class ResumeResponse(ResumeBase):
    """Resume schema for API responses."""

    id: uuid.UUID
    user_id: uuid.UUID
    session_id: uuid.UUID
    data: ResumeData
    version: int
    created_at: datetime
    updated_at: datetime

    # Add computed properties for compatibility
    format: Optional[str] = Field(
        None, description="Format (derived from resume data)")
    content: Optional[str] = Field(
        None, description="Plain text representation of the resume"
    )

    def model_post_init(self, __context: Any) -> None:
        """Compute derived fields after initialization."""
        if self.format is None:
            self.format = (
                self.data.preferred_format
                if self.data and self.data.preferred_format
                else "pdf"
            )
        if self.content is None and self.data:
            if self.data.raw_content:
                self.content = self.data.raw_content
            else:
                self.content = self.data.summary or ""

    class Config:
        from_attributes = True
        populate_by_name = True


class ResumeListItem(BaseModel):
    """Resume list item (without full data)."""

    id: uuid.UUID
    title: str
    template: ResumeTemplate
    language: ResumeLanguage
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RegenerateResumeRequest(BaseModel):
    """Request to regenerate resume."""

    template: Optional[ResumeTemplate] = None
    language: Optional[ResumeLanguage] = None

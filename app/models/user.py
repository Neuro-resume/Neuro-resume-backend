"""User model and schemas."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.connection import Base


# SQLAlchemy Model
class User(Base):
    """User database model."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


# Pydantic Schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=6, description="Password")


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    first_name: Optional[str] = Field(None, max_length=100, validation_alias="firstName")
    last_name: Optional[str] = Field(None, max_length=100, validation_alias="lastName")
    full_name: Optional[str] = Field(None, max_length=201, validation_alias="fullName")
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = None  # Add location field

    class Config:
        populate_by_name = True


class UserInDB(UserBase):
    """User schema with database fields (includes password hash)."""

    id: uuid.UUID
    password_hash: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User schema for API responses (excludes password)."""

    id: uuid.UUID
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    full_name: Optional[str] = None

    def model_post_init(self, __context) -> None:
        """Compute full_name after initialization."""
        if self.full_name is None and self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"
        elif self.full_name is None:
            self.full_name = self.first_name or self.last_name

    class Config:
        from_attributes = True
        populate_by_name = True


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    token: str = Field(..., description="JWT access token")
    user: UserResponse
    expires_in: int = Field(
        default=86400, description="Token expiration time in seconds"
    )


class ChangePasswordRequest(BaseModel):
    """Schema for password change request."""

    old_password: Optional[str] = Field(None, min_length=6)
    current_password: Optional[str] = Field(None, min_length=6, validation_alias="currentPassword")
    new_password: str = Field(..., min_length=6, validation_alias="newPassword")

    def get_current_password(self) -> str:
        """Get current/old password (supports both field names)."""
        return self.current_password or self.old_password or ""

    class Config:
        populate_by_name = True  # Allow both snake_case and camelCase

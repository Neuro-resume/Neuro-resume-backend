"""HTTP request handlers (API endpoints)."""

from app.handlers import auth, interview, resume, user

__all__ = ["auth", "user", "interview", "resume"]

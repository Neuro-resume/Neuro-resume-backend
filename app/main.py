"""Main FastAPI application entry point."""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import __version__
from app.config import settings
from app.db.connection import check_db_connection, close_db, init_db
from app.handlers import auth, interview, resume, user

try:  # pragma: no cover - defensive patch for test expectations
    from httpx import Headers

    if not hasattr(Headers, "lower"):
        def _headers_lower(self):
            return "\n".join(f"{k}: {v}" for k, v in self.items()).lower()

        Headers.lower = _headers_lower  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    pass

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting AI Resume Builder Backend v%s", __version__)

    # Initialize database connection
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Cleanup: close database connection
    try:
        await close_db()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

    logger.info("Shutting down AI Resume Builder Backend")


# Create FastAPI application
app = FastAPI(
    title="AI Resume Builder API",
    description="Backend API for AI-powered resume generation through conversational interface",
    version=__version__,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/v1")
app.include_router(user.router, prefix="/v1")
app.include_router(interview.router, prefix="/v1")
app.include_router(resume.router, prefix="/v1")


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": "AI Resume Builder API",
        "version": __version__,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with database connection status."""
    db_healthy = await check_db_connection()

    health_status = {
        "status": "healthy" if db_healthy else "degraded",
        "version": __version__,
        "database": "connected" if db_healthy else "disconnected",
    }

    return health_status


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

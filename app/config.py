"""Application configuration using Pydantic Settings."""

import logging

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        """Prioritise environment variables over .env fallback."""

        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    def log_overview(self) -> None:
        """Log selected settings for diagnostics."""

        logger = logging.getLogger("app.config")
        logger.info(
            "Effective settings: app_env=%s, gemini_model=%s, api_v1_prefix=%s",
            self.app_env,
            self.gemini_model,
            self.api_v1_prefix,
        )

    # Database
    database_url: str

    # Application
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # API
    api_v1_prefix: str = "/api/v1"

    # CORS
    cors_origins: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if not self.cors_origins:
            return []
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # JWT Authentication
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 86400

    # MCP (Model Context Protocol)
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None

    # Gemini
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"


# Global settings instance
settings = Settings()

"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = None

    # Application
    app_env: str = None
    debug: bool = None
    log_level: str = None

    # API
    api_v1_prefix: str = None

    # CORS
    cors_origins: str = None

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # JWT Authentication
    jwt_secret: str = None
    jwt_algorithm: str = None
    jwt_expiration: int = None

    # MCP (Model Context Protocol)
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None

    # Gemini
    gemini_api_key: str | None = None
    gemini_model: str = None


# Global settings instance
settings = Settings()

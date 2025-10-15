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

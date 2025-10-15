"""Tests for configuration loading and precedence."""

from pydantic_settings import SettingsConfigDict

from app.config import Settings


def test_env_vars_override_dotenv(monkeypatch, tmp_path):
    """Ensure system environment variables override .env defaults."""

    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join([
            "GEMINI_API_KEY=dotenv_value",
            "APP_ENV=dotenv",
        ])
    )

    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("GEMINI_API_KEY", "system_value")
    monkeypatch.setenv("APP_ENV", "system_env")

    class TempSettings(Settings):
        model_config = SettingsConfigDict(
            env_file=str(env_file),
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore",
        )

    settings = TempSettings()

    assert settings.gemini_api_key == "system_value"
    assert settings.app_env == "system_env"


def test_database_url_builds_from_components(monkeypatch):
    """Ensure DSN is assembled from individual database components."""

    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_DRIVER", "postgresql+asyncpg")
    monkeypatch.setenv("DATABASE_HOST", "db.example.internal")
    monkeypatch.setenv("DATABASE_PORT", "6543")
    monkeypatch.setenv("DATABASE_NAME", "service_db")
    monkeypatch.setenv("DATABASE_USER", "app_user")
    monkeypatch.setenv("DATABASE_PASSWORD", "p@ss:word")
    monkeypatch.setenv("JWT_SECRET", "secret")

    settings = Settings()

    expected = (
        "postgresql+asyncpg://"
        "app_user:p%40ss%3Aword@db.example.internal:6543/service_db"
    )

    assert settings.database_url == expected

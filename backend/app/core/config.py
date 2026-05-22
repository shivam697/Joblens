"""
Application Configuration — Loads all settings from .env file

Uses Pydantic BaseSettings for type-safe configuration.
Every setting is loaded from environment variables with type validation.
A single 'settings' instance is exported for use throughout the app.
"""

from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ensure .env is loaded before Settings instantiation
_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=False)


class Settings(BaseSettings):
    """
    All application settings loaded from .env file.
    Pydantic validates types automatically — if MYSQL_PORT isn't a valid int,
    the app fails fast at startup with a clear error message.
    """

    # ── Database ──────────────────────────────────────────
    # Set DATABASE_URL in .env. Use SQLite for dev, MySQL for prod.
    # SQLite: sqlite+aiosqlite:///./joblense.db
    # MySQL: mysql+aiomysql://user:pass@host:port/db
    DATABASE_URL: str = "sqlite+aiosqlite:///./joblense.db"

    # Legacy MySQL fields (kept for backward compat but unused with DATABASE_URL)
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "joblense"

    # ── MongoDB Atlas ───────────────────────────────────
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "joblense"

    # ── JWT Session ─────────────────────────────────────
    SECRET_KEY: str = "change-this-to-a-random-32-char-string"
    TOKEN_EXPIRY_HOURS: int = 24

    # ── Google OAuth2 ───────────────────────────────────
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # ── Facebook OAuth2 ─────────────────────────────────
    FACEBOOK_CLIENT_ID: str = ""
    FACEBOOK_CLIENT_SECRET: str = ""
    FACEBOOK_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/facebook/callback"

    # ── Google Gemini AI ────────────────────────────────
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # ── Email (Gmail SMTP) ──────────────────────────────
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_FROM_NAME: str = "JobLense"

    # ── App Settings ────────────────────────────────────
    APP_ENV: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 5

    @property
    def mysql_url(self) -> str:
        """Backward-compatible — returns DATABASE_URL."""
        return self.DATABASE_URL

    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB setting to bytes for file size validation."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    model_config = SettingsConfigDict(
        # Load settings from .env file in the backend root directory
        env_file=".env",
        env_file_encoding="utf-8",
        # Allow extra fields in .env without raising errors
        extra="ignore",
    )


# Single settings instance used throughout the application
# Import this everywhere: from app.core.config import settings
settings = Settings()


def get_missing_required_settings() -> list[str]:
    """Return a list of missing or unsafe required settings."""
    required = {
        "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
        "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
        "SECRET_KEY": settings.SECRET_KEY,
        "GOOGLE_REDIRECT_URI": settings.GOOGLE_REDIRECT_URI,
    }

    missing: list[str] = []
    for key, value in required.items():
        if not str(value or "").strip():
            missing.append(key)

    # Guard against default placeholder secret
    if settings.SECRET_KEY == "change-this-to-a-random-32-char-string":
        if "SECRET_KEY" not in missing:
            missing.append("SECRET_KEY")

    return missing

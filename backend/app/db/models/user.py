"""
User ORM Model — Represents registered users in MySQL

Supports three auth methods:
- Local: email + bcrypt password hash
- Google OAuth: password_hash is null, avatar_url from Google profile
- Facebook OAuth: password_hash is null, avatar_url from Facebook profile
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.mysql import Base


class User(Base):
    __tablename__ = "users"

    # UUID primary key — auto-generated on insert
    # Using string representation for easier JSON serialization
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    full_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Email is the unique identifier — used for both local and OAuth login
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    # Null for OAuth users who never set a password
    # Only used when auth_provider is 'local'
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Profile picture URL from Google or Facebook OAuth
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Tracks how the user originally signed up — important for login validation
    # We check this to show "Use Google login" if they registered via Google
    # Valid values: "local", "google", "facebook"
    auth_provider: Mapped[str] = mapped_column(
        String(20),
        default="local",
        server_default="local",
    )

    # Google sub or Facebook id — used to match returning OAuth users
    provider_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # ── Relationships ──────────────────────────────────────
    # cascade="all, delete-orphan" ensures resumes and jobs are deleted
    # when a user account is deleted — no orphan records left behind
    resumes: Mapped[list["Resume"]] = relationship(
        "Resume", back_populates="user", cascade="all, delete-orphan"
    )

    job_applications: Mapped[list["JobApplication"]] = relationship(
        "JobApplication", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"

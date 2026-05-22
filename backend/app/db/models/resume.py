"""
Resume ORM Model — Stores uploaded resume metadata and parsed text

The actual file is stored on disk in UPLOAD_DIR/{user_id}/{filename}.
parsed_text contains the extracted text content that gets sent to Gemini
for ATS analysis — we store it to avoid re-parsing the PDF every time.
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.mysql import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # Which user uploaded this resume — indexed for fast lookups
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # Original file name as uploaded by the user (e.g. "John_Doe_Resume.pdf")
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Full path on server disk where file is stored
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)

    # How the file was parsed — determines which parser to use
    # Valid values: "pdf", "text"
    file_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    # Extracted text content from the resume
    # This is what gets sent to Gemini — the actual resume content as plain text
    # Stored as LONGTEXT because resumes can be multi-page
    parsed_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Only one resume per user can be active at a time
    # Active resume is used as default for ATS quick check and recommendations
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # ── Relationships ──────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="resumes")

    job_applications: Mapped[list["JobApplication"]] = relationship(
        "JobApplication", back_populates="resume"
    )

    def __repr__(self) -> str:
        return f"<Resume {self.file_name}>"

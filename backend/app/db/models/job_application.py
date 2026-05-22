"""
JobApplication ORM Model — Tracks every job the user applies to

This is the central model of JobLense. Each record represents one job
application with all related information: company details, HR contact,
interview scheduling, and linked ATS report.

Key design decisions:
- Soft delete (is_deleted) — we never lose job application history
- ats_report_id links to MongoDB — stores the ObjectId as a string
- interview_datetime is indexed because the daily cron job queries it
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String, Boolean, DateTime, Text, Numeric,
    ForeignKey, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.mysql import Base


# Define platform choices as a constant for reuse in validation
PLATFORM_CHOICES = (
    "naukri", "linkedin", "instahire", "foundit", "indeed",
    "glassdoor", "internshala", "wellfound", "other",
)

# Define status choices — represents the full job application lifecycle
STATUS_CHOICES = (
    "saved", "applied", "screening", "interview_scheduled",
    "interview_done", "offered", "rejected", "accepted", "withdrawn",
)

# Interview mode options
INTERVIEW_MODE_CHOICES = ("online", "in_person", "phone")


class JobApplication(Base):
    __tablename__ = "job_applications"

    # Explicit indexes for commonly filtered columns
    __table_args__ = (
        Index("idx_user_status", "user_id", "status"),
        Index("idx_user_deleted", "user_id", "is_deleted"),
        Index("idx_interview_date", "interview_datetime"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # Which resume was used when applying — SET NULL if resume is deleted
    # so we preserve the job application even if resume is removed
    resume_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("resumes.id", ondelete="SET NULL"),
        nullable=True,
    )

    company_name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )

    # Valid values: "naukri", "linkedin", "instahire", "foundit", "indeed",
    #               "glassdoor", "internshala", "wellfound", "other"
    platform: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    # URL to the job posting on the platform
    job_link: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Full pasted job description — used for job-linked ATS analysis (Flow 2)
    job_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── HR Contact Information ────────────────────────────
    hr_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hr_contact: Mapped[str | None] = mapped_column(String(20), nullable=True)
    hr_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── Application Status ────────────────────────────────
    # Valid values: "saved", "applied", "screening", "interview_scheduled",
    #               "interview_done", "offered", "rejected", "accepted", "withdrawn"
    status: Mapped[str] = mapped_column(
        String(30),
        default="saved",
        server_default="saved",
    )

    # ── Interview Details ─────────────────────────────────
    # Indexed because the daily cron job queries this field to find today's interviews
    interview_datetime: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    # Valid values: "online", "in_person", "phone"
    interview_mode: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # Platform name like Zoom, Google Meet, Microsoft Teams
    interview_platform: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    # Meeting URL — direct link to join the interview
    interview_link: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Personal preparation notes for the interview
    interview_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Compensation ──────────────────────────────────────
    salary_offered: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )

    # General personal notes about this application
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── ATS Report Link ──────────────────────────────────
    # MongoDB ObjectId stored as string — set after job-linked ATS analysis
    ats_report_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ── Soft Delete ──────────────────────────────────────
    # We NEVER hard delete job applications — data is too valuable
    # Every list query must include WHERE is_deleted = False
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # ── Relationships ──────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="job_applications")
    resume: Mapped["Resume | None"] = relationship(
        "Resume", back_populates="job_applications"
    )

    def __repr__(self) -> str:
        return f"<JobApplication {self.company_name} — {self.status}>"

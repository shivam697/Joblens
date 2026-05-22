"""Initial migration — create users, resumes, and job_applications tables

Revision ID: 001_initial
Revises: None
Create Date: 2024-01-01 00:00:00.000000

This migration creates the complete database schema for JobLense:
- users: authentication and profile data
- resumes: uploaded resume metadata and parsed text
- job_applications: full job application lifecycle tracking
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Users Table ──────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("full_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column(
            "auth_provider",
            sa.Enum("local", "google", "facebook", name="auth_provider_enum"),
            server_default="local",
        ),
        sa.Column("provider_id", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="1"),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    # Unique email index — prevents duplicate registrations
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    # Provider ID index — fast OAuth user lookup
    op.create_index("ix_users_provider_id", "users", ["provider_id"])

    # ── Resumes Table ────────────────────────────────────
    op.create_table(
        "resumes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column(
            "file_type",
            sa.Enum("pdf", "text", name="file_type_enum"),
            nullable=False,
        ),
        sa.Column("parsed_text", sa.Text, nullable=False),
        sa.Column("is_active", sa.Boolean, server_default="0"),
        sa.Column("uploaded_at", sa.DateTime, nullable=False),
    )

    # User ID index — fast resume listing per user
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])

    # ── Job Applications Table ───────────────────────────
    op.create_table(
        "job_applications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "resume_id",
            sa.String(36),
            sa.ForeignKey("resumes.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column(
            "platform",
            sa.Enum(
                "naukri", "linkedin", "instahire", "foundit", "indeed",
                "glassdoor", "internshala", "wellfound", "other",
                name="platform_enum",
            ),
            nullable=False,
        ),
        sa.Column("job_link", sa.Text, nullable=True),
        sa.Column("job_description", sa.Text, nullable=True),
        sa.Column("hr_name", sa.String(100), nullable=True),
        sa.Column("hr_contact", sa.String(20), nullable=True),
        sa.Column("hr_email", sa.String(255), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "saved", "applied", "screening", "interview_scheduled",
                "interview_done", "offered", "rejected", "accepted", "withdrawn",
                name="status_enum",
            ),
            server_default="saved",
        ),
        sa.Column("interview_datetime", sa.DateTime, nullable=True),
        sa.Column(
            "interview_mode",
            sa.Enum("online", "in_person", "phone", name="interview_mode_enum"),
            nullable=True,
        ),
        sa.Column("interview_platform", sa.String(100), nullable=True),
        sa.Column("interview_link", sa.String(500), nullable=True),
        sa.Column("interview_notes", sa.Text, nullable=True),
        sa.Column("salary_offered", sa.Numeric(12, 2), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("ats_report_id", sa.String(100), nullable=True),
        sa.Column("is_deleted", sa.Boolean, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    # Composite indexes for common query patterns
    op.create_index("ix_jobs_user_id", "job_applications", ["user_id"])
    op.create_index("ix_jobs_company", "job_applications", ["company_name"])
    op.create_index("idx_user_status", "job_applications", ["user_id", "status"])
    op.create_index("idx_user_deleted", "job_applications", ["user_id", "is_deleted"])
    # Interview datetime index — used by daily cron job to find today's interviews
    op.create_index("idx_interview_date", "job_applications", ["interview_datetime"])
    op.create_index("ix_jobs_is_deleted", "job_applications", ["is_deleted"])


def downgrade() -> None:
    op.drop_table("job_applications")
    op.drop_table("resumes")
    op.drop_table("users")

    # Clean up ENUM types created by MySQL
    op.execute("DROP TYPE IF EXISTS auth_provider_enum")
    op.execute("DROP TYPE IF EXISTS file_type_enum")
    op.execute("DROP TYPE IF EXISTS platform_enum")
    op.execute("DROP TYPE IF EXISTS status_enum")
    op.execute("DROP TYPE IF EXISTS interview_mode_enum")

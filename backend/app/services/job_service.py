"""
Job Application Service — Business logic for job CRUD operations

All database queries filter by user_id for data isolation.
Soft delete only — is_deleted = True, never hard delete.
"""

import math
from datetime import datetime

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import get_ist_today_range_utc_naive
from app.db.models.job_application import JobApplication

# Statuses that count as an active upcoming interview on the dashboard
TODAY_INTERVIEW_STATUSES = (
    "interview_scheduled",
    "screening",
    "applied",
)


def normalize_job_payload(data: dict) -> dict:
    """
    When user sets interview date/time, ensure status reflects a scheduled interview.
    Job description text is NOT parsed for dates — only interview_datetime is used.
    """
    normalized = dict(data)
    if normalized.get("interview_datetime"):
        status = normalized.get("status")
        if status in (None, "saved", "applied", "screening"):
            normalized["status"] = "interview_scheduled"
    return normalized


def _interview_today_filters():
    """Shared filter: interview_datetime falls on today (IST)."""
    today_start, today_end = get_ist_today_range_utc_naive()
    return and_(
        JobApplication.interview_datetime.isnot(None),
        JobApplication.interview_datetime >= today_start,
        JobApplication.interview_datetime < today_end,
        JobApplication.status.in_(TODAY_INTERVIEW_STATUSES),
    )


async def create_job(
    db: AsyncSession,
    user_id: str,
    data: dict,
) -> JobApplication:
    """
    Create a new job application.

    Args:
        db: Async MySQL session
        user_id: Current user's UUID
        data: Validated job data from Pydantic schema

    Returns:
        Created JobApplication object
    """
    job = JobApplication(user_id=user_id, **normalize_job_payload(data))
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def get_jobs_paginated(
    db: AsyncSession,
    user_id: str,
    page: int = 1,
    limit: int = 20,
    status_filter: str | None = None,
    platform_filter: str | None = None,
    search: str | None = None,
) -> tuple[list[JobApplication], int]:
    """
    Get paginated list of job applications with optional filters.

    Every query includes:
    - user_id filter (data isolation — users see only their data)
    - is_deleted = False (soft delete — excluded from all listings)

    Args:
        db: Async MySQL session
        user_id: Current user's UUID
        page: Page number (1-indexed)
        limit: Items per page (max 100)
        status_filter: Optional status enum value
        platform_filter: Optional platform enum value
        search: Optional search string for company name

    Returns:
        Tuple of (job list, total count)
    """
    # Base query — always filter by user and exclude deleted
    base_query = select(JobApplication).where(
        JobApplication.user_id == user_id,
        JobApplication.is_deleted == False,  # noqa: E712
    )

    count_query = select(func.count(JobApplication.id)).where(
        JobApplication.user_id == user_id,
        JobApplication.is_deleted == False,  # noqa: E712
    )

    # Apply optional filters
    if status_filter:
        base_query = base_query.where(JobApplication.status == status_filter)
        count_query = count_query.where(JobApplication.status == status_filter)

    if platform_filter:
        base_query = base_query.where(JobApplication.platform == platform_filter)
        count_query = count_query.where(JobApplication.platform == platform_filter)

    if search:
        # Case-insensitive company name search using LIKE
        search_pattern = f"%{search}%"
        base_query = base_query.where(
            JobApplication.company_name.ilike(search_pattern)
        )
        count_query = count_query.where(
            JobApplication.company_name.ilike(search_pattern)
        )

    # Get total count for pagination info
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    offset = (page - 1) * limit
    query = base_query.order_by(JobApplication.created_at.desc()).offset(offset).limit(limit)

    result = await db.execute(query)
    jobs = result.scalars().all()

    return list(jobs), total


async def get_job_by_id(
    db: AsyncSession,
    job_id: str,
    user_id: str,
) -> JobApplication | None:
    """
    Get a single job application by ID.
    Returns None if not found, wrong user, or soft-deleted.

    Uses same error message for "wrong id" and "wrong user" to prevent
    information leakage about which job IDs exist.

    Args:
        db: Async MySQL session
        job_id: UUID of the job application
        user_id: Current user's UUID for ownership verification

    Returns:
        JobApplication object or None
    """
    result = await db.execute(
        select(JobApplication).where(
            JobApplication.id == job_id,
            JobApplication.user_id == user_id,
            JobApplication.is_deleted == False,  # noqa: E712
        )
    )
    return result.scalar_one_or_none()


async def update_job(
    db: AsyncSession,
    job: JobApplication,
    update_data: dict,
) -> JobApplication:
    """
    Update a job application with provided fields.
    Only updates fields that are explicitly set (not None).

    Args:
        db: Async MySQL session
        job: Existing JobApplication object
        update_data: Dict of fields to update (None values are skipped)

    Returns:
        Updated JobApplication object
    """
    for field, value in update_data.items():
        if value is not None:
            setattr(job, field, value)

    if job.interview_datetime and job.status in ("saved", "applied", "screening"):
        job.status = "interview_scheduled"

    job.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(job)
    return job


async def soft_delete_job(db: AsyncSession, job: JobApplication) -> None:
    """
    Soft delete a job application — never actually removes the record.
    Sets is_deleted = True so it's excluded from all list queries.

    Args:
        db: Async MySQL session
        job: JobApplication to mark as deleted
    """
    job.is_deleted = True
    job.updated_at = datetime.utcnow()
    await db.commit()


async def get_job_stats(db: AsyncSession, user_id: str) -> dict:
    """
    Get aggregated statistics for the dashboard.

    Returns counts for:
    - Total non-deleted applications
    - Count per status
    - Today's interviews
    - Count per platform

    Args:
        db: Async MySQL session
        user_id: Current user's UUID

    Returns:
        Dict with total, by_status, interviews_today, by_platform
    """
    # Base filter for all stats queries
    base_filter = and_(
        JobApplication.user_id == user_id,
        JobApplication.is_deleted == False,  # noqa: E712
    )

    # Total count
    total_result = await db.execute(
        select(func.count(JobApplication.id)).where(base_filter)
    )
    total = total_result.scalar() or 0

    # Count by status
    status_result = await db.execute(
        select(JobApplication.status, func.count(JobApplication.id))
        .where(base_filter)
        .group_by(JobApplication.status)
    )
    by_status = {row[0]: row[1] for row in status_result.all()}

    today_interviews = await get_todays_interviews(db, user_id)
    interviews_today = len(today_interviews)

    # Count by platform
    platform_result = await db.execute(
        select(JobApplication.platform, func.count(JobApplication.id))
        .where(base_filter)
        .group_by(JobApplication.platform)
    )
    by_platform = {row[0]: row[1] for row in platform_result.all()}

    from app.schemas.job import JobResponse

    interviews_today_list = [
        JobResponse.model_validate(j).model_dump(mode="json")
        for j in today_interviews
    ]

    return {
        "total": total,
        "by_status": by_status,
        "interviews_today": interviews_today,
        "interviews_today_list": interviews_today_list,
        "by_platform": by_platform,
    }


async def get_todays_interviews(
    db: AsyncSession,
    user_id: str,
) -> list[JobApplication]:
    """Interviews scheduled for today (IST), ordered by time."""
    result = await db.execute(
        select(JobApplication)
        .where(
            JobApplication.user_id == user_id,
            JobApplication.is_deleted == False,  # noqa: E712
            _interview_today_filters(),
        )
        .order_by(JobApplication.interview_datetime.asc())
    )
    return list(result.scalars().all())

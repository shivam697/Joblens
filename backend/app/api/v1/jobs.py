"""
Job Application API Routes — Full CRUD with filtering and stats

CRITICAL RULE: Every single query filters by current_user.id
Users can NEVER see or modify other users' data.

All job applications use soft delete — is_deleted = True, never hard delete.
"""

import logging
import math

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.schemas.job import (
    JobCreateSchema,
    JobUpdateSchema,
    JobResponse,
)
from app.services.job_service import (
    create_job,
    get_jobs_paginated,
    get_job_by_id,
    update_job,
    soft_delete_job,
    get_job_stats,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/")
async def create_job_application(
    body: JobCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new job application.
    Automatically assigned to the current authenticated user.
    """
    try:
        job_data = body.model_dump(exclude_none=True)
        job = await create_job(db, current_user.id, job_data)

        from app.services.interview_notify import send_today_interview_reminder

        try:
            emailed = await send_today_interview_reminder(job, current_user)
            if emailed:
                logger.info(f"Immediate interview reminder sent for job {job.id}")
        except Exception as mail_error:
            logger.error(f"Interview reminder email failed: {mail_error}")

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Job application added",
                "data": JobResponse.model_validate(job).model_dump(mode="json"),
            },
        )

    except Exception as error:
        logger.error(f"Failed to create job: {error}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to create job application.",
                "data": None,
            },
        )


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get aggregated job application stats for the dashboard.
    Returns total count, count by status, today's interviews, count by platform.
    """
    try:
        stats = await get_job_stats(db, current_user.id)
        return JSONResponse(
            content={
                "success": True,
                "message": "Stats fetched",
                "data": stats,
            }
        )

    except Exception as error:
        logger.error(f"Failed to get stats: {error}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to fetch stats.",
                "data": None,
            },
        )


@router.get("/")
async def list_jobs(
    status: str | None = Query(None, description="Filter by application status"),
    platform: str | None = Query(None, description="Filter by platform"),
    search: str | None = Query(None, description="Search by company name"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List job applications with optional filters and pagination.
    Always filters by current_user.id and excludes soft-deleted records.
    """
    try:
        jobs, total = await get_jobs_paginated(
            db=db,
            user_id=current_user.id,
            page=page,
            limit=limit,
            status_filter=status,
            platform_filter=platform,
            search=search,
        )

        total_pages = math.ceil(total / limit) if total > 0 else 1
        jobs_data = [
            JobResponse.model_validate(j).model_dump(mode="json")
            for j in jobs
        ]

        return JSONResponse(
            content={
                "success": True,
                "message": "Jobs fetched",
                "data": {
                    "items": jobs_data,
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "total_pages": total_pages,
                },
            }
        )

    except Exception as error:
        logger.error(f"Failed to list jobs: {error}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to fetch jobs.",
                "data": None,
            },
        )


@router.get("/{job_id}")
async def get_job_detail(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get full details of a single job application.
    Returns 404 if not found OR if it belongs to another user — same message
    to prevent information leakage about which job IDs exist.
    """
    try:
        job = await get_job_by_id(db, job_id, current_user.id)

        if not job:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "Job application not found.",
                    "data": None,
                },
            )

        return JSONResponse(
            content={
                "success": True,
                "message": "Job fetched",
                "data": JobResponse.model_validate(job).model_dump(mode="json"),
            }
        )

    except Exception as error:
        logger.error(f"Failed to get job: {error}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to fetch job application.",
                "data": None,
            },
        )


@router.put("/{job_id}")
async def update_job_application(
    job_id: str,
    body: JobUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a job application.
    Only updates fields that are explicitly provided (not None).
    """
    try:
        job = await get_job_by_id(db, job_id, current_user.id)

        if not job:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "Job application not found.",
                    "data": None,
                },
            )

        update_data = body.model_dump(exclude_unset=True)
        updated_job = await update_job(db, job, update_data)

        from app.services.interview_notify import send_today_interview_reminder

        try:
            await send_today_interview_reminder(updated_job, current_user)
        except Exception as mail_error:
            logger.error(f"Interview reminder email failed: {mail_error}")

        return JSONResponse(
            content={
                "success": True,
                "message": "Updated successfully",
                "data": JobResponse.model_validate(updated_job).model_dump(mode="json"),
            }
        )

    except Exception as error:
        logger.error(f"Failed to update job: {error}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to update job application.",
                "data": None,
            },
        )


@router.delete("/{job_id}")
async def delete_job_application(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Soft-delete a job application.
    Sets is_deleted = True — NEVER actually removes the record.
    The application will no longer appear in list queries.
    """
    try:
        job = await get_job_by_id(db, job_id, current_user.id)

        if not job:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "Job application not found.",
                    "data": None,
                },
            )

        await soft_delete_job(db, job)

        return JSONResponse(
            content={
                "success": True,
                "message": "Application removed",
                "data": None,
            }
        )

    except Exception as error:
        logger.error(f"Failed to delete job: {error}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to remove application.",
                "data": None,
            },
        )

"""
Interview Reminder Cron Job — Runs daily at 8:00 AM IST

Purpose: Send email reminders to users who have interviews scheduled today.

This function is registered with APScheduler and runs automatically.
It queries MySQL for today's interviews and sends personalized emails.
"""

import logging
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.datetime_utils import get_ist_today_range_utc_naive
from app.db.mysql import async_session_factory
from app.db.models.job_application import JobApplication
from app.db.models.user import User
from app.services.email_service import send_interview_reminder_email
from app.services.interview_notify import format_interview_time_for_email
from app.services.job_service import TODAY_INTERVIEW_STATUSES

logger = logging.getLogger(__name__)


async def send_interview_reminders() -> None:
    """
    Cron job that runs every day at 8:00 AM IST.

    Steps:
    1. Calculate today's date range: 00:00:00 to 23:59:59
    2. Open async MySQL session
    3. Query JobApplications where:
       - interview_datetime is between today_start and today_end
       - status is 'interview_scheduled'
       - is_deleted is False
    4. For each interview found:
       a. Fetch user record to get their email and name
       b. Send personalized reminder email
    5. Log total reminders sent for monitoring
    """
    logger.info("Starting daily interview reminder job...")

    # Today in India (IST) — matches dashboard "Today's Interviews"
    today_start, today_end = get_ist_today_range_utc_naive()

    reminder_count = 0

    try:
        # Open a fresh database session for the cron job
        # Cron jobs run outside of FastAPI request lifecycle,
        # so they need their own session
        async with async_session_factory() as db:
            # Find all interviews scheduled for today
            result = await db.execute(
                select(JobApplication)
                .where(
                    and_(
                        JobApplication.interview_datetime >= today_start,
                        JobApplication.interview_datetime < today_end,
                        JobApplication.status.in_(TODAY_INTERVIEW_STATUSES),
                        JobApplication.is_deleted == False,  # noqa: E712
                    )
                )
            )
            interviews = result.scalars().all()

            for job in interviews:
                try:
                    # Fetch the user for this interview
                    user_result = await db.execute(
                        select(User).where(User.id == job.user_id)
                    )
                    user = user_result.scalar_one_or_none()

                    if not user or not user.email:
                        continue

                    interview_time = format_interview_time_for_email(job.interview_datetime)

                    # Send the reminder email
                    await send_interview_reminder_email(
                        user_name=user.full_name,
                        user_email=user.email,
                        company_name=job.company_name,
                        interview_time=interview_time,
                        interview_mode=job.interview_mode,
                        interview_platform=job.interview_platform,
                        interview_link=job.interview_link,
                        interview_notes=job.interview_notes,
                        job_id=job.id,
                    )
                    reminder_count += 1

                except Exception as email_error:
                    # Don't let one failed email stop the entire cron job
                    logger.error(
                        f"Failed to send reminder for job {job.id}: {email_error}"
                    )
                    continue

    except Exception as error:
        logger.error(f"Interview reminder cron job failed: {error}")

    logger.info(f"Interview reminder job completed. Sent {reminder_count} reminders.")

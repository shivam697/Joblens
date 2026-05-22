"""
Interview notifications — immediate email when an interview is scheduled for today.
Daily batch reminders still run via APScheduler at 8:00 AM IST.
"""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import settings
from app.core.datetime_utils import is_interview_today_ist, IST
from app.db.models.job_application import JobApplication
from app.db.models.user import User
from app.services.email_service import send_interview_reminder_email

logger = logging.getLogger(__name__)


def format_interview_time_for_email(interview_datetime: datetime | None) -> str:
    if not interview_datetime:
        return "Time not set"
    if interview_datetime.tzinfo is None:
        display_dt = interview_datetime.replace(tzinfo=ZoneInfo("UTC")).astimezone(IST)
    else:
        display_dt = interview_datetime.astimezone(IST)
    return display_dt.strftime("%I:%M %p on %B %d, %Y (IST)")


async def send_today_interview_reminder(job: JobApplication, user: User) -> bool:
    """
    Send reminder email for a single interview scheduled today (IST).
    Returns True if email was sent.
    """
    if not is_interview_today_ist(job.interview_datetime):
        return False

    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        logger.warning("Interview email skipped — MAIL_USERNAME/MAIL_PASSWORD not set")
        return False

    if not user.email:
        return False

    interview_time = format_interview_time_for_email(job.interview_datetime)

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
    return True

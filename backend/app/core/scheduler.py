"""
APScheduler Setup — Cron Job Registration and Scheduling

APScheduler runs inside the same Python process as FastAPI.
No separate worker, no message broker, no Redis needed.
Perfect for single-server applications on Windows.

We use AsyncIOScheduler because our cron jobs are async functions
that need to access async database connections.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.tasks.interview_reminder import send_interview_reminders


# Create the scheduler with Indian timezone
# Jobs are triggered based on IST (India Standard Time)
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")


def start_scheduler() -> None:
    """
    Register all cron jobs and start the scheduler.
    Called once during FastAPI startup event.
    APScheduler runs alongside the FastAPI event loop — no separate process needed.
    """
    # Daily interview reminder — sends email at 8:00 AM IST
    # to all users who have interviews scheduled for today
    scheduler.add_job(
        func=send_interview_reminders,
        trigger="cron",
        hour=8,
        minute=0,
        id="daily_interview_reminder",
        replace_existing=True,
        # Run even if app was down and missed 8AM by up to 1 hour
        # Without this, missed jobs are silently skipped
        misfire_grace_time=3600,
    )

    scheduler.start()


def stop_scheduler() -> None:
    """
    Gracefully stop the scheduler during app shutdown.
    wait=False means don't wait for running jobs to complete.
    """
    if scheduler.running:
        scheduler.shutdown(wait=False)

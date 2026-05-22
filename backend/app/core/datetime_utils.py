"""
Timezone helpers — JobLense uses India (IST) for "today" interview logic and cron.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


def get_ist_today_range_utc_naive() -> tuple[datetime, datetime]:
    """
    Return [start, end) for "today" in Asia/Kolkata as UTC-naive datetimes.

    DB stores interview_datetime as UTC (from frontend ISO strings).
    """
    now_ist = datetime.now(IST)
    start_ist = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)
    end_ist = start_ist + timedelta(days=1)

    start_utc = start_ist.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    end_utc = end_ist.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    return start_utc, end_utc


def is_interview_today_ist(interview_datetime: datetime | None) -> bool:
    """True if interview falls on today's calendar date in IST."""
    if not interview_datetime:
        return False
    today_start, today_end = get_ist_today_range_utc_naive()
    return today_start <= interview_datetime < today_end

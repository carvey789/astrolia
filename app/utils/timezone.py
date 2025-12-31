"""Timezone utilities for user-specific date calculations"""
from datetime import datetime, date
import pytz


def get_user_today(timezone_str: str) -> date:
    """Get today's date in user's timezone"""
    try:
        tz = pytz.timezone(timezone_str) if timezone_str else pytz.UTC
        return datetime.now(tz).date()
    except Exception:
        # Fallback to UTC if invalid timezone
        return datetime.now(pytz.UTC).date()


def get_user_datetime(timezone_str: str) -> datetime:
    """Get current datetime in user's timezone"""
    try:
        tz = pytz.timezone(timezone_str) if timezone_str else pytz.UTC
        return datetime.now(tz)
    except Exception:
        return datetime.now(pytz.UTC)


def format_user_date(timezone_str: str) -> str:
    """Get today's date as ISO string in user's timezone"""
    return get_user_today(timezone_str).isoformat()


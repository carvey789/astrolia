"""Zodiac sign utilities."""
from datetime import datetime
from typing import Optional, List, Dict


ZODIAC_SIGNS = [
    {"id": "aries", "name": "Aries", "symbol": "♈", "start_month": 3, "start_day": 21, "end_month": 4, "end_day": 19},
    {"id": "taurus", "name": "Taurus", "symbol": "♉", "start_month": 4, "start_day": 20, "end_month": 5, "end_day": 20},
    {"id": "gemini", "name": "Gemini", "symbol": "♊", "start_month": 5, "start_day": 21, "end_month": 6, "end_day": 20},
    {"id": "cancer", "name": "Cancer", "symbol": "♋", "start_month": 6, "start_day": 21, "end_month": 7, "end_day": 22},
    {"id": "leo", "name": "Leo", "symbol": "♌", "start_month": 7, "start_day": 23, "end_month": 8, "end_day": 22},
    {"id": "virgo", "name": "Virgo", "symbol": "♍", "start_month": 8, "start_day": 23, "end_month": 9, "end_day": 22},
    {"id": "libra", "name": "Libra", "symbol": "♎", "start_month": 9, "start_day": 23, "end_month": 10, "end_day": 22},
    {"id": "scorpio", "name": "Scorpio", "symbol": "♏", "start_month": 10, "start_day": 23, "end_month": 11, "end_day": 21},
    {"id": "sagittarius", "name": "Sagittarius", "symbol": "♐", "start_month": 11, "start_day": 22, "end_month": 12, "end_day": 21},
    {"id": "capricorn", "name": "Capricorn", "symbol": "♑", "start_month": 12, "start_day": 22, "end_month": 1, "end_day": 19},
    {"id": "aquarius", "name": "Aquarius", "symbol": "♒", "start_month": 1, "start_day": 20, "end_month": 2, "end_day": 18},
    {"id": "pisces", "name": "Pisces", "symbol": "♓", "start_month": 2, "start_day": 19, "end_month": 3, "end_day": 20},
]


def get_zodiac_sign_id(birth_date: datetime) -> str:
    """Get zodiac sign ID from birth date."""
    month = birth_date.month
    day = birth_date.day

    for sign in ZODIAC_SIGNS:
        start_m, start_d = sign["start_month"], sign["start_day"]
        end_m, end_d = sign["end_month"], sign["end_day"]

        # Handle Capricorn (crosses year boundary)
        if start_m > end_m:
            if (month == start_m and day >= start_d) or (month == end_m and day <= end_d):
                return sign["id"]
        else:
            if (month == start_m and day >= start_d) or (month == end_m and day <= end_d):
                return sign["id"]

    return "capricorn"  # Default fallback


def get_all_signs() -> List[Dict]:
    """Get all zodiac signs."""
    return ZODIAC_SIGNS


def get_sign_by_id(sign_id: str) -> Optional[Dict]:
    """Get a zodiac sign by ID."""
    for sign in ZODIAC_SIGNS:
        if sign["id"] == sign_id:
            return sign
    return None

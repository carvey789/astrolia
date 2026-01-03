"""
Moon Phases Router - Calculate and return moon phase information
"""
from datetime import datetime, date, timedelta
from typing import List
import math

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/moon", tags=["Moon Phases"])


class MoonPhase(BaseModel):
    date: str
    phase_name: str
    phase_emoji: str
    illumination: float  # 0-100
    days_until_full: int
    days_until_new: int


class MonthlyCalendar(BaseModel):
    year: int
    month: int
    phases: List[MoonPhase]


# Moon phase names and emojis
MOON_PHASES = [
    ("New Moon", "🌑"),
    ("Waxing Crescent", "🌒"),
    ("First Quarter", "🌓"),
    ("Waxing Gibbous", "🌔"),
    ("Full Moon", "🌕"),
    ("Waning Gibbous", "🌖"),
    ("Last Quarter", "🌗"),
    ("Waning Crescent", "🌘"),
]

# Phase meanings for astrological guidance
PHASE_MEANINGS = {
    "New Moon": "A time for new beginnings, setting intentions, and planting seeds for the future. Perfect for starting fresh projects and manifesting desires.",
    "Waxing Crescent": "Energy is building. Take action on your intentions. This is a time for courage, motivation, and moving forward with plans.",
    "First Quarter": "A time of decision and commitment. You may face challenges that test your resolve. Push through obstacles with determination.",
    "Waxing Gibbous": "Refine and adjust your approach. Trust the process and stay focused. Success is building momentum.",
    "Full Moon": "Peak energy and illumination. Emotions run high. A time for celebration, gratitude, and releasing what no longer serves you.",
    "Waning Gibbous": "Time for gratitude and sharing wisdom. Reflect on lessons learned and give back to others.",
    "Last Quarter": "Release and let go. Clear out the old to make room for the new. Forgiveness and closure are favored.",
    "Waning Crescent": "Rest, restore, and surrender. Prepare for the next cycle. Meditation and introspection are powerful now.",
}


def calculate_moon_phase(target_date: date) -> dict:
    """
    Calculate moon phase for a given date using the synodic month approximation.
    The lunar cycle is approximately 29.53 days.
    """
    # Known new moon reference: January 6, 2000
    known_new_moon = date(2000, 1, 6)
    lunar_cycle = 29.53058867

    # Calculate days since known new moon
    days_since = (target_date - known_new_moon).days

    # Current position in lunar cycle (0-29.53)
    cycle_position = days_since % lunar_cycle

    # Determine phase (0-7)
    phase_index = int((cycle_position / lunar_cycle) * 8) % 8

    # Calculate illumination (0-100%)
    # Illumination peaks at full moon (phase 4)
    if cycle_position < lunar_cycle / 2:
        illumination = (cycle_position / (lunar_cycle / 2)) * 100
    else:
        illumination = ((lunar_cycle - cycle_position) / (lunar_cycle / 2)) * 100

    # Days until next full moon (phase 4, midpoint)
    days_to_full = (lunar_cycle / 2 - cycle_position) % lunar_cycle
    if days_to_full > lunar_cycle / 2:
        days_to_full = lunar_cycle - days_to_full

    # Days until next new moon
    days_to_new = (lunar_cycle - cycle_position) % lunar_cycle
    if days_to_new == 0:
        days_to_new = lunar_cycle

    phase_name, phase_emoji = MOON_PHASES[phase_index]

    return {
        "date": target_date.isoformat(),
        "phase_name": phase_name,
        "phase_emoji": phase_emoji,
        "illumination": round(illumination, 1),
        "days_until_full": int(days_to_full),
        "days_until_new": int(days_to_new),
        "meaning": PHASE_MEANINGS[phase_name],
    }


@router.get("/current")
async def get_current_moon_phase():
    """Get today's moon phase"""
    today = date.today()
    phase = calculate_moon_phase(today)
    return phase


@router.get("/date/{year}/{month}/{day}")
async def get_moon_phase_for_date(year: int, month: int, day: int):
    """Get moon phase for a specific date"""
    try:
        target_date = date(year, month, day)
        phase = calculate_moon_phase(target_date)
        return phase
    except ValueError:
        return {"error": "Invalid date"}


@router.get("/calendar/{year}/{month}")
async def get_monthly_calendar(year: int, month: int):
    """Get moon phases for entire month"""
    try:
        # Get first day of month
        first_day = date(year, month, 1)

        # Get last day of month
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)

        # Calculate phases for each day
        phases = []
        current_day = first_day
        while current_day <= last_day:
            phase = calculate_moon_phase(current_day)
            phases.append(phase)
            current_day += timedelta(days=1)

        return {
            "year": year,
            "month": month,
            "month_name": first_day.strftime("%B"),
            "phases": phases,
        }
    except ValueError:
        return {"error": "Invalid month"}


@router.get("/upcoming")
async def get_upcoming_phases():
    """Get upcoming significant moon phases (new and full moons)"""
    today = date.today()
    upcoming = []

    current = today
    found_phases = {"New Moon": False, "Full Moon": False}

    # Look ahead up to 60 days to find next new and full moons
    for _ in range(60):
        phase = calculate_moon_phase(current)
        phase_name = phase["phase_name"]

        if phase_name in found_phases and not found_phases[phase_name]:
            upcoming.append({
                "date": current.isoformat(),
                "phase_name": phase_name,
                "phase_emoji": phase["phase_emoji"],
                "days_until": (current - today).days,
            })
            found_phases[phase_name] = True

        if all(found_phases.values()):
            break

        current += timedelta(days=1)

    return {"upcoming": upcoming}

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..utils import get_current_user
from ..utils.timezone import get_user_datetime

router = APIRouter(prefix="/transits", tags=["Transits"])


# Current transit data for late 2025-2026
# In production, this would be calculated dynamically using ephemeris
TRANSITS_2024_2025 = [
    # Currently Active (Dec 2025)
    {
        "id": "pluto_aquarius",
        "planet": "Pluto",
        "planet_symbol": "♇",
        "type": "ingress",
        "sign_from": "Aquarius",
        "start_date": "2024-11-19",
        "end_date": "2044-01-19",
        "importance": "critical",
        "description": "Pluto in Aquarius (20-year transit!)",
        "guidance": "Generational transformation of society, technology, and collective power. Revolutionary changes in humanity's future.",
        "effects": ["AI revolution", "Power to people", "Social transformation", "Tech evolution"],
        "rituals": ["Embrace innovation", "Community involvement", "Future visioning"]
    },
    {
        "id": "neptune_aries_2025",
        "planet": "Neptune",
        "planet_symbol": "♆",
        "type": "ingress",
        "sign_from": "Pisces",
        "sign_to": "Aries",
        "start_date": "2025-03-30",
        "end_date": "2039-01-26",
        "importance": "high",
        "description": "Neptune in Aries",
        "guidance": "Dreams take action. Spiritual pioneering. Dissolving ego boundaries while asserting individuality. Creative warriors.",
        "effects": ["Spiritual activism", "Artistic innovation", "Compassionate action", "Idealistic movements"],
        "rituals": ["Active meditation", "Creative visualization", "Conscious action"]
    },
    {
        "id": "uranus_gemini_2025",
        "planet": "Uranus",
        "planet_symbol": "♅",
        "type": "ingress",
        "sign_from": "Taurus",
        "sign_to": "Gemini",
        "start_date": "2025-07-07",
        "end_date": "2032-11-08",
        "importance": "high",
        "description": "Uranus in Gemini",
        "guidance": "Revolutionary ideas in communication and learning. AI breakthroughs. New ways of thinking and connecting.",
        "effects": ["AI communication revolution", "Education transformation", "Thought innovation", "Tech in transport"],
        "rituals": ["Learn new tech", "Share radical ideas", "Experiment with communication"]
    },
    {
        "id": "saturn_aries_2025",
        "planet": "Saturn",
        "planet_symbol": "♄",
        "type": "ingress",
        "sign_from": "Pisces",
        "sign_to": "Aries",
        "start_date": "2025-05-24",
        "end_date": "2028-02-13",
        "importance": "high",
        "description": "Saturn in Aries",
        "guidance": "Disciplined new beginnings. Structure in self-assertion. Building identity with responsibility.",
        "effects": ["Leadership responsibility", "Identity structure", "Courageous discipline", "Self-mastery"],
        "rituals": ["Set personal boundaries", "Physical discipline", "Take calculated risks"]
    },
    {
        "id": "jupiter_cancer_2025",
        "planet": "Jupiter",
        "planet_symbol": "♃",
        "type": "ingress",
        "sign_from": "Gemini",
        "sign_to": "Cancer",
        "start_date": "2025-06-09",
        "end_date": "2026-06-30",
        "importance": "medium",
        "description": "Jupiter in Cancer (exalted!)",
        "guidance": "Abundant blessings in home, family, and emotional security. Great for property, nurturing, and inner growth.",
        "effects": ["Family expansion", "Home blessings", "Emotional growth", "Nurturing prosperity"],
        "rituals": ["Bless your home", "Connect with family", "Emotional self-care"]
    },

    # Mercury Retrogrades 2026
    {
        "id": "mercury_retro_jan_2026",
        "planet": "Mercury",
        "planet_symbol": "☿",
        "type": "retrograde",
        "sign_from": "Aquarius",
        "start_date": "2026-01-15",
        "end_date": "2026-02-05",
        "importance": "high",
        "description": "Mercury Retrograde in Aquarius",
        "guidance": "Review technology and innovation projects. Old ideas resurface with new relevance. Back up digital data.",
        "effects": ["Tech glitches", "Revisiting innovation", "Old connections return", "Digital detox needed"],
        "rituals": ["Backup data", "Review tech choices", "Reconnect with groups"]
    },

    # Upcoming Events (Jan 2026)
    {
        "id": "full_moon_jan_2026",
        "planet": "Moon",
        "planet_symbol": "🌕",
        "type": "ingress",
        "sign_from": "Cancer",
        "start_date": "2026-01-03",
        "importance": "medium",
        "description": "Full Moon in Cancer",
        "guidance": "Emotional culmination around home and family. Release what no longer nurtures you.",
        "effects": ["Family clarity", "Home decisions", "Emotional release", "Nurturing completion"],
        "rituals": ["Moon bath", "Release ritual", "Family healing"]
    },
    {
        "id": "new_moon_jan_2026",
        "planet": "Moon",
        "planet_symbol": "🌑",
        "type": "ingress",
        "sign_from": "Capricorn",
        "start_date": "2026-01-18",
        "importance": "medium",
        "description": "New Moon in Capricorn",
        "guidance": "Set intentions for career and long-term goals. Plant seeds for worldly success.",
        "effects": ["Career intentions", "Goal setting", "Ambition renewal", "Structure building"],
        "rituals": ["Goal planning", "Career visualization", "Discipline commitment"]
    },

    # Eclipses 2026
    {
        "id": "lunar_eclipse_mar_2026",
        "planet": "Moon",
        "planet_symbol": "☽",
        "type": "eclipse",
        "sign_from": "Virgo",
        "start_date": "2026-03-03",
        "importance": "critical",
        "description": "Lunar Eclipse in Virgo",
        "guidance": "Release perfectionism in health and work. Emotional revelations about daily routines and service.",
        "effects": ["Health shifts", "Work endings", "Routine release", "Service completion"],
        "rituals": ["Health commitment", "Declutter", "Let go of perfectionism"]
    },
    {
        "id": "solar_eclipse_mar_2026",
        "planet": "Sun",
        "planet_symbol": "☉",
        "type": "eclipse",
        "sign_from": "Pisces",
        "start_date": "2026-03-17",
        "importance": "critical",
        "description": "Solar Eclipse in Pisces",
        "guidance": "New spiritual beginnings. Plant seeds for dreams and imagination. Trust intuition.",
        "effects": ["Spiritual awakening", "Dream manifestation", "Intuitive opening", "Creative rebirth"],
        "rituals": ["Dream work", "Meditation", "Art creation"]
    },
    {
        "id": "lunar_eclipse_aug_2026",
        "planet": "Moon",
        "planet_symbol": "☽",
        "type": "eclipse",
        "sign_from": "Aquarius",
        "start_date": "2026-08-28",
        "importance": "critical",
        "description": "Lunar Eclipse in Aquarius",
        "guidance": "Release old group dynamics and outdated ideals. Emotional clarity about friendship and humanity.",
        "effects": ["Friendship shifts", "Group endings", "Humanitarian awakening", "Tech transformation"],
        "rituals": ["Community ritual", "Release old groups", "Future visioning"]
    },
    {
        "id": "solar_eclipse_sep_2026",
        "planet": "Sun",
        "planet_symbol": "☉",
        "type": "eclipse",
        "sign_from": "Virgo",
        "start_date": "2026-09-12",
        "importance": "critical",
        "description": "Solar Eclipse in Virgo",
        "guidance": "New chapter in health, work, and service. Perfect time for wellness routines and job changes.",
        "effects": ["Health transformation", "New work chapter", "Service opportunities", "Routine renewal"],
        "rituals": ["Start new routine", "Health goal setting", "Service commitment"]
    },
]


# Daily cosmic energy based on moon phase and day
DAILY_ENERGY = {
    0: {"energy": "Initiating", "color": "🔴", "focus": "Start new projects", "avoid": "Procrastination"},
    1: {"energy": "Building", "color": "🟠", "focus": "Steady progress", "avoid": "Rushing"},
    2: {"energy": "Communicating", "color": "🟡", "focus": "Networking & ideas", "avoid": "Gossip"},
    3: {"energy": "Nurturing", "color": "🟢", "focus": "Home & self-care", "avoid": "Emotional eating"},
    4: {"energy": "Creating", "color": "🔵", "focus": "Creative expression", "avoid": "Drama"},
    5: {"energy": "Analyzing", "color": "🟣", "focus": "Details & planning", "avoid": "Over-criticism"},
    6: {"energy": "Resting", "color": "⚪", "focus": "Reflection & rest", "avoid": "Overworking"},
}


class TransitResponse(BaseModel):
    id: str
    planet: str
    planet_symbol: str
    type: str
    sign_from: str
    sign_to: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    importance: str
    description: str
    guidance: str
    effects: List[str]
    rituals: List[str]
    is_active: bool
    days_until: Optional[int] = None
    days_remaining: Optional[int] = None


class DailyTransitsResponse(BaseModel):
    date: str
    daily_energy: dict
    active_transits: List[TransitResponse]
    upcoming_transits: List[TransitResponse]


def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")


def is_transit_active(transit: dict, today: datetime) -> bool:
    start = parse_date(transit["start_date"])
    today_date = today.date() if hasattr(today, 'date') else today
    start_date = start.date() if hasattr(start, 'date') else start

    if transit.get("end_date"):
        end = parse_date(transit["end_date"])
        end_date = end.date() if hasattr(end, 'date') else end
        return start_date <= today_date <= end_date
    # Single-day event (eclipse) - active on the day or within 3 days AFTER
    days_since = (today_date - start_date).days
    return start_date == today_date or (0 <= days_since <= 3)


def get_transit_response(transit: dict, today: datetime) -> TransitResponse:
    start = parse_date(transit["start_date"])
    end = parse_date(transit["end_date"]) if transit.get("end_date") else None
    today_date = today.date() if hasattr(today, 'date') else today
    start_date = start.date() if hasattr(start, 'date') else start
    end_date = (end.date() if hasattr(end, 'date') else end) if end else None

    is_active = is_transit_active(transit, today)
    days_until = (start_date - today_date).days if start_date > today_date else None
    days_remaining = (end_date - today_date).days if end_date and end_date > today_date and is_active else None

    return TransitResponse(
        id=transit["id"],
        planet=transit["planet"],
        planet_symbol=transit["planet_symbol"],
        type=transit["type"],
        sign_from=transit["sign_from"],
        sign_to=transit.get("sign_to"),
        start_date=transit["start_date"],
        end_date=transit.get("end_date"),
        importance=transit["importance"],
        description=transit["description"],
        guidance=transit["guidance"],
        effects=transit["effects"],
        rituals=transit.get("rituals", []),
        is_active=is_active,
        days_until=days_until,
        days_remaining=days_remaining
    )


@router.get("/daily", response_model=DailyTransitsResponse)
async def get_daily_transits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily transits overview with active and upcoming events."""
    # Use user's timezone for date calculation
    today = get_user_datetime(current_user.timezone or 'UTC')

    # Daily energy based on day of week
    day_of_week = today.weekday()
    daily_energy = DAILY_ENERGY.get(day_of_week, DAILY_ENERGY[0])

    # Process all transits
    all_transits = [get_transit_response(t, today) for t in TRANSITS_2024_2025]

    # Split into active and upcoming
    active = [t for t in all_transits if t.is_active]
    upcoming = [t for t in all_transits if not t.is_active and t.days_until and 0 < t.days_until <= 120]

    # Sort upcoming by days until
    upcoming.sort(key=lambda x: x.days_until or 999)

    return DailyTransitsResponse(
        date=today.strftime("%Y-%m-%d"),
        daily_energy=daily_energy,
        active_transits=active,
        upcoming_transits=upcoming[:10]  # Limit to next 10
    )


@router.get("/active", response_model=List[TransitResponse])
async def get_active_transits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get currently active planetary transits."""
    today = datetime.now()
    all_transits = [get_transit_response(t, today) for t in TRANSITS_2024_2025]
    return [t for t in all_transits if t.is_active]


@router.get("/upcoming", response_model=List[TransitResponse])
async def get_upcoming_transits(
    days: int = 60,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get upcoming planetary transits."""
    today = datetime.now()
    all_transits = [get_transit_response(t, today) for t in TRANSITS_2024_2025]
    upcoming = [t for t in all_transits if not t.is_active and t.days_until and 0 < t.days_until <= days]
    upcoming.sort(key=lambda x: x.days_until or 999)
    return upcoming

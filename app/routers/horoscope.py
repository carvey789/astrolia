from datetime import datetime
from typing import Optional
import random
import httpx
from fastapi import APIRouter
from ..utils.zodiac import get_all_signs, get_sign_by_id

router = APIRouter(prefix="/horoscope", tags=["Horoscope"])

# Fallback horoscope messages (if API fails)
FALLBACK_MESSAGES = [
    "The stars align in your favor today. Trust your instincts and take bold action.",
    "A period of reflection begins. Take time to assess your goals and realign your path.",
    "New opportunities emerge on the horizon. Stay open to unexpected possibilities.",
    "Your creative energy peaks today. Channel it into your passion projects.",
    "Communication flows smoothly. It's an ideal day for important conversations.",
    "Focus on self-care and inner peace. Your well-being is the foundation of success.",
    "Financial matters require attention. Review your resources and plan wisely.",
    "Love and relationships take center stage. Express your feelings openly.",
    "Your determination will overcome any obstacles. Stay focused on your goals.",
    "A surprise encounter may change your perspective. Embrace new connections.",
]

MOODS = ["Energetic", "Reflective", "Adventurous", "Creative", "Peaceful", "Ambitious"]

# External API URLs (free horoscope APIs)
AZTRO_API_URL = "https://aztro.sameerkumar.website/"
HOROSCOPE_APP_API = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"


async def fetch_real_horoscope(sign_id: str, day: str = "today") -> Optional[dict]:
    """Fetch real horoscope from external API."""
    try:
        # Try Horoscope App API (more reliable)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                HOROSCOPE_APP_API,
                params={"sign": sign_id, "day": day}
            )
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    return {
                        "content": data["data"].get("horoscope_data", ""),
                        "date": data["data"].get("date", ""),
                    }
    except Exception as e:
        pass  # Fallback to generated horoscope

    try:
        # Fallback to Aztro API
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                AZTRO_API_URL,
                params={"sign": sign_id, "day": day}
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "content": data.get("description", ""),
                    "mood": data.get("mood", ""),
                    "lucky_number": data.get("lucky_number", ""),
                    "lucky_time": data.get("lucky_time", ""),
                    "color": data.get("color", ""),
                    "compatibility": data.get("compatibility", ""),
                    "date_range": data.get("date_range", ""),
                }
    except Exception as e:
        pass  # Aztro API failed too

    return None


def generate_fallback_horoscope(sign_id: str, date: datetime):
    """Generate fallback horoscope if APIs fail."""
    seed = date.toordinal() + hash(sign_id)
    random.seed(seed)

    return {
        "content": random.choice(FALLBACK_MESSAGES),
        "mood": random.choice(MOODS),
        "lucky_time": f"{random.randint(1, 12)}:00 {'AM' if random.random() < 0.5 else 'PM'}",
        "lucky_number": str(random.randint(1, 99)),
    }


@router.get("/signs")
async def get_zodiac_signs():
    """Get all zodiac signs."""
    return get_all_signs()


@router.get("/daily/{sign_id}")
async def get_daily_horoscope(sign_id: str, day: str = "today"):
    """Get daily horoscope for a zodiac sign.

    Args:
        sign_id: The zodiac sign ID (e.g., 'aries', 'leo')
        day: 'yesterday', 'today', or 'tomorrow'
    """
    sign = get_sign_by_id(sign_id)
    if not sign:
        return {"error": "Invalid sign ID"}

    # Try to fetch real horoscope
    real_horoscope = await fetch_real_horoscope(sign_id, day)

    if real_horoscope and real_horoscope.get("content"):
        horoscope = {
            "sign_id": sign_id,
            "date": datetime.utcnow().isoformat(),
            "content": real_horoscope.get("content", ""),
            "mood": real_horoscope.get("mood", random.choice(MOODS)),
            "lucky_time": real_horoscope.get("lucky_time", ""),
            "lucky_number": real_horoscope.get("lucky_number", random.randint(1, 99)),
            "color": real_horoscope.get("color", ""),
            "compatibility": real_horoscope.get("compatibility", ""),
            "source": "real_api",
        }
    else:
        # Fallback to generated horoscope
        horoscope = generate_fallback_horoscope(sign_id, datetime.utcnow())
        horoscope.update({
            "sign_id": sign_id,
            "date": datetime.utcnow().isoformat(),
            "source": "fallback",
        })

    horoscope["sign"] = sign
    horoscope["rating"] = random.randint(3, 5)
    return horoscope


@router.get("/weekly/{sign_id}")
async def get_weekly_horoscope(sign_id: str):
    """Get weekly horoscope for a zodiac sign."""
    sign = get_sign_by_id(sign_id)
    if not sign:
        return {"error": "Invalid sign ID"}

    # Weekly horoscope (combine multiple days)
    seed = datetime.utcnow().isocalendar()[1] + hash(sign_id)
    random.seed(seed)

    return {
        "sign_id": sign_id,
        "sign": sign,
        "week": datetime.utcnow().isocalendar()[1],
        "content": f"This week brings {random.choice(['exciting opportunities', 'time for reflection', 'new connections', 'creative energy'])} for {sign['name']}. {random.choice(FALLBACK_MESSAGES)}",
        "focus_areas": random.sample(["Love", "Career", "Health", "Finance", "Personal Growth"], 3),
        "challenges": random.sample(["Patience", "Communication", "Balance", "Focus", "Trust"], 2),
    }


@router.get("/compatibility/{sign1_id}/{sign2_id}")
async def get_compatibility(sign1_id: str, sign2_id: str):
    """Get compatibility between two zodiac signs."""
    sign1 = get_sign_by_id(sign1_id)
    sign2 = get_sign_by_id(sign2_id)

    if not sign1 or not sign2:
        return {"error": "Invalid sign ID"}

    # Generate compatibility scores based on elements
    element_compatibility = {
        ("Fire", "Fire"): 85, ("Fire", "Air"): 90, ("Fire", "Earth"): 50, ("Fire", "Water"): 60,
        ("Air", "Air"): 80, ("Air", "Earth"): 55, ("Air", "Water"): 65,
        ("Earth", "Earth"): 85, ("Earth", "Water"): 90,
        ("Water", "Water"): 80,
    }

    elem1, elem2 = sign1.get("element", ""), sign2.get("element", "")
    base_score = element_compatibility.get((elem1, elem2)) or element_compatibility.get((elem2, elem1)) or 70

    seed = hash(f"{sign1_id}_{sign2_id}")
    random.seed(seed)

    # Add some variation
    overall = min(98, max(40, base_score + random.randint(-10, 10)))

    return {
        "sign1": sign1,
        "sign2": sign2,
        "overall_score": overall,
        "love_score": min(98, max(40, overall + random.randint(-15, 15))),
        "friendship_score": min(98, max(50, overall + random.randint(-10, 10))),
        "communication_score": min(98, max(45, overall + random.randint(-12, 12))),
        "summary": f"{sign1['name']} ({elem1}) and {sign2['name']} ({elem2}) {'share great natural chemistry' if base_score > 80 else 'can create balance with effort' if base_score > 60 else 'have an interesting dynamic'}.",
        "strengths": ["Mutual respect", "Complementary energies", "Shared interests"],
        "challenges": ["Different communication styles", "Need for patience"],
    }

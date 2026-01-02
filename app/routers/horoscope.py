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


# Monthly horoscope themes
MONTHLY_THEMES = [
    "transformation and growth", "new beginnings and fresh starts",
    "building stable foundations", "embracing creative expression",
    "deepening meaningful connections", "career advancement and success",
    "self-discovery and inner wisdom", "abundance and prosperity",
]

# Yearly horoscope keywords
YEARLY_KEYWORDS = [
    "prosperity", "love", "growth", "adventure", "stability",
    "creativity", "wisdom", "healing", "success", "transformation",
]


@router.get("/monthly/{sign_id}")
async def get_monthly_horoscope(sign_id: str):
    """Get monthly horoscope for a zodiac sign (premium)."""
    sign = get_sign_by_id(sign_id)
    if not sign:
        return {"error": "Invalid sign ID"}

    now = datetime.utcnow()
    month_seed = now.year * 12 + now.month + hash(sign_id)
    random.seed(month_seed)

    theme = random.choice(MONTHLY_THEMES)

    return {
        "sign_id": sign_id,
        "sign": sign,
        "month": now.strftime("%B %Y"),
        "theme": theme.capitalize(),
        "overview": f"This month is all about {theme} for {sign['name']}. The cosmic energies support your natural strengths and encourage you to step into your power. Pay attention to opportunities that align with your deeper values.",
        "love": f"In matters of the heart, expect {random.choice(['passionate encounters', 'deeper connections', 'clarity in relationships', 'new romantic possibilities'])}. {random.choice(['Venus favors your sign', 'Communication is key', 'Trust your intuition', 'Be open to surprises'])}.",
        "career": f"Professionally, focus on {random.choice(['building strategic alliances', 'showcasing your talents', 'taking calculated risks', 'establishing authority'])}. {random.choice(['A new opportunity may arise mid-month', 'Your efforts will be recognized', 'Collaboration leads to success', 'Financial gains are possible'])}.",
        "health": f"Take care of your {random.choice(['physical energy', 'mental well-being', 'emotional balance', 'overall vitality'])}. {random.choice(['Regular exercise benefits you', 'Mindfulness practices help', 'Rest is essential', 'Nature heals'])}.",
        "lucky_days": sorted(random.sample(range(1, 29), 5)),
        "lucky_color": random.choice(["Royal Blue", "Emerald Green", "Golden Yellow", "Rose Pink", "Silver", "Crimson Red"]),
        "lucky_number": random.randint(1, 99),
        "affirmation": random.choice([
            "I am aligned with my highest potential.",
            "Abundance flows to me effortlessly.",
            "I trust the journey of my life.",
            "I embrace change with grace and courage.",
            "My intuition guides me to the right path.",
        ]),
    }


@router.get("/yearly/{sign_id}")
async def get_yearly_horoscope(sign_id: str):
    """Get yearly horoscope for a zodiac sign (premium)."""
    sign = get_sign_by_id(sign_id)
    if not sign:
        return {"error": "Invalid sign ID"}

    now = datetime.utcnow()
    year_seed = now.year + hash(sign_id)
    random.seed(year_seed)

    keywords = random.sample(YEARLY_KEYWORDS, 3)

    return {
        "sign_id": sign_id,
        "sign": sign,
        "year": now.year,
        "keywords": keywords,
        "overview": f"For {sign['name']}, {now.year} is a year of {', '.join(keywords[:2])} and {keywords[2]}. The planetary alignments favor those who embrace authenticity and purposeful action. This is a time to dream big while staying grounded in practical steps.",
        "love_forecast": f"Love and relationships undergo significant {random.choice(['evolution', 'deepening', 'transformation', 'renewal'])} this year. {random.choice(['Single signs may meet someone special in the first half of the year', 'Committed relationships grow stronger through shared experiences', 'Venus retrograde mid-year brings reflection on values', 'Jupiter brings expansion to your love sector'])}.",
        "career_forecast": f"Career moves forward with {random.choice(['determination', 'strategic planning', 'creative innovation', 'confident leadership'])}. {random.choice(['Expect recognition for past efforts', 'New opportunities emerge in Q2', 'Financial stability increases', 'Professional networks expand significantly'])}.",
        "personal_growth": f"This year calls you to {random.choice(['develop new skills', 'heal old wounds', 'expand your horizons', 'deepen spiritual practice'])}. {random.choice(['Travel or education may play a role', 'Meditation and reflection bring insights', 'Health improvements boost overall life quality', 'Creative pursuits bring fulfillment'])}.",
        "key_months": {
            "best": random.sample(["January", "March", "May", "July", "September", "November"], 3),
            "challenging": random.sample(["February", "April", "June", "August", "October", "December"], 2),
        },
        "lucky_numbers": sorted(random.sample(range(1, 50), 5)),
        "power_color": random.choice(["Midnight Blue", "Forest Green", "Sunset Orange", "Royal Purple", "Champagne Gold"]),
        "mantra": random.choice([
            "I create my own destiny with every choice.",
            "This year, I rise to my fullest potential.",
            "I am open to the magic of new possibilities.",
            "My path unfolds perfectly in divine timing.",
        ]),
    }

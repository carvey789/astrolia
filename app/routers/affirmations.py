"""
Affirmations Router - AI-generated daily affirmations by zodiac sign
"""
import os
import httpx
from datetime import date
from typing import List, Dict
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/affirmations", tags=["Affirmations"])

# In-memory cache for daily affirmations: {date_sign_category: Affirmation}
_affirmation_cache: Dict[str, dict] = {}
_cache_date: date = date.today()


class Affirmation(BaseModel):
    id: str
    text: str
    category: str
    emoji: str


# Categories for affirmations with emoji mappings
CATEGORIES = [
    ("Power", "🔥"),
    ("Love", "💕"),
    ("Abundance", "💰"),
    ("Healing", "💜"),
    ("Courage", "⚡"),
    ("Wisdom", "✨"),
    ("Peace", "🕊️"),
    ("Creativity", "🎨"),
    ("Growth", "🌱"),
    ("Self-Love", "💖"),
]

# Zodiac traits for personalized generation
ZODIAC_TRAITS = {
    "aries": "bold, courageous, pioneering, energetic leader",
    "taurus": "stable, patient, sensual, loves comfort and beauty",
    "gemini": "curious, adaptable, communicative, quick-minded",
    "cancer": "nurturing, intuitive, emotional, protective",
    "leo": "confident, creative, generous, natural performer",
    "virgo": "analytical, helpful, practical, detail-oriented",
    "libra": "harmonious, diplomatic, aesthetic, partnership-focused",
    "scorpio": "intense, transformative, passionate, deeply emotional",
    "sagittarius": "adventurous, optimistic, philosophical, freedom-loving",
    "capricorn": "ambitious, disciplined, responsible, goal-oriented",
    "aquarius": "innovative, humanitarian, independent, visionary",
    "pisces": "compassionate, intuitive, artistic, spiritually connected",
}


async def generate_all_affirmations(sign: str) -> list:
    """Generate all 10 affirmations in a single Gemini API call."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return []

    traits = ZODIAC_TRAITS.get(sign.lower(), "unique and special")
    categories_list = ", ".join([f"{cat} ({emoji})" for cat, emoji in CATEGORIES])

    prompt = f"""Generate 10 powerful, personalized daily affirmations for a {sign.title()} person.

Context:
- Zodiac traits: {traits}
- Today's date: {date.today().strftime('%B %d, %Y')}

Generate one affirmation for each of these categories (in order):
{categories_list}

Requirements for each affirmation:
- Start with "I am" or "I"
- Be specific to {sign}'s nature
- Keep each under 15 words
- Be inspiring and empowering

Format your response EXACTLY like this (one per line, no numbering):
Power: I am bold and courageous in all I do.
Love: I attract deep and meaningful connections.
... (continue for all 10 categories)"""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={api_key}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.9,
                        "maxOutputTokens": 500,
                    }
                }
            )

            if response.status_code == 200:
                data = response.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

                if text:
                    # Parse the response
                    affirmations = []
                    lines = text.strip().split('\n')

                    for i, (category, emoji) in enumerate(CATEGORIES):
                        # Find the line for this category
                        affirmation_text = None
                        for line in lines:
                            if line.lower().startswith(category.lower() + ':'):
                                affirmation_text = line.split(':', 1)[1].strip().strip('"').strip("'")
                                break

                        if affirmation_text:
                            affirmations.append(Affirmation(
                                id=f"{sign.lower()}_ai_{i+1}",
                                text=affirmation_text,
                                category=category,
                                emoji=emoji
                            ))

                    if affirmations:
                        return affirmations
            else:
            pass  # Log errors silently in production
    except Exception:
        pass  # Fallback to hardcoded

    return []


# Comprehensive affirmations database - 10+ per sign
AFFIRMATIONS = {
    "aries": [
        Affirmation(id="aries_1", text="I am a powerful creator. My courage opens doors.", category="Power", emoji="🔥"),
        Affirmation(id="aries_2", text="I trust my instincts and take bold action.", category="Courage", emoji="⚡"),
        Affirmation(id="aries_3", text="My passion ignites positive change.", category="Passion", emoji="🌟"),
        Affirmation(id="aries_4", text="I lead with confidence and inspire others.", category="Leadership", emoji="👑"),
        Affirmation(id="aries_5", text="My energy attracts success and abundance.", category="Abundance", emoji="💰"),
        Affirmation(id="aries_6", text="I embrace new challenges with enthusiasm.", category="Growth", emoji="🚀"),
        Affirmation(id="aries_7", text="My determination knows no bounds.", category="Determination", emoji="💪"),
        Affirmation(id="aries_8", text="I am fearless in pursuing my dreams.", category="Dreams", emoji="✨"),
        Affirmation(id="aries_9", text="My authentic self shines through every action.", category="Authenticity", emoji="🌈"),
        Affirmation(id="aries_10", text="I attract opportunities that match my ambition.", category="Opportunity", emoji="🎯"),
    ],
    "taurus": [
        Affirmation(id="taurus_1", text="I am grounded, stable, and secure in my worth.", category="Stability", emoji="🌿"),
        Affirmation(id="taurus_2", text="Abundance flows to me naturally.", category="Abundance", emoji="💎"),
        Affirmation(id="taurus_3", text="I deserve comfort and all good things.", category="Worth", emoji="🌸"),
        Affirmation(id="taurus_4", text="My patience brings me the best rewards.", category="Patience", emoji="🌳"),
        Affirmation(id="taurus_5", text="I attract prosperity through my dedication.", category="Prosperity", emoji="💰"),
        Affirmation(id="taurus_6", text="I am worthy of deep, lasting love.", category="Love", emoji="💕"),
        Affirmation(id="taurus_7", text="My senses guide me to beauty and pleasure.", category="Pleasure", emoji="🌹"),
        Affirmation(id="taurus_8", text="I build a life of luxury and comfort.", category="Luxury", emoji="✨"),
        Affirmation(id="taurus_9", text="My persistence creates lasting success.", category="Success", emoji="🏆"),
        Affirmation(id="taurus_10", text="I am at peace with the rhythm of life.", category="Peace", emoji="🕊️"),
    ],
    "gemini": [
        Affirmation(id="gemini_1", text="My curiosity leads me to discoveries.", category="Curiosity", emoji="✨"),
        Affirmation(id="gemini_2", text="I express my truth with clarity.", category="Communication", emoji="💬"),
        Affirmation(id="gemini_3", text="I embrace all aspects of myself.", category="Self-Love", emoji="💕"),
        Affirmation(id="gemini_4", text="My words have the power to inspire.", category="Inspiration", emoji="🌟"),
        Affirmation(id="gemini_5", text="I adapt gracefully to change.", category="Adaptability", emoji="🦋"),
        Affirmation(id="gemini_6", text="My mind is a fountain of brilliant ideas.", category="Creativity", emoji="💡"),
        Affirmation(id="gemini_7", text="I connect deeply with everyone I meet.", category="Connection", emoji="🤝"),
        Affirmation(id="gemini_8", text="I learn something valuable every day.", category="Learning", emoji="📚"),
        Affirmation(id="gemini_9", text="My versatility is my superpower.", category="Versatility", emoji="🌀"),
        Affirmation(id="gemini_10", text="I communicate my needs with confidence.", category="Confidence", emoji="👑"),
    ],
    "cancer": [
        Affirmation(id="cancer_1", text="My sensitivity is my superpower.", category="Sensitivity", emoji="🌙"),
        Affirmation(id="cancer_2", text="I create safe spaces wherever I go.", category="Security", emoji="🏠"),
        Affirmation(id="cancer_3", text="My intuition guides me perfectly.", category="Intuition", emoji="🔮"),
        Affirmation(id="cancer_4", text="I nurture myself with the same love I give others.", category="Self-Care", emoji="💝"),
        Affirmation(id="cancer_5", text="My emotions are valid and powerful.", category="Emotions", emoji="💧"),
        Affirmation(id="cancer_6", text="I am deeply loved and protected.", category="Love", emoji="💕"),
        Affirmation(id="cancer_7", text="My home is a sanctuary of peace.", category="Home", emoji="🏡"),
        Affirmation(id="cancer_8", text="I honor my need for rest and reflection.", category="Rest", emoji="🌊"),
        Affirmation(id="cancer_9", text="My caring nature attracts loyal friends.", category="Friendship", emoji="🤗"),
        Affirmation(id="cancer_10", text="I trust the cycles of life to support me.", category="Trust", emoji="🌙"),
    ],
    "leo": [
        Affirmation(id="leo_1", text="I shine brightly and inspire others.", category="Confidence", emoji="☀️"),
        Affirmation(id="leo_2", text="My creativity flows abundantly.", category="Creativity", emoji="🎨"),
        Affirmation(id="leo_3", text="I am worthy of love and recognition.", category="Self-Worth", emoji="👑"),
        Affirmation(id="leo_4", text="My heart is generous and full of warmth.", category="Generosity", emoji="💛"),
        Affirmation(id="leo_5", text="I attract admiration through authenticity.", category="Authenticity", emoji="🌟"),
        Affirmation(id="leo_6", text="My presence lights up every room.", category="Presence", emoji="✨"),
        Affirmation(id="leo_7", text="I lead with love and inspire loyalty.", category="Leadership", emoji="🦁"),
        Affirmation(id="leo_8", text="My passion creates beautiful things.", category="Passion", emoji="🔥"),
        Affirmation(id="leo_9", text="I celebrate myself and my achievements.", category="Celebration", emoji="🎉"),
        Affirmation(id="leo_10", text="I am the star of my own life story.", category="Self-Love", emoji="⭐"),
    ],
    "virgo": [
        Affirmation(id="virgo_1", text="I embrace my beautiful imperfections.", category="Acceptance", emoji="🌾"),
        Affirmation(id="virgo_2", text="My attention to detail creates excellence.", category="Excellence", emoji="💫"),
        Affirmation(id="virgo_3", text="I am healthy and complete as I am.", category="Health", emoji="🌱"),
        Affirmation(id="virgo_4", text="My service to others enriches my soul.", category="Service", emoji="🤲"),
        Affirmation(id="virgo_5", text="I release the need for perfection.", category="Release", emoji="🦋"),
        Affirmation(id="virgo_6", text="My practical wisdom guides me well.", category="Wisdom", emoji="🧘"),
        Affirmation(id="virgo_7", text="I am valuable beyond my productivity.", category="Worth", emoji="💎"),
        Affirmation(id="virgo_8", text="My body is a temple I honor daily.", category="Body", emoji="🧘‍♀️"),
        Affirmation(id="virgo_9", text="I trust myself to make the right choices.", category="Trust", emoji="🌿"),
        Affirmation(id="virgo_10", text="My organized mind creates peaceful days.", category="Peace", emoji="📚"),
    ],
    "libra": [
        Affirmation(id="libra_1", text="I attract harmonious relationships.", category="Harmony", emoji="⚖️"),
        Affirmation(id="libra_2", text="Beauty surrounds and flows through me.", category="Beauty", emoji="🌹"),
        Affirmation(id="libra_3", text="I make decisions with ease.", category="Decisiveness", emoji="💝"),
        Affirmation(id="libra_4", text="I am balanced in all areas of life.", category="Balance", emoji="☯️"),
        Affirmation(id="libra_5", text="My partnerships bring out my best.", category="Partnership", emoji="💕"),
        Affirmation(id="libra_6", text="I create peace wherever I go.", category="Peace", emoji="🕊️"),
        Affirmation(id="libra_7", text="My charm opens doors to opportunity.", category="Charm", emoji="✨"),
        Affirmation(id="libra_8", text="I deserve love that feels like home.", category="Love", emoji="🏡"),
        Affirmation(id="libra_9", text="I stand firm in my values and beliefs.", category="Values", emoji="💪"),
        Affirmation(id="libra_10", text="I find beauty in every moment.", category="Appreciation", emoji="🌸"),
    ],
    "scorpio": [
        Affirmation(id="scorpio_1", text="I transform challenges into growth.", category="Transformation", emoji="🦋"),
        Affirmation(id="scorpio_2", text="My intensity creates deep connections.", category="Depth", emoji="🌊"),
        Affirmation(id="scorpio_3", text="I release what no longer serves me.", category="Rebirth", emoji="🔥"),
        Affirmation(id="scorpio_4", text="My power comes from within.", category="Power", emoji="⚡"),
        Affirmation(id="scorpio_5", text="I trust my ability to heal and renew.", category="Healing", emoji="💜"),
        Affirmation(id="scorpio_6", text="My passion drives meaningful change.", category="Passion", emoji="🌋"),
        Affirmation(id="scorpio_7", text="I embrace the mysteries of life.", category="Mystery", emoji="🔮"),
        Affirmation(id="scorpio_8", text="My vulnerability is my strength.", category="Vulnerability", emoji="💧"),
        Affirmation(id="scorpio_9", text="I attract loyal, authentic souls.", category="Loyalty", emoji="🦂"),
        Affirmation(id="scorpio_10", text="I rise from every challenge stronger.", category="Resilience", emoji="🌅"),
    ],
    "sagittarius": [
        Affirmation(id="sag_1", text="Adventure awaits me at every turn.", category="Adventure", emoji="🏹"),
        Affirmation(id="sag_2", text="My optimism attracts miracles.", category="Optimism", emoji="🌈"),
        Affirmation(id="sag_3", text="I embrace limitless possibilities.", category="Expansion", emoji="🌍"),
        Affirmation(id="sag_4", text="My freedom fuels my creativity.", category="Freedom", emoji="🦅"),
        Affirmation(id="sag_5", text="I find wisdom in every experience.", category="Wisdom", emoji="📖"),
        Affirmation(id="sag_6", text="My joy is contagious and inspiring.", category="Joy", emoji="✨"),
        Affirmation(id="sag_7", text="I trust the journey as much as the destination.", category="Trust", emoji="🛤️"),
        Affirmation(id="sag_8", text="I speak my truth with honesty.", category="Honesty", emoji="💬"),
        Affirmation(id="sag_9", text="My luck follows me everywhere.", category="Luck", emoji="🍀"),
        Affirmation(id="sag_10", text="I grow through every adventure.", category="Growth", emoji="🌱"),
    ],
    "capricorn": [
        Affirmation(id="cap_1", text="I am building an extraordinary life.", category="Achievement", emoji="🏔️"),
        Affirmation(id="cap_2", text="My discipline leads to success.", category="Discipline", emoji="🎯"),
        Affirmation(id="cap_3", text="I balance ambition with self-care.", category="Balance", emoji="⭐"),
        Affirmation(id="cap_4", text="My hard work creates lasting legacy.", category="Legacy", emoji="🏆"),
        Affirmation(id="cap_5", text="I am worthy of rest and relaxation.", category="Rest", emoji="🌙"),
        Affirmation(id="cap_6", text="My goals are within reach.", category="Goals", emoji="🎯"),
        Affirmation(id="cap_7", text="I climb every mountain with grace.", category="Perseverance", emoji="⛰️"),
        Affirmation(id="cap_8", text="Success flows to me naturally.", category="Success", emoji="💰"),
        Affirmation(id="cap_9", text="I honor my need for structure and order.", category="Structure", emoji="📐"),
        Affirmation(id="cap_10", text="My wisdom grows with every year.", category="Wisdom", emoji="🦉"),
    ],
    "aquarius": [
        Affirmation(id="aqua_1", text="My unique perspective changes the world.", category="Innovation", emoji="💡"),
        Affirmation(id="aqua_2", text="I embrace my individuality.", category="Authenticity", emoji="🌀"),
        Affirmation(id="aqua_3", text="I connect with like-minded souls.", category="Community", emoji="🤝"),
        Affirmation(id="aqua_4", text="My ideas have the power to revolutionize.", category="Revolution", emoji="⚡"),
        Affirmation(id="aqua_5", text="I honor my need for freedom.", category="Freedom", emoji="🦋"),
        Affirmation(id="aqua_6", text="My humanitarian heart guides my actions.", category="Compassion", emoji="💙"),
        Affirmation(id="aqua_7", text="I am ahead of my time.", category="Vision", emoji="🔭"),
        Affirmation(id="aqua_8", text="My eccentricity is my gift.", category="Uniqueness", emoji="🌟"),
        Affirmation(id="aqua_9", text="I create change through understanding.", category="Understanding", emoji="🧠"),
        Affirmation(id="aqua_10", text="I attract my tribe effortlessly.", category="Tribe", emoji="👥"),
    ],
    "pisces": [
        Affirmation(id="pisces_1", text="My dreams are powerful portals.", category="Dreams", emoji="🌙"),
        Affirmation(id="pisces_2", text="I trust the flow of life.", category="Trust", emoji="🌊"),
        Affirmation(id="pisces_3", text="My compassion heals everyone I meet.", category="Compassion", emoji="💜"),
        Affirmation(id="pisces_4", text="My creativity knows no limits.", category="Creativity", emoji="🎨"),
        Affirmation(id="pisces_5", text="I am connected to universal wisdom.", category="Wisdom", emoji="✨"),
        Affirmation(id="pisces_6", text="My intuition guides me perfectly.", category="Intuition", emoji="🔮"),
        Affirmation(id="pisces_7", text="I embrace my spiritual gifts.", category="Spirituality", emoji="🙏"),
        Affirmation(id="pisces_8", text="My empathy is a superpower.", category="Empathy", emoji="💕"),
        Affirmation(id="pisces_9", text="I protect my energy with love.", category="Protection", emoji="🛡️"),
        Affirmation(id="pisces_10", text="I create magic wherever I go.", category="Magic", emoji="🪄"),
    ],
}


@router.get("/{sign}")
async def get_affirmations(sign: str) -> List[Affirmation]:
    """Get all AI-generated affirmations for a zodiac sign (cached daily)"""
    global _affirmation_cache, _cache_date

    sign_lower = sign.lower()
    if sign_lower not in ZODIAC_TRAITS:
        # Fall back to hardcoded for unknown signs
        if sign_lower in AFFIRMATIONS:
            return AFFIRMATIONS[sign_lower]
        return []

    # Check if cache needs refresh (new day)
    today = date.today()
    if _cache_date != today:
        _affirmation_cache = {}
        _cache_date = today

    # Check if we have cached affirmations for this sign
    cache_key = f"{today.isoformat()}_{sign_lower}"
    if cache_key in _affirmation_cache:
        return _affirmation_cache[cache_key]

    # Generate ALL affirmations in a single API call
    affirmations = await generate_all_affirmations(sign_lower)

    # Fallback to hardcoded if AI fails
    if not affirmations:
        if sign_lower in AFFIRMATIONS:
            affirmations = AFFIRMATIONS[sign_lower]

    # Cache the results
    if affirmations:
        _affirmation_cache[cache_key] = affirmations

    return affirmations


@router.get("/{sign}/daily")
async def get_daily_affirmation(sign: str, timezone: str = "UTC"):
    """Get today's AI-generated affirmation for a zodiac sign (cached daily)"""
    import pytz
    from datetime import datetime

    sign_lower = sign.lower()
    if sign_lower not in ZODIAC_TRAITS:
        return {"error": "Sign not found"}

    # Get current date in user's timezone
    try:
        tz = pytz.timezone(timezone)
        local_now = datetime.now(tz)
        local_date = local_now.date()
    except:
        local_date = date.today()

    # Get all affirmations (uses cache)
    affirmations = await get_affirmations(sign)

    if not affirmations:
        return {"error": "No affirmations available"}

    # Calculate today's index based on day of year
    day_of_year = local_date.timetuple().tm_yday
    index = day_of_year % len(affirmations)

    affirmation = affirmations[index]

    return {
        "affirmation": affirmation,
        "date": local_date.isoformat(),
        "index": index + 1,
        "total": len(affirmations),
        "ai_generated": True,
    }

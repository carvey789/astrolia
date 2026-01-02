"""
Synastry (Relationship Compatibility) Router - AI-powered compatibility deep dive
"""
import os
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from dotenv import load_dotenv
load_dotenv()

from ..database import get_db
from ..models import User
from ..utils import get_current_user

router = APIRouter(prefix="/synastry", tags=["Synastry"])


class SynastryRequest(BaseModel):
    sign1: str
    sign2: str
    birth_date1: Optional[str] = None
    birth_date2: Optional[str] = None


class SynastryResponse(BaseModel):
    overall_score: int  # 0-100
    love_score: int
    friendship_score: int
    communication_score: int
    passion_score: int
    trust_score: int
    strengths: List[str]
    challenges: List[str]
    advice: str
    ai_reading: Optional[str] = None


# Base compatibility scores between zodiac signs
BASE_COMPATIBILITY = {
    "aries": {"aries": 75, "taurus": 55, "gemini": 83, "cancer": 47, "leo": 93, "virgo": 48, "libra": 78, "scorpio": 58, "sagittarius": 93, "capricorn": 47, "aquarius": 85, "pisces": 53},
    "taurus": {"aries": 55, "taurus": 87, "gemini": 42, "cancer": 89, "leo": 62, "virgo": 93, "libra": 55, "scorpio": 85, "sagittarius": 50, "capricorn": 95, "aquarius": 42, "pisces": 85},
    "gemini": {"aries": 83, "taurus": 42, "gemini": 78, "cancer": 45, "leo": 88, "virgo": 62, "libra": 93, "scorpio": 38, "sagittarius": 78, "capricorn": 35, "aquarius": 92, "pisces": 45},
    "cancer": {"aries": 47, "taurus": 89, "gemini": 45, "cancer": 82, "leo": 65, "virgo": 78, "libra": 55, "scorpio": 94, "sagittarius": 42, "capricorn": 72, "aquarius": 35, "pisces": 95},
    "leo": {"aries": 93, "taurus": 62, "gemini": 88, "cancer": 65, "leo": 78, "virgo": 55, "libra": 85, "scorpio": 52, "sagittarius": 93, "capricorn": 45, "aquarius": 68, "pisces": 55},
    "virgo": {"aries": 48, "taurus": 93, "gemini": 62, "cancer": 78, "leo": 55, "virgo": 85, "libra": 62, "scorpio": 88, "sagittarius": 42, "capricorn": 95, "aquarius": 35, "pisces": 65},
    "libra": {"aries": 78, "taurus": 55, "gemini": 93, "cancer": 55, "leo": 85, "virgo": 62, "libra": 82, "scorpio": 55, "sagittarius": 75, "capricorn": 52, "aquarius": 92, "pisces": 62},
    "scorpio": {"aries": 58, "taurus": 85, "gemini": 38, "cancer": 94, "leo": 52, "virgo": 88, "libra": 55, "scorpio": 82, "sagittarius": 42, "capricorn": 78, "aquarius": 38, "pisces": 93},
    "sagittarius": {"aries": 93, "taurus": 50, "gemini": 78, "cancer": 42, "leo": 93, "virgo": 42, "libra": 75, "scorpio": 42, "sagittarius": 85, "capricorn": 48, "aquarius": 85, "pisces": 52},
    "capricorn": {"aries": 47, "taurus": 95, "gemini": 35, "cancer": 72, "leo": 45, "virgo": 95, "libra": 52, "scorpio": 78, "sagittarius": 48, "capricorn": 88, "aquarius": 52, "pisces": 65},
    "aquarius": {"aries": 85, "taurus": 42, "gemini": 92, "cancer": 35, "leo": 68, "virgo": 35, "libra": 92, "scorpio": 38, "sagittarius": 85, "capricorn": 52, "aquarius": 82, "pisces": 55},
    "pisces": {"aries": 53, "taurus": 85, "gemini": 45, "cancer": 95, "leo": 55, "virgo": 65, "libra": 62, "scorpio": 93, "sagittarius": 52, "capricorn": 65, "aquarius": 55, "pisces": 88},
}


@router.post("/analyze", response_model=SynastryResponse)
async def analyze_synastry(
    request: SynastryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed synastry analysis between two zodiac signs with AI insights."""

    sign1 = request.sign1.lower()
    sign2 = request.sign2.lower()

    if sign1 not in BASE_COMPATIBILITY or sign2 not in BASE_COMPATIBILITY:
        raise HTTPException(status_code=400, detail="Invalid zodiac sign")

    # Calculate scores
    overall = BASE_COMPATIBILITY[sign1][sign2]

    # Generate sub-scores with some variation
    import random
    random.seed(hash(sign1 + sign2))

    love = min(100, max(20, overall + random.randint(-15, 15)))
    friendship = min(100, max(20, overall + random.randint(-10, 20)))
    communication = min(100, max(20, overall + random.randint(-20, 15)))
    passion = min(100, max(20, overall + random.randint(-10, 25)))
    trust = min(100, max(20, overall + random.randint(-20, 10)))

    # Get AI reading
    ai_reading = await _get_ai_synastry_reading(sign1, sign2, overall)

    # Generate strengths and challenges based on element compatibility
    strengths, challenges, advice = _get_compatibility_insights(sign1, sign2, overall)

    return SynastryResponse(
        overall_score=overall,
        love_score=love,
        friendship_score=friendship,
        communication_score=communication,
        passion_score=passion,
        trust_score=trust,
        strengths=strengths,
        challenges=challenges,
        advice=advice,
        ai_reading=ai_reading,
    )


async def _get_ai_synastry_reading(sign1: str, sign2: str, score: int) -> Optional[str]:
    """Generate AI-powered synastry reading."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        import httpx

        prompt = f"""As an expert astrologer, provide a personalized synastry reading for a {sign1.title()} and {sign2.title()} relationship.

Their base compatibility score is {score}/100.

Write a warm, insightful 2-3 paragraph reading that covers:
1. The unique dynamic between these two signs
2. How their elements and modalities interact
3. Specific advice for making this relationship thrive

Be specific to these signs, not generic. Use engaging, mystical language. Keep it under 200 words."""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={api_key}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.8,
                        "maxOutputTokens": 400,
                    }
                }
            )

            if response.status_code == 200:
                data = response.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return text.strip() if text else None

    except Exception as e:
        print(f"⚠️ Synastry AI error: {e}")

    return None


def _get_compatibility_insights(sign1: str, sign2: str, score: int):
    """Generate compatibility insights based on elements."""

    elements = {
        "aries": "fire", "leo": "fire", "sagittarius": "fire",
        "taurus": "earth", "virgo": "earth", "capricorn": "earth",
        "gemini": "air", "libra": "air", "aquarius": "air",
        "cancer": "water", "scorpio": "water", "pisces": "water",
    }

    element1 = elements.get(sign1, "fire")
    element2 = elements.get(sign2, "fire")

    # Element-based insights
    if element1 == element2:
        strengths = [
            f"Natural understanding as both are {element1} signs",
            "Similar emotional needs and communication styles",
            "Intuitive connection and shared values",
        ]
        challenges = [
            "May amplify each other's weaknesses",
            "Can lack balance without opposing elements",
        ]
    elif (element1, element2) in [("fire", "air"), ("air", "fire"), ("earth", "water"), ("water", "earth")]:
        strengths = [
            f"{element1.title()} and {element2.title()} naturally complement each other",
            "Balance of energy and stability",
            "Mutual inspiration and growth",
        ]
        challenges = [
            "Different paces may cause friction",
            "Need to actively understand each other's nature",
        ]
    else:
        strengths = [
            "Opportunity to learn and grow from differences",
            "Each brings unique strengths to the relationship",
        ]
        challenges = [
            "Fundamentally different approaches to life",
            "Communication may require extra effort",
            "Different emotional needs",
        ]

    if score >= 80:
        advice = f"This is a highly compatible match! Your {sign1.title()}-{sign2.title()} connection has natural flow and mutual understanding. Nurture your bond through shared adventures and deep conversations."
    elif score >= 60:
        advice = f"Your {sign1.title()}-{sign2.title()} pairing has good potential. Focus on celebrating your differences and finding common ground. With effort, this can be a deeply rewarding relationship."
    else:
        advice = f"While {sign1.title()} and {sign2.title()} face some challenges, growth often comes from differences. Patience, open communication, and mutual respect are key to making this connection work."

    return strengths, challenges, advice

"""
AI Astrologer Chat Router - Uses Gemini AI for personalized astrology chat
"""
import os
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Load .env file for GEMINI_API_KEY
from dotenv import load_dotenv
load_dotenv()

from ..database import get_db
from ..models import User
from ..utils import get_current_user

router = APIRouter(prefix="/chat", tags=["AI Astrologer"])

# System prompt for astrology personality
ASTROLOGER_SYSTEM_PROMPT = """You are Astra, a wise and mystical AI astrologer in the Astrolia app. You combine ancient astrological wisdom with modern psychological insights.

Your personality:
- Warm, encouraging, and insightful
- You speak with gentle mystical flair but stay grounded and practical
- You reference celestial bodies, transits, and cosmic energy naturally
- You're empathetic and supportive, never judgmental

Your knowledge includes:
- Natal chart interpretation (Sun, Moon, Rising, planets in signs/houses)
- Planetary transits and their effects
- Compatibility and synastry
- Tarot card meanings
- Numerology basics
- Moon phases and their significance

Guidelines:
- Keep responses concise (2-4 paragraphs max)
- Always tie advice back to the user's natal chart when relevant
- Use emojis sparingly for warmth (✨, 🌙, ⭐)
- If you don't know something specific about astrology, say so gracefully
- Never give medical, legal, or financial advice
- Encourage self-reflection and personal growth

The user's birth details and natal chart information will be provided for context.
"""


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    response: str
    success: bool


def get_natal_chart_context(user: User) -> str:
    """Build context string from user's birth data."""
    if not user.birth_date:
        return "User has not provided birth details yet."

    # Handle birth_date as string or datetime
    birth_date = user.birth_date
    if isinstance(birth_date, str):
        try:
            birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
        except ValueError:
            try:
                birth_date = datetime.fromisoformat(birth_date)
            except ValueError:
                return f"User was born on {user.birth_date}"

    month, day = birth_date.month, birth_date.day

    # Simple Sun sign calculation
    zodiac_dates = [
        ((3, 21), (4, 19), "Aries"),
        ((4, 20), (5, 20), "Taurus"),
        ((5, 21), (6, 20), "Gemini"),
        ((6, 21), (7, 22), "Cancer"),
        ((7, 23), (8, 22), "Leo"),
        ((8, 23), (9, 22), "Virgo"),
        ((9, 23), (10, 22), "Libra"),
        ((10, 23), (11, 21), "Scorpio"),
        ((11, 22), (12, 21), "Sagittarius"),
        ((12, 22), (1, 19), "Capricorn"),
        ((1, 20), (2, 18), "Aquarius"),
        ((2, 19), (3, 20), "Pisces"),
    ]

    sun_sign = "Unknown"
    for (start_m, start_d), (end_m, end_d), sign in zodiac_dates:
        if start_m <= end_m:
            if (month == start_m and day >= start_d) or (month == end_m and day <= end_d):
                sun_sign = sign
                break
            if start_m < month < end_m:
                sun_sign = sign
                break
        else:  # Capricorn case (Dec-Jan)
            if (month == start_m and day >= start_d) or (month == end_m and day <= end_d):
                sun_sign = sign
                break

    context = f"""
USER'S BIRTH INFORMATION:
- Name: {user.name or 'Unknown'}
- Birth Date: {birth_date.strftime('%B %d, %Y')}
- Sun Sign: {sun_sign}
"""

    if user.birth_time:
        # Handle birth_time as string or time
        if isinstance(user.birth_time, str):
            context += f"- Birth Time: {user.birth_time}\n"
        else:
            context += f"- Birth Time: {user.birth_time.strftime('%I:%M %p')}\n"

    if user.birth_location:
        context += f"- Birth Location: {user.birth_location}\n"

    return context


@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to the AI astrologer and get a response."""

    # Check if user is premium (for now, allow all for testing)
    # if not current_user.is_premium:
    #     raise HTTPException(status_code=403, detail="Premium subscription required")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return ChatResponse(
            response="✨ AI service not configured. Please add GEMINI_API_KEY to .env",
            success=False
        )

    try:
        import httpx

        # Get user's natal chart context
        natal_context = get_natal_chart_context(current_user)

        # Build conversation history
        full_prompt = f"{ASTROLOGER_SYSTEM_PROMPT}\n\n{natal_context}\n\n"

        if request.history:
            for msg in request.history[-10:]:  # Last 10 messages for context
                role = "User" if msg.role == "user" else "Astra"
                full_prompt += f"{role}: {msg.content}\n\n"

        full_prompt += f"User: {request.message}\n\nAstra:"

        # Call Gemini REST API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={api_key}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json={
                    "contents": [{"parts": [{"text": full_prompt}]}],
                    "generationConfig": {
                        "temperature": 0.8,
                        "maxOutputTokens": 500,
                    }
                }
            )

            if response.status_code == 200:
                data = response.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if text:
                    return ChatResponse(response=text.strip(), success=True)
                else:
                    print(f"⚠️ Gemini returned empty text. Response: {data}")
            else:
                print(f"⚠️ Gemini API error {response.status_code}: {response.text}")

            return ChatResponse(
                response="✨ The cosmic connection is hazy. Please try again!",
                success=False
            )

    except Exception as e:
        print(f"⚠️ Astra chat exception: {e}")
        return ChatResponse(
            response=f"✨ The stars are a bit cloudy right now. ({str(e)[:50]})",
            success=False
        )


@router.get("/suggestions")
async def get_chat_suggestions(current_user: User = Depends(get_current_user)):
    """Get suggested conversation starters based on user's chart."""

    suggestions = [
        "What does my Sun sign say about my personality?",
        "How will Mercury retrograde affect me?",
        "What career paths suit my zodiac sign?",
        "Tell me about love compatibility for my sign",
        "What should I focus on this month?",
        "Explain my strengths and challenges",
        "What crystals are good for my sign?",
        "How can I use moon phases in my life?",
    ]

    return {"suggestions": suggestions}

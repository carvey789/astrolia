from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..utils import get_current_user
from ..utils.timezone import get_user_datetime

router = APIRouter(prefix="/numerology", tags=["Numerology"])


# Personal Day interpretations
PERSONAL_DAY_MEANINGS = {
    1: {
        "title": "Day of New Beginnings",
        "emoji": "🌅",
        "energy": "Initiating",
        "guidance": "Today's energy favors starting new projects and taking initiative. Trust your instincts and lead with confidence. Your personal power is strong - use it to make bold moves.",
        "affirmation": "I am a powerful creator of my reality.",
        "focus": ["Start new projects", "Take initiative", "Be independent", "Assert yourself"],
        "avoid": ["Following the crowd", "Procrastination", "Self-doubt"]
    },
    2: {
        "title": "Day of Cooperation",
        "emoji": "🤝",
        "energy": "Harmonizing",
        "guidance": "Today calls for patience and diplomacy. Partnership energies are strong. Listen more than you speak, and seek balance in all interactions.",
        "affirmation": "I create harmony in my relationships.",
        "focus": ["Collaborative work", "Listening", "Patience", "Relationships"],
        "avoid": ["Being pushy", "Impatience", "Forcing issues"]
    },
    3: {
        "title": "Day of Expression",
        "emoji": "🎨",
        "energy": "Creative",
        "guidance": "Your creativity and communication are supercharged today. Express yourself through art, writing, or conversation. Joy and social connections are favored.",
        "affirmation": "My creative expression flows freely.",
        "focus": ["Creative projects", "Social activities", "Self-expression", "Joy"],
        "avoid": ["Negative self-talk", "Isolation", "Criticism"]
    },
    4: {
        "title": "Day of Building",
        "emoji": "🏗️",
        "energy": "Grounding",
        "guidance": "Focus on practical matters, organization, and building solid foundations. Hard work pays off today. Create structure and attend to details.",
        "affirmation": "I build lasting foundations for my dreams.",
        "focus": ["Organization", "Practical tasks", "Planning", "Hard work"],
        "avoid": ["Cutting corners", "Disorganization", "Rigidity"]
    },
    5: {
        "title": "Day of Change",
        "emoji": "🦋",
        "energy": "Dynamic",
        "guidance": "Embrace change and variety today. Adventure calls! Be flexible and open to unexpected opportunities. Break free from routine.",
        "affirmation": "I embrace change with excitement and grace.",
        "focus": ["New experiences", "Flexibility", "Adventure", "Freedom"],
        "avoid": ["Resistance to change", "Excess", "Scattered energy"]
    },
    6: {
        "title": "Day of Nurturing",
        "emoji": "💝",
        "energy": "Loving",
        "guidance": "Home and family take priority today. Nurture yourself and loved ones. Beauty and harmony are especially important. Give and receive love freely.",
        "affirmation": "I nurture myself and others with love.",
        "focus": ["Family", "Home improvements", "Self-care", "Helping others"],
        "avoid": ["Neglecting yourself", "Perfectionism", "Martyrdom"]
    },
    7: {
        "title": "Day of Reflection",
        "emoji": "🔮",
        "energy": "Introspective",
        "guidance": "Take time for meditation and inner reflection. Seek knowledge and spiritual connection. Trust your intuition - answers come from within today.",
        "affirmation": "I trust my inner wisdom.",
        "focus": ["Meditation", "Study", "Solitude", "Spiritual practices"],
        "avoid": ["Overthinking", "Isolation extremes", "Skepticism"]
    },
    8: {
        "title": "Day of Manifestation",
        "emoji": "💎",
        "energy": "Abundant",
        "guidance": "Financial and material matters are favored. Take action on business goals. Your power to manifest is strong - think big and act decisively.",
        "affirmation": "Abundance flows to me naturally.",
        "focus": ["Business matters", "Financial decisions", "Goal achievement", "Leadership"],
        "avoid": ["Greed", "Ignoring ethics", "Workaholism"]
    },
    9: {
        "title": "Day of Completion",
        "emoji": "🌍",
        "energy": "Humanitarian",
        "guidance": "Focus on completing projects and releasing what no longer serves you. Compassion and service to others bring fulfillment. Let go with love.",
        "affirmation": "I release the old to welcome the new.",
        "focus": ["Completion", "Letting go", "Helping others", "Forgiveness"],
        "avoid": ["Starting new projects", "Holding grudges", "Selfishness"]
    },
}

# Life Path interpretations (extended)
LIFE_PATH_MEANINGS = {
    1: {
        "title": "The Leader",
        "emoji": "👑",
        "traits": ["Independent", "Ambitious", "Pioneering", "Confident"],
        "description": "You are a natural born leader with strong willpower. Independent and ambitious, you forge your own path and inspire others to follow.",
        "strengths": ["Leadership", "Innovation", "Determination", "Originality"],
        "challenges": ["Stubbornness", "Self-centeredness", "Impatience"],
        "life_purpose": "To develop individuality and lead others toward new beginnings."
    },
    2: {
        "title": "The Peacemaker",
        "emoji": "🕊️",
        "traits": ["Diplomatic", "Sensitive", "Cooperative", "Intuitive"],
        "description": "You are a natural mediator with deep intuition. Partnership and harmony are your gifts, bringing people together.",
        "strengths": ["Diplomacy", "Intuition", "Patience", "Sensitivity"],
        "challenges": ["Oversensitivity", "Indecisiveness", "Dependency"],
        "life_purpose": "To bring harmony and cooperation to relationships and groups."
    },
    3: {
        "title": "The Communicator",
        "emoji": "🎨",
        "traits": ["Creative", "Expressive", "Optimistic", "Social"],
        "description": "You are gifted with creativity and self-expression. Joy and inspiration flow through you naturally.",
        "strengths": ["Creativity", "Communication", "Optimism", "Artistic talent"],
        "challenges": ["Scattered energy", "Superficiality", "Mood swings"],
        "life_purpose": "To inspire others through creative self-expression and joy."
    },
    4: {
        "title": "The Builder",
        "emoji": "🏗️",
        "traits": ["Practical", "Hardworking", "Stable", "Reliable"],
        "description": "You are the foundation builder of society. Order, stability, and hard work define your approach.",
        "strengths": ["Organization", "Discipline", "Loyalty", "Practicality"],
        "challenges": ["Rigidity", "Stubbornness", "Workaholic tendencies"],
        "life_purpose": "To create lasting structures and systems that benefit others."
    },
    5: {
        "title": "The Freedom Seeker",
        "emoji": "🌊",
        "traits": ["Adventurous", "Versatile", "Dynamic", "Free-spirited"],
        "description": "You crave freedom and adventure. Change is your constant companion, bringing dynamic energy.",
        "strengths": ["Adaptability", "Curiosity", "Resourcefulness", "Versatility"],
        "challenges": ["Restlessness", "Inconsistency", "Excess"],
        "life_purpose": "To experience life fully and help others embrace positive change."
    },
    6: {
        "title": "The Nurturer",
        "emoji": "💝",
        "traits": ["Caring", "Responsible", "Protective", "Harmonious"],
        "description": "You are the cosmic parent. Love, family, and responsibility are central to your being.",
        "strengths": ["Compassion", "Responsibility", "Healing", "Domestic harmony"],
        "challenges": ["Self-sacrifice", "Perfectionism", "Over-protectiveness"],
        "life_purpose": "To nurture and heal others while creating harmony in home and community."
    },
    7: {
        "title": "The Seeker",
        "emoji": "🔮",
        "traits": ["Analytical", "Spiritual", "Introspective", "Wise"],
        "description": "You are the truth seeker. Spirituality, knowledge, and inner wisdom guide your path.",
        "strengths": ["Wisdom", "Intuition", "Analysis", "Spiritual depth"],
        "challenges": ["Isolation", "Skepticism", "Aloofness"],
        "life_purpose": "To seek spiritual truth and share wisdom with others."
    },
    8: {
        "title": "The Powerhouse",
        "emoji": "💎",
        "traits": ["Ambitious", "Authoritative", "Successful", "Material"],
        "description": "You are meant for abundance. Power, success, and material achievement are your destiny.",
        "strengths": ["Business acumen", "Authority", "Achievement", "Manifestation"],
        "challenges": ["Materialism", "Workaholism", "Power struggles"],
        "life_purpose": "To achieve material success and use power responsibly for the greater good."
    },
    9: {
        "title": "The Humanitarian",
        "emoji": "🌍",
        "traits": ["Compassionate", "Generous", "Idealistic", "Creative"],
        "description": "You are here to serve humanity. Universal love and compassion define your soul mission.",
        "strengths": ["Compassion", "Wisdom", "Creativity", "Generosity"],
        "challenges": ["Detachment", "Martyrdom", "Being too idealistic"],
        "life_purpose": "To serve humanity and bring healing on a global scale."
    },
    11: {
        "title": "The Intuitive",
        "emoji": "✨",
        "traits": ["Visionary", "Spiritual", "Inspiring", "Sensitive"],
        "description": "Master Number. You are a spiritual messenger with heightened intuition and psychic gifts.",
        "strengths": ["Inspiration", "Spiritual insight", "Leadership", "Healing"],
        "challenges": ["Anxiety", "Self-doubt", "Nervous energy"],
        "life_purpose": "To inspire and illuminate others through spiritual vision."
    },
    22: {
        "title": "The Master Builder",
        "emoji": "🏛️",
        "traits": ["Visionary", "Practical", "Ambitious", "Powerful"],
        "description": "Master Number. You can turn the grandest spiritual visions into practical reality.",
        "strengths": ["Vision", "Practicality", "Leadership", "Global impact"],
        "challenges": ["Overwhelm", "Self-pressure", "Unrealistic expectations"],
        "life_purpose": "To build structures and systems that benefit humanity on a large scale."
    },
    33: {
        "title": "The Master Teacher",
        "emoji": "🌟",
        "traits": ["Nurturing", "Spiritual", "Healing", "Selfless"],
        "description": "Master Number. You are a beacon of light and unconditional love for humanity.",
        "strengths": ["Healing", "Teaching", "Compassion", "Unconditional love"],
        "challenges": ["Burnout", "Over-giving", "Martyrdom"],
        "life_purpose": "To teach, heal, and uplift humanity through unconditional love."
    },
}


class NumerologyResponse(BaseModel):
    life_path_number: int
    life_path_meaning: dict
    personal_year: int
    personal_month: int
    personal_day: int
    personal_day_meaning: dict
    destiny_number: int
    soul_number: int
    personality_number: int


def reduce_to_single(n: int) -> int:
    """Reduce number to single digit (preserve master numbers)."""
    while n > 9 and n not in [11, 22, 33]:
        n = sum(int(d) for d in str(n))
    return n


def calculate_life_path(birth_date: datetime) -> int:
    """Calculate life path number from birth date."""
    total = birth_date.year + birth_date.month + birth_date.day
    return reduce_to_single(total)


def calculate_personal_year(birth_date: datetime, current_date: datetime) -> int:
    """Calculate personal year number."""
    total = current_date.year + birth_date.month + birth_date.day
    return reduce_to_single(total)


def calculate_personal_month(personal_year: int, current_month: int) -> int:
    """Calculate personal month number."""
    return reduce_to_single(personal_year + current_month)


def calculate_personal_day(personal_month: int, current_day: int) -> int:
    """Calculate personal day number."""
    return reduce_to_single(personal_month + current_day)


@router.get("/daily", response_model=NumerologyResponse)
async def get_daily_numerology(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily numerology reading based on user's birth date."""
    # Use user's timezone for date calculation
    today = get_user_datetime(current_user.timezone or 'UTC')
    birth_date = current_user.birth_date

    # Calculate all numbers
    life_path = calculate_life_path(birth_date)
    personal_year = calculate_personal_year(birth_date, today)
    personal_month = calculate_personal_month(personal_year, today.month)
    personal_day = calculate_personal_day(personal_month, today.day)

    # Other numbers
    destiny = reduce_to_single(birth_date.day)
    soul = reduce_to_single(birth_date.month)
    personality = reduce_to_single(birth_date.year)

    # Get meanings
    life_path_meaning = LIFE_PATH_MEANINGS.get(life_path, LIFE_PATH_MEANINGS[1])
    personal_day_meaning = PERSONAL_DAY_MEANINGS.get(personal_day, PERSONAL_DAY_MEANINGS[1])

    return NumerologyResponse(
        life_path_number=life_path,
        life_path_meaning=life_path_meaning,
        personal_year=personal_year,
        personal_month=personal_month,
        personal_day=personal_day,
        personal_day_meaning=personal_day_meaning,
        destiny_number=destiny,
        soul_number=soul,
        personality_number=personality
    )

from datetime import datetime
import random
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Load .env for GEMINI_API_KEY
from dotenv import load_dotenv
load_dotenv()

from ..database import get_db
from ..models import User, TarotHistory
from ..schemas import TarotHistoryResponse
from ..utils import get_current_user
from ..utils.timezone import get_user_today

router = APIRouter(prefix="/tarot", tags=["Tarot"])

# Major Arcana cards with full interpretations
# Image URLs from public tarot card CDN (Rider-Waite deck)
TAROT_IMAGE_BASE = "https://www.sacred-texts.com/tarot/pkt/img"

MAJOR_ARCANA = [
    {"id": "fool", "name": "The Fool", "number": 0, "image": "🃏", "image_url": f"{TAROT_IMAGE_BASE}/ar00.jpg"},
    {"id": "magician", "name": "The Magician", "number": 1, "image": "🧙", "image_url": f"{TAROT_IMAGE_BASE}/ar01.jpg"},
    {"id": "priestess", "name": "The High Priestess", "number": 2, "image": "🌙", "image_url": f"{TAROT_IMAGE_BASE}/ar02.jpg"},
    {"id": "empress", "name": "The Empress", "number": 3, "image": "👑", "image_url": f"{TAROT_IMAGE_BASE}/ar03.jpg"},
    {"id": "emperor", "name": "The Emperor", "number": 4, "image": "🏛️", "image_url": f"{TAROT_IMAGE_BASE}/ar04.jpg"},
    {"id": "hierophant", "name": "The Hierophant", "number": 5, "image": "📿", "image_url": f"{TAROT_IMAGE_BASE}/ar05.jpg"},
    {"id": "lovers", "name": "The Lovers", "number": 6, "image": "💕", "image_url": f"{TAROT_IMAGE_BASE}/ar06.jpg"},
    {"id": "chariot", "name": "The Chariot", "number": 7, "image": "⚔️", "image_url": f"{TAROT_IMAGE_BASE}/ar07.jpg"},
    {"id": "strength", "name": "Strength", "number": 8, "image": "🦁", "image_url": f"{TAROT_IMAGE_BASE}/ar08.jpg"},
    {"id": "hermit", "name": "The Hermit", "number": 9, "image": "🏔️", "image_url": f"{TAROT_IMAGE_BASE}/ar09.jpg"},
    {"id": "wheel", "name": "Wheel of Fortune", "number": 10, "image": "🎡", "image_url": f"{TAROT_IMAGE_BASE}/ar10.jpg"},
    {"id": "justice", "name": "Justice", "number": 11, "image": "⚖️", "image_url": f"{TAROT_IMAGE_BASE}/ar11.jpg"},
    {"id": "hanged", "name": "The Hanged Man", "number": 12, "image": "🙃", "image_url": f"{TAROT_IMAGE_BASE}/ar12.jpg"},
    {"id": "death", "name": "Death", "number": 13, "image": "🦋", "image_url": f"{TAROT_IMAGE_BASE}/ar13.jpg"},
    {"id": "temperance", "name": "Temperance", "number": 14, "image": "⚗️", "image_url": f"{TAROT_IMAGE_BASE}/ar14.jpg"},
    {"id": "devil", "name": "The Devil", "number": 15, "image": "⛓️", "image_url": f"{TAROT_IMAGE_BASE}/ar15.jpg"},
    {"id": "tower", "name": "The Tower", "number": 16, "image": "🗼", "image_url": f"{TAROT_IMAGE_BASE}/ar16.jpg"},
    {"id": "star", "name": "The Star", "number": 17, "image": "⭐", "image_url": f"{TAROT_IMAGE_BASE}/ar17.jpg"},
    {"id": "moon", "name": "The Moon", "number": 18, "image": "🌕", "image_url": f"{TAROT_IMAGE_BASE}/ar18.jpg"},
    {"id": "sun", "name": "The Sun", "number": 19, "image": "☀️", "image_url": f"{TAROT_IMAGE_BASE}/ar19.jpg"},
    {"id": "judgement", "name": "Judgement", "number": 20, "image": "📯", "image_url": f"{TAROT_IMAGE_BASE}/ar20.jpg"},
    {"id": "world", "name": "The World", "number": 21, "image": "🌍", "image_url": f"{TAROT_IMAGE_BASE}/ar21.jpg"},
]

# Detailed interpretations for each card
CARD_INTERPRETATIONS = {
    "fool": {
        "upright": {
            "meaning": "New beginnings, innocence, spontaneity, and a free spirit. Today invites you to take a leap of faith and embrace the unknown with childlike wonder.",
            "daily_guidance": "Trust your instincts and don't be afraid to start something new. The universe supports fresh starts today.",
            "keywords": ["new beginnings", "innocence", "adventure", "potential", "spontaneity"]
        },
        "reversed": {
            "meaning": "Recklessness, risk-taking, or holding back from new experiences. You may be acting without thinking or letting fear prevent you from taking necessary steps.",
            "daily_guidance": "Consider whether you're being too impulsive or too cautious. Find balance between spontaneity and wisdom.",
            "keywords": ["recklessness", "fear", "hesitation", "naivety", "carelessness"]
        }
    },
    "magician": {
        "upright": {
            "meaning": "Manifestation, resourcefulness, and inspired action. You have all the tools you need to succeed. Channel your willpower to create your reality.",
            "daily_guidance": "Focus your intention and take action. You have the power to manifest your desires today.",
            "keywords": ["manifestation", "willpower", "creation", "skill", "concentration"]
        },
        "reversed": {
            "meaning": "Manipulation, untapped potential, or deception. You may not be using your talents fully, or someone may not be being honest.",
            "daily_guidance": "Examine your motives and ensure you're using your abilities ethically. Watch for deception.",
            "keywords": ["manipulation", "tricks", "unused potential", "cunning", "deceit"]
        }
    },
    "priestess": {
        "upright": {
            "meaning": "Intuition, mystery, and inner knowledge. Trust your subconscious wisdom and pay attention to dreams and synchronicities.",
            "daily_guidance": "Listen to your inner voice today. Answers come through quiet reflection, not action.",
            "keywords": ["intuition", "mystery", "subconscious", "wisdom", "spirituality"]
        },
        "reversed": {
            "meaning": "Secrets, disconnection from intuition, or hidden agendas. You may be ignoring your inner voice or something is being concealed.",
            "daily_guidance": "Reconnect with your intuition. If something feels off, investigate before proceeding.",
            "keywords": ["secrets", "silence", "withdrawal", "hidden truths", "blocked intuition"]
        }
    },
    "empress": {
        "upright": {
            "meaning": "Abundance, nurturing, and creativity. Embrace beauty, comfort, and the creative flow. Nature and self-care are especially important.",
            "daily_guidance": "Nurture yourself and others. Creative projects flourish. Connect with nature.",
            "keywords": ["abundance", "fertility", "nurturing", "creativity", "beauty"]
        },
        "reversed": {
            "meaning": "Dependence, smothering, or creative block. You may be neglecting self-care or being overprotective.",
            "daily_guidance": "Check if you're giving too much or too little care to yourself or others. Find balance.",
            "keywords": ["dependence", "emptiness", "creative block", "overprotection", "neglect"]
        }
    },
    "emperor": {
        "upright": {
            "meaning": "Authority, structure, and leadership. Take control of your situation with discipline and strategic thinking.",
            "daily_guidance": "Lead with confidence. Structure and organization help you achieve your goals today.",
            "keywords": ["authority", "leadership", "structure", "control", "discipline"]
        },
        "reversed": {
            "meaning": "Tyranny, rigidity, or lack of discipline. You may be too controlling or struggling with authority.",
            "daily_guidance": "Examine your relationship with power. Are you too rigid or too scattered?",
            "keywords": ["domination", "rigidity", "stubbornness", "powerlessness", "control issues"]
        }
    },
    "hierophant": {
        "upright": {
            "meaning": "Tradition, spiritual wisdom, and established institutions. Seek guidance from mentors or traditional practices.",
            "daily_guidance": "Honor traditions and seek wisdom from established sources. Teaching and learning are favored.",
            "keywords": ["tradition", "conformity", "religion", "beliefs", "guidance"]
        },
        "reversed": {
            "meaning": "Rebellion, nonconformity, or challenging traditions. You may need to find your own spiritual path.",
            "daily_guidance": "Question rules that don't serve you. Your personal beliefs matter more than conformity.",
            "keywords": ["rebellion", "nonconformity", "personal beliefs", "freedom", "questioning"]
        }
    },
    "lovers": {
        "upright": {
            "meaning": "Love, harmony, and meaningful connections. Important choices in relationships align your values with your heart.",
            "daily_guidance": "Express love openly. Make choices that honor your true values and deepen connections.",
            "keywords": ["love", "harmony", "choices", "values", "partnership"]
        },
        "reversed": {
            "meaning": "Disharmony, imbalance, or misaligned values. Relationships may face challenges or choices feel conflicted.",
            "daily_guidance": "Examine where your actions don't match your values. Seek to restore harmony.",
            "keywords": ["disharmony", "imbalance", "miscommunication", "detachment", "conflict"]
        }
    },
    "chariot": {
        "upright": {
            "meaning": "Determination, willpower, and victory. Move forward with confidence—success comes through focused effort.",
            "daily_guidance": "Take control and push forward. Obstacles can be overcome with determination today.",
            "keywords": ["determination", "control", "success", "ambition", "willpower"]
        },
        "reversed": {
            "meaning": "Lack of direction, aggression, or obstacles. You may feel stuck or be forcing situations inappropriately.",
            "daily_guidance": "Don't force progress. If you feel blocked, reassess your direction rather than pushing harder.",
            "keywords": ["obstacles", "lack of control", "aggression", "defeat", "aimlessness"]
        }
    },
    "strength": {
        "upright": {
            "meaning": "Inner strength, courage, and compassion. True power comes from patience and gentle perseverance, not force.",
            "daily_guidance": "Lead with compassion. Your quiet strength accomplishes more than aggression.",
            "keywords": ["courage", "patience", "compassion", "influence", "inner strength"]
        },
        "reversed": {
            "meaning": "Self-doubt, weakness, or raw emotions. You may be struggling with confidence or letting fears control you.",
            "daily_guidance": "Reconnect with your inner power. Don't let doubt or anxiety overwhelm you.",
            "keywords": ["self-doubt", "weakness", "insecurity", "low energy", "vulnerability"]
        }
    },
    "hermit": {
        "upright": {
            "meaning": "Soul-searching, introspection, and inner guidance. Time alone brings wisdom and clarity.",
            "daily_guidance": "Take time for solitude and reflection. The answers you seek are within.",
            "keywords": ["introspection", "solitude", "guidance", "wisdom", "inner search"]
        },
        "reversed": {
            "meaning": "Isolation, loneliness, or withdrawal. You may be isolating too much or avoiding necessary self-reflection.",
            "daily_guidance": "Balance solitude with connection. Don't use isolation as escape.",
            "keywords": ["isolation", "loneliness", "withdrawal", "paranoia", "antisocial"]
        }
    },
    "wheel": {
        "upright": {
            "meaning": "Change, cycles, and fate. The wheel turns in your favor—embrace change and trust the timing.",
            "daily_guidance": "Change is coming. Go with the flow and trust that fortune favors you today.",
            "keywords": ["change", "cycles", "destiny", "luck", "turning point"]
        },
        "reversed": {
            "meaning": "Bad luck, resistance to change, or broken cycles. You may be fighting inevitable change.",
            "daily_guidance": "Accept what you cannot control. Resistance to natural change creates more struggle.",
            "keywords": ["resistance", "bad luck", "setbacks", "external forces", "unwelcome change"]
        }
    },
    "justice": {
        "upright": {
            "meaning": "Fairness, truth, and cause and effect. Act with integrity—karma is active and justice prevails.",
            "daily_guidance": "Act fairly and honestly. Legal matters and decisions favor truth and balance.",
            "keywords": ["fairness", "truth", "law", "karma", "accountability"]
        },
        "reversed": {
            "meaning": "Injustice, dishonesty, or avoiding accountability. There may be unfairness or lack of balance.",
            "daily_guidance": "Take responsibility for your actions. Watch for unfair treatment or dishonesty.",
            "keywords": ["injustice", "dishonesty", "unfairness", "blame", "corruption"]
        }
    },
    "hanged": {
        "upright": {
            "meaning": "Pause, surrender, and new perspectives. Suspension leads to enlightenment—let go and see differently.",
            "daily_guidance": "Pause and see your situation from a new angle. Surrender control to gain insight.",
            "keywords": ["pause", "surrender", "sacrifice", "perspective", "letting go"]
        },
        "reversed": {
            "meaning": "Stalling, resistance, or unnecessary sacrifice. You may be stuck in indecision or martyrdom.",
            "daily_guidance": "Stop sacrificing needlessly. Make a decision rather than remaining in limbo.",
            "keywords": ["stalling", "resistance", "indecision", "martyrdom", "delay"]
        }
    },
    "death": {
        "upright": {
            "meaning": "Endings, transformation, and transition. Something must end for the new to begin—embrace the transformation.",
            "daily_guidance": "Release what no longer serves you. Transformation brings renewal and growth.",
            "keywords": ["endings", "transformation", "transition", "change", "release"]
        },
        "reversed": {
            "meaning": "Resistance to change, stagnation, or fear of endings. You may be holding onto what needs to go.",
            "daily_guidance": "Stop resisting inevitable change. Holding on creates more pain than letting go.",
            "keywords": ["resistance", "stagnation", "fear of change", "decay", "immobility"]
        }
    },
    "temperance": {
        "upright": {
            "meaning": "Balance, moderation, and patience. Blend different aspects of your life harmoniously.",
            "daily_guidance": "Practice moderation and patience. Balanced approaches succeed today.",
            "keywords": ["balance", "moderation", "patience", "purpose", "harmony"]
        },
        "reversed": {
            "meaning": "Imbalance, excess, or lack of patience. You may be going to extremes or lacking self-control.",
            "daily_guidance": "Look for where you're out of balance. Slow down and find your center.",
            "keywords": ["imbalance", "excess", "lack of vision", "discord", "overindulgence"]
        }
    },
    "devil": {
        "upright": {
            "meaning": "Shadow self, attachment, and restriction. Examine what binds you—addictions, unhealthy patterns, or limiting beliefs.",
            "daily_guidance": "Face your shadows honestly. You have more power to break free than you realize.",
            "keywords": ["shadow self", "attachment", "addiction", "restriction", "materialism"]
        },
        "reversed": {
            "meaning": "Breaking free, release, and reclaiming power. You're ready to let go of what has held you captive.",
            "daily_guidance": "You're breaking free from restrictions. Celebrate your liberation and keep moving forward.",
            "keywords": ["release", "freedom", "independence", "detachment", "reclaiming power"]
        }
    },
    "tower": {
        "upright": {
            "meaning": "Sudden change, upheaval, and revelation. Structures built on false foundations crumble—embrace the truth.",
            "daily_guidance": "Expect the unexpected. Sudden changes, though jarring, clear the way for rebuilding stronger.",
            "keywords": ["sudden change", "upheaval", "revelation", "chaos", "awakening"]
        },
        "reversed": {
            "meaning": "Avoiding disaster, fear of change, or delayed upheaval. You may be resisting necessary destruction.",
            "daily_guidance": "Don't prolong inevitable change. Better to face disruption now than disaster later.",
            "keywords": ["avoiding disaster", "fear of change", "resistance", "prolonged pain", "delayed"]
        }
    },
    "star": {
        "upright": {
            "meaning": "Hope, inspiration, and serenity. After difficulty comes healing—trust in the universe's guidance.",
            "daily_guidance": "Have faith and stay hopeful. Inspiration and healing flow to you today.",
            "keywords": ["hope", "faith", "inspiration", "renewal", "serenity"]
        },
        "reversed": {
            "meaning": "Despair, lack of faith, or disconnection. You may have lost hope or feel spiritually empty.",
            "daily_guidance": "Reconnect with hope. Even small steps toward faith can restore your spirit.",
            "keywords": ["despair", "lack of faith", "discouragement", "disconnection", "hopelessness"]
        }
    },
    "moon": {
        "upright": {
            "meaning": "Illusion, fear, and the subconscious. Not everything is as it seems—trust your intuition through uncertainty.",
            "daily_guidance": "Navigate uncertainty with intuition. Dreams and emotions carry important messages.",
            "keywords": ["illusion", "fear", "subconscious", "intuition", "uncertainty"]
        },
        "reversed": {
            "meaning": "Release of fear, truth revealed, or overcoming anxiety. Confusion clears as truth emerges.",
            "daily_guidance": "Confusion lifts and fears fade. Trust the clarity that's emerging.",
            "keywords": ["clarity", "understanding", "release of fear", "truth", "recovery"]
        }
    },
    "sun": {
        "upright": {
            "meaning": "Joy, success, and vitality. Bask in positivity—everything shines bright with optimism and achievement.",
            "daily_guidance": "Embrace joy and success. This is an excellent day for happiness and celebration.",
            "keywords": ["joy", "success", "vitality", "positivity", "optimism"]
        },
        "reversed": {
            "meaning": "Temporary setbacks, lack of enthusiasm, or delayed success. The light dims but doesn't disappear.",
            "daily_guidance": "Don't let temporary clouds diminish your inner light. Success is delayed, not denied.",
            "keywords": ["temporary depression", "lack of success", "sadness", "delays", "pessimism"]
        }
    },
    "judgement": {
        "upright": {
            "meaning": "Reflection, reckoning, and awakening. A time of evaluation and answering a higher calling.",
            "daily_guidance": "Reflect on your journey and heed your calling. Major decisions bring transformation.",
            "keywords": ["judgement", "rebirth", "inner calling", "reflection", "awakening"]
        },
        "reversed": {
            "meaning": "Self-doubt, inner critic, or ignoring the call. You may be avoiding necessary self-evaluation.",
            "daily_guidance": "Don't ignore your inner calling. Silence the harsh critic and answer with courage.",
            "keywords": ["self-doubt", "inner critic", "self-judgment", "refusal", "avoidance"]
        }
    },
    "world": {
        "upright": {
            "meaning": "Completion, achievement, and wholeness. A cycle completes successfully—celebrate your journey.",
            "daily_guidance": "Celebrate accomplishment and integration. You've achieved wholeness in an area of life.",
            "keywords": ["completion", "achievement", "fulfillment", "wholeness", "travel"]
        },
        "reversed": {
            "meaning": "Incompletion, lack of closure, or seeking personal closure. Something remains unfinished.",
            "daily_guidance": "Complete what's unfinished before starting new ventures. Closure brings freedom.",
            "keywords": ["incompletion", "emptiness", "lack of achievement", "stagnation", "unfulfilled"]
        }
    },
}


class DailyTarotResponse(BaseModel):
    card: dict
    is_reversed: bool
    already_drawn: bool
    interpretation: str
    daily_guidance: str
    keywords: List[str]


@router.get("/cards")
async def get_all_cards():
    """Get all tarot cards."""
    return MAJOR_ARCANA


@router.get("/daily", response_model=DailyTarotResponse)
async def get_daily_card(
    force_new: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily tarot card. Premium users can force a new draw."""
    # Use user's timezone for date calculation
    today = get_user_today(current_user.timezone or 'UTC')

    # Premium users can force a new draw; free users get once per day
    if not force_new or not current_user.is_premium:
        # Check if user already drew today
        existing = db.query(TarotHistory).filter(
            TarotHistory.user_id == current_user.id,
            TarotHistory.position == "single"
        ).order_by(TarotHistory.reading_date.desc()).first()

        if existing and existing.reading_date.date() == today:
            card = next((c for c in MAJOR_ARCANA if c["id"] == existing.card_id), None)
            interp = CARD_INTERPRETATIONS.get(existing.card_id, {})
            reading_type = "reversed" if existing.is_reversed else "upright"
            reading = interp.get(reading_type, {})

            return DailyTarotResponse(
                card=card,
                is_reversed=existing.is_reversed,
                already_drawn=True,
                interpretation=reading.get("meaning", ""),
                daily_guidance=reading.get("daily_guidance", ""),
                keywords=reading.get("keywords", [])
            )

    # Draw new card - use date seed for free users, true random for premium force_new
    if force_new and current_user.is_premium:
        random.seed()  # True random for premium users
    else:
        day_seed = today.toordinal() + hash(str(current_user.id)) % 1000
        random.seed(day_seed)
    card = random.choice(MAJOR_ARCANA)
    is_reversed = random.random() < 0.33

    # Save to history
    history = TarotHistory(
        user_id=current_user.id,
        card_id=card["id"],
        is_reversed=is_reversed,
        position="single"
    )
    db.add(history)
    db.commit()

    # Get interpretation
    interp = CARD_INTERPRETATIONS.get(card["id"], {})
    reading_type = "reversed" if is_reversed else "upright"
    reading = interp.get(reading_type, {})

    return DailyTarotResponse(
        card=card,
        is_reversed=is_reversed,
        already_drawn=False,
        interpretation=reading.get("meaning", ""),
        daily_guidance=reading.get("daily_guidance", ""),
        keywords=reading.get("keywords", [])
    )


@router.get("/spread")
async def get_three_card_spread(
    force_new: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a 3-card spread (past, present, future). Premium users can force new draws."""
    # Use user's timezone for date calculation
    today = get_user_today(current_user.timezone or 'UTC')
    positions = ["past", "present", "future"]

    # Premium users can force a new draw; free users get once per day
    if not force_new or not current_user.is_premium:
        # Check if user already did a spread today
        existing_spread = db.query(TarotHistory).filter(
            TarotHistory.user_id == current_user.id,
            TarotHistory.position.in_(positions)
        ).order_by(TarotHistory.reading_date.desc()).limit(3).all()

        # Check if the spread is from today
        if existing_spread and len(existing_spread) == 3:
            first_card = existing_spread[0]
            if first_card.reading_date.date() == today:
                # Return existing spread
                result = []
                for entry in reversed(existing_spread):  # Reverse to get past, present, future order
                    card = next((c for c in MAJOR_ARCANA if c["id"] == entry.card_id), MAJOR_ARCANA[0])
                    interp = CARD_INTERPRETATIONS.get(entry.card_id, {})
                    reading_type = "reversed" if entry.is_reversed else "upright"
                    reading = interp.get(reading_type, {})

                    result.append({
                        "card": card,
                        "is_reversed": entry.is_reversed,
                        "position": entry.position,
                        "already_drawn": True,
                        "interpretation": reading.get("meaning", ""),
                        "daily_guidance": reading.get("daily_guidance", ""),
                        "keywords": reading.get("keywords", [])
                    })
                return result


    # Draw new spread - use date seed for free users, true random for premium force_new
    if force_new and current_user.is_premium:
        random.seed()  # True random for premium users
    else:
        day_seed = today.toordinal() + hash(str(current_user.id)) % 10000 + 1000
        random.seed(day_seed)
    shuffled = random.sample(MAJOR_ARCANA, 3)

    result = []
    for i, card in enumerate(shuffled):
        is_reversed = random.random() < 0.33

        # Get interpretation
        interp = CARD_INTERPRETATIONS.get(card["id"], {})
        reading_type = "reversed" if is_reversed else "upright"
        reading = interp.get(reading_type, {})

        history = TarotHistory(
            user_id=current_user.id,
            card_id=card["id"],
            is_reversed=is_reversed,
            position=positions[i]
        )
        db.add(history)

        result.append({
            "card": card,
            "is_reversed": is_reversed,
            "position": positions[i],
            "already_drawn": False,
            "interpretation": reading.get("meaning", ""),
            "daily_guidance": reading.get("daily_guidance", ""),
            "keywords": reading.get("keywords", [])
        })

    db.commit()
    return result


@router.get("/history", response_model=List[TarotHistoryResponse])
async def get_tarot_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get user's tarot reading history."""
    history = db.query(TarotHistory).filter(
        TarotHistory.user_id == current_user.id
    ).order_by(TarotHistory.reading_date.desc()).limit(limit).all()
    return history


# ==================== AI PERSONALIZED TAROT ====================

class AITarotRequest(BaseModel):
    card_id: str
    is_reversed: bool
    user_name: Optional[str] = None
    zodiac_sign: Optional[str] = None
    question: Optional[str] = None  # User's specific question for the reading


class AITarotResponse(BaseModel):
    personalized_reading: str
    daily_advice: str
    reflection_prompt: str
    affirmation: str


@router.post("/ai-reading", response_model=AITarotResponse)
async def get_ai_tarot_reading(
    request: AITarotRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate an AI-powered personalized tarot reading."""
    import os
    import httpx

    # Get card details
    card = next((c for c in MAJOR_ARCANA if c["id"] == request.card_id), None)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    card_name = card["name"]
    orientation = "reversed" if request.is_reversed else "upright"

    # Get base interpretation
    interp = CARD_INTERPRETATIONS.get(request.card_id, {}).get(orientation, {})
    base_meaning = interp.get("meaning", "")

    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        try:
            # Build personalization context
            name_text = f"for {request.user_name}" if request.user_name else ""
            zodiac_text = f"Their zodiac sign is {request.zodiac_sign.title()}." if request.zodiac_sign else ""
            question_text = f"They asked: \"{request.question}\"" if request.question else "They drew this card for general daily guidance."

            prompt = f"""You are a mystical tarot reader providing a deeply personal reading.

Card Drawn: {card_name} ({orientation})
Base Meaning: {base_meaning}
{zodiac_text}
{question_text}

Generate a personalized tarot reading {name_text}. Be warm, insightful, and mystical.

Provide:
1. personalized_reading: A 3-4 sentence reading that feels personal and speaks directly to them. If they asked a question, address it. Reference their zodiac if provided.
2. daily_advice: One practical piece of advice for today (1-2 sentences)
3. reflection_prompt: One question for them to reflect on today
4. affirmation: A short, powerful affirmation related to the card (one sentence)

Respond ONLY with valid JSON:
{{"personalized_reading": "...", "daily_advice": "...", "reflection_prompt": "...", "affirmation": "..."}}
"""

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={api_key}"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.85,
                            "maxOutputTokens": 500,
                        }
                    }
                )

                if response.status_code == 200:
                    import json
                    import re

                    data = response.json()
                    text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

                    json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
                    if json_match:
                        try:
                            parsed = json.loads(json_match.group())
                            return AITarotResponse(
                                personalized_reading=parsed.get('personalized_reading', ''),
                                daily_advice=parsed.get('daily_advice', ''),
                                reflection_prompt=parsed.get('reflection_prompt', ''),
                                affirmation=parsed.get('affirmation', '')
                            )
                        except json.JSONDecodeError:
                            pass

        except Exception as e:
            pass  # Fall back to static reading

    # Fallback to enhanced static reading
    name_prefix = f"{request.user_name}, " if request.user_name else ""
    zodiac_flavor = f" As a {request.zodiac_sign.title()}, this resonates with your natural strengths." if request.zodiac_sign else ""

    return AITarotResponse(
        personalized_reading=f"{name_prefix}{card_name} ({orientation}) has appeared for you today. {base_meaning}{zodiac_flavor}",
        daily_advice=interp.get("daily_guidance", "Trust your intuition and stay open to the messages around you."),
        reflection_prompt=f"How does the energy of {card_name} show up in your current situation?",
        affirmation=f"I embrace the wisdom of {card_name} and trust my journey."
    )

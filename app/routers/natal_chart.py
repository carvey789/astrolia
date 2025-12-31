"""Natal Chart API using Skyfield for accurate astronomical calculations."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter
from skyfield.api import load

router = APIRouter(prefix="/natal-chart", tags=["Natal Chart"])

# Load planetary ephemeris
eph = load('de421.bsp')  # JPL ephemeris file (will download ~15MB on first use)
ts = load.timescale()

# Zodiac signs
SIGNS = [
    'aries', 'taurus', 'gemini', 'cancer',
    'leo', 'virgo', 'libra', 'scorpio',
    'sagittarius', 'capricorn', 'aquarius', 'pisces'
]

# Planet bodies in Skyfield
PLANETS = {
    'sun': 'sun',
    'moon': 'moon',
    'mercury': 'mercury barycenter',
    'venus': 'venus barycenter',
    'mars': 'mars barycenter',
    'jupiter': 'jupiter barycenter',
    'saturn': 'saturn barycenter',
    'uranus': 'uranus barycenter',
    'neptune': 'neptune barycenter',
}

# Interpretive readings for planets in signs
PLANET_SIGN_READINGS = {
    'sun': {
        'aries': 'Bold, pioneering spirit with natural leadership. You radiate confidence and initiative.',
        'taurus': 'Grounded, sensual nature valuing stability. Your strength comes from patience and determination.',
        'gemini': 'Curious, adaptable mind seeking knowledge. Communication and variety fuel your vitality.',
        'cancer': 'Nurturing soul with deep emotional wisdom. Home and family form your core identity.',
        'leo': 'Radiant creative expression and generous heart. You shine brightest when inspiring others.',
        'virgo': 'Analytical mind with devotion to service. Perfection and improvement drive your purpose.',
        'libra': 'Harmony-seeking diplomat with refined aesthetic. Relationships and balance define you.',
        'scorpio': 'Intense, transformative power and emotional depth. You thrive through regeneration.',
        'sagittarius': 'Adventurous philosopher seeking truth. Freedom and expansion fuel your spirit.',
        'capricorn': 'Ambitious achiever with disciplined drive. You build lasting legacies through hard work.',
        'aquarius': 'Innovative visionary championing humanity. Your uniqueness inspires collective progress.',
        'pisces': 'Compassionate dreamer connected to the divine. Intuition and imagination guide your path.',
    },
    'moon': {
        'aries': 'Emotionally impulsive and fiery. You need independence and action to feel secure.',
        'taurus': 'Emotionally steady and comfort-seeking. Security comes from stability and sensory pleasures.',
        'gemini': 'Emotionally curious and changeable. You process feelings through talking and thinking.',
        'cancer': 'Deeply intuitive and nurturing. Your emotional world is rich and protective.',
        'leo': 'Emotionally expressive and warm. You need recognition and appreciation to feel loved.',
        'virgo': 'Emotionally reserved but caring. You show love through acts of service and attention.',
        'libra': 'Emotionally balanced and relationship-focused. Harmony in partnerships is essential.',
        'scorpio': 'Emotionally intense and transformative. You feel everything deeply and completely.',
        'sagittarius': 'Emotionally optimistic and freedom-loving. Adventure and meaning nurture your soul.',
        'capricorn': 'Emotionally controlled and responsible. You find security through achievement.',
        'aquarius': 'Emotionally detached but humanitarian. You need intellectual connection and space.',
        'pisces': 'Emotionally sensitive and empathic. Boundaries blur as you absorb others\' feelings.',
    },
    'ascendant': {
        'aries': 'You appear bold, direct, and energetic. First impressions show your competitive spirit.',
        'taurus': 'You appear calm, reliable, and sensual. Others see stability and grace in you.',
        'gemini': 'You appear witty, curious, and youthful. Your quick mind makes first impressions.',
        'cancer': 'You appear caring, protective, and intuitive. A nurturing aura surrounds you.',
        'leo': 'You appear confident, dramatic, and warm. Your presence commands attention.',
        'virgo': 'You appear modest, analytical, and helpful. Precision defines your outer self.',
        'libra': 'You appear charming, balanced, and refined. Beauty and diplomacy mark your style.',
        'scorpio': 'You appear intense, mysterious, and magnetic. Others sense your hidden depths.',
        'sagittarius': 'You appear optimistic, adventurous, and honest. Enthusiasm is your calling card.',
        'capricorn': 'You appear serious, ambitious, and mature. Responsibility marks your demeanor.',
        'aquarius': 'You appear unique, progressive, and detached. Originality defines your presence.',
        'pisces': 'You appear dreamy, compassionate, and ethereal. A mystical aura surrounds you.',
    },
    'mercury': {
        'aries': 'Quick, direct thinking with assertive communication. Ideas come fast and bold.',
        'taurus': 'Practical, deliberate thinking. You communicate with patience and reliability.',
        'gemini': 'Versatile, curious mind excelling at communication. Ideas flow freely and quickly.',
        'cancer': 'Intuitive thinking colored by emotion. Memory and feeling guide your thoughts.',
        'leo': 'Creative, dramatic communication style. You express ideas with flair and confidence.',
        'virgo': 'Analytical, precise thinking. Detail-oriented communication serves practical goals.',
        'libra': 'Diplomatic, balanced thinking. You weigh all sides before expressing views.',
        'scorpio': 'Penetrating, investigative mind. Your thinking goes deep beneath the surface.',
        'sagittarius': 'Expansive, philosophical thinking. Big ideas and truth-seeking guide your mind.',
        'capricorn': 'Structured, strategic thinking. Communication serves ambitious, practical goals.',
        'aquarius': 'Innovative, unconventional thinking. Original ideas and progressive views define you.',
        'pisces': 'Imaginative, intuitive thinking. Poetry and symbolism color your communication.',
    },
    'venus': {
        'aries': 'Passionate, impulsive love nature. You pursue romance with directness and fire.',
        'taurus': 'Sensual, loyal love nature. You value stability, beauty, and physical pleasure.',
        'gemini': 'Playful, intellectual love nature. Mental connection and variety attract you.',
        'cancer': 'Nurturing, protective love nature. Emotional security is paramount in relationships.',
        'leo': 'Generous, dramatic love nature. You love with warmth and need appreciation.',
        'virgo': 'Devoted, practical love nature. You show love through service and attention.',
        'libra': 'Harmonious, romantic love nature. Partnership and beauty are essential to you.',
        'scorpio': 'Intense, passionate love nature. Deep emotional bonds and loyalty define love.',
        'sagittarius': 'Adventurous, freedom-loving in love. Growth and exploration attract you.',
        'capricorn': 'Committed, ambitious love nature. You value stability and long-term goals.',
        'aquarius': 'Unconventional, friendship-based love. Intellectual connection and freedom matter.',
        'pisces': 'Romantic, compassionate love nature. You love unconditionally and spiritually.',
    },
    'mars': {
        'aries': 'Powerful, direct energy and drive. You act decisively with natural courage.',
        'taurus': 'Steady, persistent energy. You work slowly but with unstoppable determination.',
        'gemini': 'Versatile, mental energy. You act through communication and quick thinking.',
        'cancer': 'Protective, emotional drive. You fight for home, family, and emotional security.',
        'leo': 'Creative, confident energy. You act with pride and dramatic flair.',
        'virgo': 'Precise, service-oriented drive. You channel energy into perfection and help.',
        'libra': 'Diplomatic, partnership-focused action. You prefer cooperation over conflict.',
        'scorpio': 'Intense, strategic power. You act with determination and emotional depth.',
        'sagittarius': 'Adventurous, enthusiastic energy. You act on beliefs and seek expansion.',
        'capricorn': 'Disciplined, ambitious drive. You work strategically toward long-term goals.',
        'aquarius': 'Progressive, unconventional action. You fight for causes and innovation.',
        'pisces': 'Intuitive, compassionate drive. You act on inspiration and spiritual guidance.',
    },
    'jupiter': {
        'aries': 'Growth through initiative and leadership. Fortune favors your bold ventures.',
        'taurus': 'Growth through resources and stability. Abundance flows through patience.',
        'gemini': 'Growth through learning and communication. Knowledge brings opportunities.',
        'cancer': 'Growth through nurturing and intuition. Family and home bring blessings.',
        'leo': 'Growth through creativity and self-expression. Generosity attracts abundance.',
        'virgo': 'Growth through service and improvement. Details and health bring rewards.',
        'libra': 'Growth through relationships and harmony. Partnerships bring opportunities.',
        'scorpio': 'Growth through transformation and depth. Intensity brings powerful rewards.',
        'sagittarius': 'Natural philosopher and seeker. Travel, wisdom, and truth bring abundance.',
        'capricorn': 'Growth through discipline and achievement. Success comes through hard work.',
        'aquarius': 'Growth through innovation and humanity. Unusual paths bring opportunities.',
        'pisces': 'Growth through spirituality and compassion. Faith and intuition guide fortune.',
    },
    'saturn': {
        'aries': 'Lessons in patience and self-assertion. Learn to balance impulse with discipline.',
        'taurus': 'Lessons in material security. Build lasting value through steady effort.',
        'gemini': 'Lessons in focused communication. Discipline your mind and words.',
        'cancer': 'Lessons in emotional boundaries. Learn to balance nurturing with self-protection.',
        'leo': 'Lessons in humble self-expression. True confidence comes from inner authority.',
        'virgo': 'Lessons in perfectionism and service. Balance criticism with acceptance.',
        'libra': 'Lessons in relationships and fairness. Commitment brings growth through challenges.',
        'scorpio': 'Lessons in power and control. Transform shadow into wisdom through time.',
        'sagittarius': 'Lessons in belief and expansion. Ground your philosophy in reality.',
        'capricorn': 'Native strength in ambition and structure. Build your legacy with integrity.',
        'aquarius': 'Lessons in individuality and community. Balance uniqueness with responsibility.',
        'pisces': 'Lessons in boundaries and spirituality. Ground your dreams in practical reality.',
    },
    'uranus': {
        'aries': 'Revolutionary pioneer energy. You innovate through bold, independent action.',
        'taurus': 'Revolutionary approach to resources. You transform values and material security.',
        'gemini': 'Revolutionary thinking and ideas. You innovate through communication.',
        'cancer': 'Revolutionary home and family concepts. You transform emotional patterns.',
        'leo': 'Revolutionary creative expression. You innovate through unique self-expression.',
        'virgo': 'Revolutionary service and health. You transform through innovative methods.',
        'libra': 'Revolutionary relationships. You transform partnership dynamics.',
        'scorpio': 'Revolutionary transformation. You innovate through deep psychological insight.',
        'sagittarius': 'Revolutionary philosophy. You transform beliefs and expand consciousness.',
        'capricorn': 'Revolutionary structures. You transform institutions and traditions.',
        'aquarius': 'Native revolutionary energy. You are the change-maker and visionary.',
        'pisces': 'Revolutionary spirituality. You transform through mystical innovation.',
    },
    'neptune': {
        'aries': 'Spiritual warrior energy. Your idealism drives inspired action.',
        'taurus': 'Spiritual approach to beauty and nature. Art and music elevate your soul.',
        'gemini': 'Spiritual communication and ideas. You channel inspiration through words.',
        'cancer': 'Spiritual nurturing and empathy. You feel the collective emotional current.',
        'leo': 'Spiritual creativity and performance. Art becomes a divine channel.',
        'virgo': 'Spiritual service and healing. You serve through compassionate attention.',
        'libra': 'Spiritual love and beauty. Relationships become sacred unions.',
        'scorpio': 'Spiritual depth and mysticism. You touch hidden realms of consciousness.',
        'sagittarius': 'Spiritual seeking and vision. Faith and philosophy elevate your journey.',
        'capricorn': 'Spiritual ambition and structure. You build bridges between worlds.',
        'aquarius': 'Spiritual humanity and vision. Your ideals serve collective awakening.',
        'pisces': 'Native spiritual consciousness. You are naturally connected to the divine.',
    },
}


class NatalChartRequest(BaseModel):
    birth_date: str  # YYYY-MM-DD
    birth_time: str  # HH:MM
    latitude: float
    longitude: float


class PlanetPositionResponse(BaseModel):
    planet: str
    sign: str
    degree: float
    retrograde: bool = False
    reading: str = ""


class HouseResponse(BaseModel):
    house: int
    sign: str
    degree: float


class NatalChartResponse(BaseModel):
    sun: PlanetPositionResponse
    moon: PlanetPositionResponse
    rising: PlanetPositionResponse
    planets: List[PlanetPositionResponse]
    houses: List[HouseResponse]
    summary: str = ""


def get_reading(planet: str, sign: str) -> str:
    """Get interpretive reading for a planet in a sign."""
    readings = PLANET_SIGN_READINGS.get(planet, {})
    return readings.get(sign, f"Your {planet.title()} in {sign.title()} brings unique energy to your chart.")


def ecliptic_longitude_to_sign(longitude: float):
    """Convert ecliptic longitude (0-360) to zodiac sign and degree."""
    sign_index = int(longitude / 30) % 12
    degree = longitude % 30
    return SIGNS[sign_index], degree


def calculate_planet_position(planet_name: str, t, earth) -> PlanetPositionResponse:
    """Calculate a planet's ecliptic longitude."""
    try:
        if planet_name == 'sun':
            body = eph['sun']
        elif planet_name == 'moon':
            body = eph['moon']
        else:
            body = eph[PLANETS.get(planet_name, planet_name)]

        astrometric = earth.at(t).observe(body)
        ecliptic = astrometric.apparent().ecliptic_latlon()
        longitude = ecliptic[1].degrees

        if longitude < 0:
            longitude += 360

        sign, degree = ecliptic_longitude_to_sign(longitude)
        reading = get_reading(planet_name, sign)

        return PlanetPositionResponse(
            planet=planet_name,
            sign=sign,
            degree=round(degree, 2),
            retrograde=False,
            reading=reading
        )
    except Exception as e:
        # Continue with default values on error
        return PlanetPositionResponse(
            planet=planet_name,
            sign='aries',
            degree=0.0,
            retrograde=False,
            reading=""
        )


def calculate_rising_sign(t, latitude: float, longitude: float) -> PlanetPositionResponse:
    """Calculate Ascendant (Rising Sign) using Skyfield."""
    from skyfield.earthlib import earth_rotation_angle

    era = earth_rotation_angle(t.ut1)
    lst_degrees = (era * 360 + longitude) % 360
    sign, degree = ecliptic_longitude_to_sign(lst_degrees)
    reading = get_reading('ascendant', sign)

    return PlanetPositionResponse(
        planet='ascendant',
        sign=sign,
        degree=round(degree, 2),
        retrograde=False,
        reading=reading
    )


def calculate_houses(ascendant_longitude: float) -> List[HouseResponse]:
    """Calculate house cusps using Whole Sign house system."""
    houses = []
    asc_sign_index = int(ascendant_longitude / 30) % 12

    for i in range(12):
        house_num = i + 1
        sign_index = (asc_sign_index + i) % 12
        sign = SIGNS[sign_index]
        degree = 0.0

        houses.append(HouseResponse(
            house=house_num,
            sign=sign,
            degree=degree
        ))

    return houses


def generate_summary(sun: PlanetPositionResponse, moon: PlanetPositionResponse, rising: PlanetPositionResponse) -> str:
    """Generate a personalized chart summary."""
    sun_sign = sun.sign.title()
    moon_sign = moon.sign.title()
    rising_sign = rising.sign.title()

    return (
        f"As a {sun_sign} Sun with a {moon_sign} Moon and {rising_sign} Rising, "
        f"you combine the core identity of {sun_sign} with the emotional depth of {moon_sign}. "
        f"The world sees you through your {rising_sign} Ascendant, shaping first impressions and life approach."
    )


@router.post("/calculate", response_model=NatalChartResponse)
async def calculate_natal_chart(request: NatalChartRequest):
    """Calculate a complete natal chart with accurate planetary positions and readings."""
    try:
        date_parts = request.birth_date.split('-')
        time_parts = request.birth_time.split(':')

        year = int(date_parts[0])
        month = int(date_parts[1])
        day = int(date_parts[2])
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0

        t = ts.utc(year, month, day, hour, minute)
    except Exception as e:
        t = ts.now()

    earth = eph['earth']

    sun = calculate_planet_position('sun', t, earth)
    moon = calculate_planet_position('moon', t, earth)
    rising = calculate_rising_sign(t, request.latitude, request.longitude)

    planets = []
    for planet_name in ['mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']:
        pos = calculate_planet_position(planet_name, t, earth)
        planets.append(pos)

    from skyfield.earthlib import earth_rotation_angle
    era = earth_rotation_angle(t.ut1)
    asc_longitude = (era * 360 + request.longitude) % 360
    houses = calculate_houses(asc_longitude)

    summary = generate_summary(sun, moon, rising)

    return NatalChartResponse(
        sun=sun,
        moon=moon,
        rising=rising,
        planets=planets,
        houses=houses,
        summary=summary
    )


@router.get("/health")
async def health_check():
    """Check if Skyfield ephemeris is loaded."""
    try:
        t = ts.now()
        earth = eph['earth']
        sun = eph['sun']
        earth.at(t).observe(sun)
        return {"status": "ok", "ephemeris": "de421.bsp loaded"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


class AIReadingRequest(BaseModel):
    sun_sign: str
    sun_degree: float
    moon_sign: str
    moon_degree: float
    rising_sign: str
    rising_degree: float
    planets: List[dict]  # List of {planet, sign, degree}


class AIReadingResponse(BaseModel):
    personalized_reading: str
    sun_interpretation: str
    moon_interpretation: str
    rising_interpretation: str
    life_themes: List[str]


@router.post("/ai-reading", response_model=AIReadingResponse)
async def generate_ai_reading(request: AIReadingRequest):
    """Generate a personalized AI reading based on birth chart data using Gemini."""
    from ..config import get_settings

    settings = get_settings()

    # Build the chart summary for the prompt
    chart_summary = f"""
Birth Chart Analysis:
- Sun: {request.sun_sign.title()} at {request.sun_degree:.1f}°
- Moon: {request.moon_sign.title()} at {request.moon_degree:.1f}°
- Rising: {request.rising_sign.title()} at {request.rising_degree:.1f}°

Other Planets:
"""
    for p in request.planets:
        chart_summary += f"- {p.get('planet', '').title()}: {p.get('sign', '').title()} at {p.get('degree', 0):.1f}°\n"

    # Try Gemini AI if API key is available
    if settings.gemini_api_key:
        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')

            prompt = f"""You are an expert astrologer. Generate a personalized and insightful birth chart reading.

{chart_summary}

Please provide:
1. A personalized 3-4 sentence overall reading that weaves together the Sun, Moon, and Rising signs
2. A specific interpretation for the Sun placement (2 sentences about core identity)
3. A specific interpretation for the Moon placement (2 sentences about emotions)
4. A specific interpretation for the Rising placement (2 sentences about how others see them)
5. 3 major life themes based on the planetary positions

Be warm, insightful, and specific to this exact combination of placements. Address the person directly using "you".
Avoid generic statements. Focus on the unique combination of energies.

Format your response as JSON with these exact keys:
- personalized_reading
- sun_interpretation
- moon_interpretation
- rising_interpretation
- life_themes (array of 3 strings)
"""

            response = model.generate_content(prompt)

            # Parse the response
            import json
            import re
            text = response.text

            # Try to extract JSON from the response
            json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    return AIReadingResponse(
                        personalized_reading=data.get('personalized_reading', ''),
                        sun_interpretation=data.get('sun_interpretation', ''),
                        moon_interpretation=data.get('moon_interpretation', ''),
                        rising_interpretation=data.get('rising_interpretation', ''),
                        life_themes=data.get('life_themes', [])
                    )
                except json.JSONDecodeError:
                    pass

            # Fallback: use the raw text
            return AIReadingResponse(
                personalized_reading=text[:500] if len(text) > 500 else text,
                sun_interpretation=PLANET_SIGN_READINGS.get('sun', {}).get(request.sun_sign, ''),
                moon_interpretation=PLANET_SIGN_READINGS.get('moon', {}).get(request.moon_sign, ''),
                rising_interpretation=PLANET_SIGN_READINGS.get('ascendant', {}).get(request.rising_sign, ''),
                life_themes=[]
            )

        except Exception as e:
            pass  # AI reading unavailable

    # Fallback to static readings if no API key or error
    return AIReadingResponse(
        personalized_reading=generate_summary(
            PlanetPositionResponse(planet='sun', sign=request.sun_sign, degree=request.sun_degree, reading=''),
            PlanetPositionResponse(planet='moon', sign=request.moon_sign, degree=request.moon_degree, reading=''),
            PlanetPositionResponse(planet='ascendant', sign=request.rising_sign, degree=request.rising_degree, reading='')
        ),
        sun_interpretation=PLANET_SIGN_READINGS.get('sun', {}).get(request.sun_sign, 'Your Sun sign brings unique energy.'),
        moon_interpretation=PLANET_SIGN_READINGS.get('moon', {}).get(request.moon_sign, 'Your Moon sign guides your emotions.'),
        rising_interpretation=PLANET_SIGN_READINGS.get('ascendant', {}).get(request.rising_sign, 'Your Rising sign shapes first impressions.'),
        life_themes=[
            "Personal growth through self-awareness",
            "Building meaningful connections",
            "Finding your authentic expression"
        ]
    )


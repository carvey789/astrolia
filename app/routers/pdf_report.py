"""
PDF Astrology Report Router - Personalized comprehensive astrological report
"""
import os
from datetime import datetime, date
from typing import Optional
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from fpdf import FPDF

from dotenv import load_dotenv
load_dotenv()

from ..database import get_db
from ..models import User
from ..utils import get_current_user

router = APIRouter(prefix="/report", tags=["PDF Report"])

# Zodiac data for symbols and elements
ZODIAC_DATA = {
    "aries": {"symbol": "(Aries)", "element": "Fire", "ruling": "Mars"},
    "taurus": {"symbol": "(Taurus)", "element": "Earth", "ruling": "Venus"},
    "gemini": {"symbol": "(Gemini)", "element": "Air", "ruling": "Mercury"},
    "cancer": {"symbol": "(Cancer)", "element": "Water", "ruling": "Moon"},
    "leo": {"symbol": "(Leo)", "element": "Fire", "ruling": "Sun"},
    "virgo": {"symbol": "(Virgo)", "element": "Earth", "ruling": "Mercury"},
    "libra": {"symbol": "(Libra)", "element": "Air", "ruling": "Venus"},
    "scorpio": {"symbol": "(Scorpio)", "element": "Water", "ruling": "Pluto"},
    "sagittarius": {"symbol": "(Sagittarius)", "element": "Fire", "ruling": "Jupiter"},
    "capricorn": {"symbol": "(Capricorn)", "element": "Earth", "ruling": "Saturn"},
    "aquarius": {"symbol": "(Aquarius)", "element": "Air", "ruling": "Uranus"},
    "pisces": {"symbol": "(Pisces)", "element": "Water", "ruling": "Neptune"},
}


class AstrologyPDF(FPDF):
    """Custom PDF class with cosmic styling and visual graphics"""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        # Dark purple header bar
        self.set_fill_color(26, 26, 46)  # #1a1a2e
        self.rect(0, 0, 210, 30, 'F')

        # Decorative circles (stars)
        self.set_fill_color(255, 215, 0)  # Gold
        self.ellipse(180, 5, 3, 3, 'F')
        self.ellipse(190, 10, 2, 2, 'F')
        self.ellipse(175, 15, 2, 2, 'F')
        self.ellipse(195, 20, 1.5, 1.5, 'F')

        # Gold accent line
        self.set_draw_color(255, 215, 0)  # Gold
        self.set_line_width(1)
        self.line(0, 30, 210, 30)

        # Title
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(255, 215, 0)  # Gold
        self.set_xy(10, 8)
        self.cell(0, 10, 'ASTROLIA', align='L')

        # Subtitle
        self.set_font('Helvetica', '', 10)
        self.set_text_color(200, 200, 220)
        self.set_xy(10, 18)
        self.cell(0, 5, 'Your Personal Astrology Report', align='L')

        self.ln(30)

    def footer(self):
        # Footer bar
        self.set_y(-20)
        self.set_fill_color(26, 26, 46)
        self.rect(0, self.get_y(), 210, 20, 'F')

        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(200, 200, 220)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%B %d, %Y")} | Astrolia App', align='C')

    def section_title(self, title: str):
        """Add a styled section title with decorative box"""
        # Background box
        self.set_fill_color(155, 125, 255)  # Mystic violet
        self.rect(10, self.get_y(), 4, 8, 'F')

        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(60, 40, 120)  # Dark purple
        self.set_x(18)
        self.cell(0, 8, title, ln=True)

        # Decorative line
        self.set_draw_color(200, 180, 255)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def body_text(self, text: str):
        """Add body text with proper styling"""
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50, 50, 70)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def info_box(self, label: str, value: str):
        """Add a labeled info with visual dot"""
        # Dot indicator
        self.set_fill_color(155, 125, 255)
        self.ellipse(12, self.get_y() + 2, 2, 2, 'F')

        self.set_x(18)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(100, 80, 140)
        self.cell(35, 6, f"{label}:", align='L')

        self.set_font('Helvetica', '', 10)
        self.set_text_color(50, 50, 70)
        self.cell(0, 6, value, ln=True)

    def rating_box(self, rating: int):
        """Add visual rating with filled/empty circles"""
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(100, 80, 140)
        self.cell(40, 6, "Today's Rating:", align='L')

        # Draw rating circles
        x_start = self.get_x() + 5
        for i in range(5):
            if i < rating:
                self.set_fill_color(255, 215, 0)  # Gold filled
            else:
                self.set_fill_color(220, 220, 230)  # Empty
            self.ellipse(x_start + (i * 8), self.get_y() + 1, 5, 5, 'F')

        self.ln(8)

    def highlight_box(self, title: str, content: str, color_r: int, color_g: int, color_b: int):
        """Add a highlighted content box"""
        y_start = self.get_y()

        # Background
        self.set_fill_color(color_r, color_g, color_b)
        self.rect(10, y_start, 190, 25, 'F')

        # Left accent bar
        self.set_fill_color(min(255, color_r + 40), min(255, color_g + 40), min(255, color_b + 40))
        self.rect(10, y_start, 4, 25, 'F')

        self.set_xy(18, y_start + 3)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(80, 60, 100)
        self.cell(0, 5, title, ln=True)

        self.set_x(18)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(60, 60, 80)
        self.multi_cell(175, 4.5, content)

        self.set_y(y_start + 28)

    def transit_row(self, planet: str, sign: str, meaning: str):
        """Add a styled transit row"""
        y_start = self.get_y()

        # Planet circle
        self.set_fill_color(155, 125, 255)
        self.ellipse(12, y_start + 1, 6, 6, 'F')

        # Planet name inside
        self.set_xy(12, y_start + 1)
        self.set_font('Helvetica', 'B', 5)
        self.set_text_color(255, 255, 255)
        self.cell(6, 6, planet[0], align='C')

        # Planet and sign
        self.set_xy(22, y_start)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(80, 60, 120)
        self.cell(0, 5, f"{planet} in {sign}", ln=True)

        # Meaning
        self.set_x(22)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(80, 80, 100)
        self.cell(0, 4, meaning, ln=True)

        self.ln(1)


def get_zodiac_sign(birth_date: date) -> str:
    """Get zodiac sign from birth date"""
    month, day = birth_date.month, birth_date.day

    if (month == 3 and day >= 21) or (month == 4 and day <= 19): return "aries"
    if (month == 4 and day >= 20) or (month == 5 and day <= 20): return "taurus"
    if (month == 5 and day >= 21) or (month == 6 and day <= 20): return "gemini"
    if (month == 6 and day >= 21) or (month == 7 and day <= 22): return "cancer"
    if (month == 7 and day >= 23) or (month == 8 and day <= 22): return "leo"
    if (month == 8 and day >= 23) or (month == 9 and day <= 22): return "virgo"
    if (month == 9 and day >= 23) or (month == 10 and day <= 22): return "libra"
    if (month == 10 and day >= 23) or (month == 11 and day <= 21): return "scorpio"
    if (month == 11 and day >= 22) or (month == 12 and day <= 21): return "sagittarius"
    if (month == 12 and day >= 22) or (month == 1 and day <= 19): return "capricorn"
    if (month == 1 and day >= 20) or (month == 2 and day <= 18): return "aquarius"
    return "pisces"


def generate_daily_reading(sign: str) -> dict:
    """Generate daily horoscope content"""
    readings = {
        "aries": "Today brings dynamic energy that fuels your ambitions. Trust your instincts and take bold action. A surprising opportunity may present itself.",
        "taurus": "Focus on stability and comfort today. Financial matters look favorable. Take time to appreciate the simple pleasures around you.",
        "gemini": "Communication flows easily today. It's an excellent time for networking and intellectual pursuits. Stay curious and open-minded.",
        "cancer": "Emotional connections deepen today. Home and family matters take priority. Trust your intuition in personal relationships.",
        "leo": "Your creative energy shines brightly. Express yourself confidently and others will be drawn to your warmth. Leadership opportunities arise.",
        "virgo": "Attention to detail pays off today. Focus on health and organization. Small improvements lead to significant results.",
        "libra": "Harmony and balance are your focus. Relationships flourish with honest communication. Artistic pursuits bring joy.",
        "scorpio": "Deep transformation continues. Trust the process of change. Hidden truths may come to light, bringing healing.",
        "sagittarius": "Adventure calls to you today. Expand your horizons through learning or travel. Optimism attracts good fortune.",
        "capricorn": "Steady progress toward goals continues. Your discipline and determination inspire others. Career matters advance positively.",
        "aquarius": "Innovation and originality are highlighted. Connect with like-minded individuals. Your unique perspective is valued.",
        "pisces": "Intuition is heightened today. Creative and spiritual pursuits flourish. Dreams may hold important messages.",
    }
    return {
        "reading": readings.get(sign, readings["aries"]),
        "rating": 4,
        "lucky_number": str((hash(sign + str(date.today())) % 9) + 1),
        "lucky_color": ["Red", "Blue", "Green", "Gold", "Purple", "Silver"][hash(sign) % 6]
    }


def generate_weekly_reading(sign: str) -> str:
    """Generate weekly overview"""
    weeks = {
        "aries": "This week emphasizes new beginnings and fresh starts. Mars energizes your ambitions mid-week. Weekend brings social opportunities.",
        "taurus": "Financial matters take center stage. Venus brings harmony to relationships. End the week with self-care and relaxation.",
        "gemini": "Communication is your superpower this week. Multiple projects demand your attention. Stay organized to maximize productivity.",
        "cancer": "Emotional depth characterizes this week. Home improvements bring satisfaction. Family connections strengthen.",
        "leo": "Creative expression flows freely. Romance and playfulness are highlighted. Share your talents with confidence.",
        "virgo": "Focus on health routines and daily habits. Small improvements accumulate into major progress. Help others who seek your advice.",
        "libra": "Partnership matters are emphasized. Seek balance between give and take. Artistic inspiration strikes unexpectedly.",
        "scorpio": "Transformation continues at a deep level. Release what no longer serves you. Power dynamics shift in your favor.",
        "sagittarius": "Adventure and learning expand your horizons. Travel plans may develop. Philosophical insights bring clarity.",
        "capricorn": "Career advancement is possible this week. Your hard work gains recognition. Set ambitious but realistic goals.",
        "aquarius": "Social connections bring opportunities. Innovative ideas find receptive audiences. Community involvement is rewarding.",
        "pisces": "Spiritual growth accelerates. Dreams are particularly meaningful. Compassion guides your interactions.",
    }
    return weeks.get(sign, weeks["aries"])


def generate_monthly_reading(sign: str) -> str:
    """Generate monthly forecast"""
    months = {
        "aries": "January 2026 brings powerful new beginnings. The New Moon mid-month ignites your personal projects. Mars supports decisive action. Focus on self-improvement and launching new ventures.",
        "taurus": "This month emphasizes financial stability and values. Venus enhances your charm and attracts resources. Build toward long-term security. Relationships deepen meaningfully.",
        "gemini": "Communication and learning are highlighted this month. Mercury supports all mental activities. Networking leads to valuable connections. Share your ideas with confidence.",
        "cancer": "Home and family matters take priority this month. Nurturing energy flows naturally. Property matters are favored. Emotional connections deepen significantly.",
        "leo": "Creative self-expression flourishes this month. Romance and playfulness bring joy. Children or creative projects thrive. Lead with heart and courage.",
        "virgo": "Health and daily routines need attention this month. Small improvements compound into major results. Service to others is especially rewarding. Stay organized.",
        "libra": "Relationships are the focus this month. Balance between self and others requires attention. Artistic pursuits bring fulfillment. Beauty surrounds you.",
        "scorpio": "Deep transformation continues this month. Release old patterns to embrace renewal. Shared resources may shift. Trust the process of rebirth.",
        "sagittarius": "Adventure and expansion call to you this month. Travel or higher learning beckons. Philosophical insights bring wisdom. Optimism attracts opportunities.",
        "capricorn": "Career and reputation are emphasized this month. Your efforts gain recognition. Ambitious goals are within reach. Structure supports success.",
        "aquarius": "Social connections and future visions are highlighted. Community involvement brings fulfillment. Innovation finds receptive audiences. Embrace your uniqueness.",
        "pisces": "Spiritual and creative pursuits flourish this month. Intuition guides important decisions. Compassion flows naturally. Dreams reveal important insights.",
    }
    return months.get(sign, months["aries"])


def generate_yearly_reading(sign: str) -> str:
    """Generate yearly outlook"""
    years = {
        "aries": "2026 is a year of bold new beginnings and personal reinvention. Major opportunities arrive in spring. Relationships evolve significantly by autumn. Trust your pioneering spirit.",
        "taurus": "2026 brings financial growth and material stability. Resources expand through steady effort. Love deepens mid-year. Security builds through patience.",
        "gemini": "2026 emphasizes communication and learning. Your voice reaches wider audiences. Travel or education expands horizons. Versatility is your greatest asset.",
        "cancer": "2026 focuses on home, family, and emotional foundations. Property matters are favorable. Nurturing relationships flourish. Security comes from within.",
        "leo": "2026 celebrates your creative expression and leadership. Romance sparkles throughout the year. Children or creative works thrive. Shine your light brightly.",
        "virgo": "2026 rewards your dedication to improvement. Health and habits transform positively. Service to others brings fulfillment. Details matter more than ever.",
        "libra": "2026 highlights relationships and partnerships of all kinds. Balance is the key theme. Artistic endeavors flourish. Beauty surrounds your life.",
        "scorpio": "2026 continues deep transformation and rebirth. Release the old to embrace renewal. Power dynamics shift favorably. Trust your regenerative abilities.",
        "sagittarius": "2026 expands your horizons through adventure and wisdom. Travel and education are highlighted. Philosophical growth brings clarity. Optimism is rewarded.",
        "capricorn": "2026 advances your career and public standing. Hard work gains significant recognition. Leadership opportunities increase. Build lasting structures.",
        "aquarius": "2026 emphasizes community, friendship, and future visions. Social networks expand meaningfully. Innovation finds its audience. Embrace humanitarian ideals.",
        "pisces": "2026 deepens spiritual connection and creative inspiration. Intuition is your guide. Compassion flows to those in need. Dreams manifest into reality.",
    }
    return years.get(sign, years["aries"])


def get_current_transits() -> list:
    """Get current planetary transits"""
    return [
        {"planet": "Pluto", "sign": "Aquarius", "meaning": "Generational transformation of society and technology"},
        {"planet": "Neptune", "sign": "Aries", "meaning": "New spiritual awakening and creative inspiration"},
        {"planet": "Uranus", "sign": "Gemini", "meaning": "Revolutionary changes in communication and thinking"},
        {"planet": "Saturn", "sign": "Aries", "meaning": "Building new structures with discipline and courage"},
        {"planet": "Jupiter", "sign": "Cancer", "meaning": "Expansion of home, family, and emotional growth"},
    ]


@router.get("/generate")
async def generate_pdf_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate personalized PDF astrology report"""

    # Get user data
    if not current_user.birth_date:
        raise HTTPException(status_code=400, detail="Birth date required for report")

    # Parse birth date
    if isinstance(current_user.birth_date, str):
        birth_date = datetime.strptime(current_user.birth_date, "%Y-%m-%d").date()
    else:
        birth_date = current_user.birth_date

    sign = get_zodiac_sign(birth_date)
    sign_lower = sign.lower()
    zodiac_info = ZODIAC_DATA.get(sign_lower, ZODIAC_DATA["aries"])

    # Create PDF
    pdf = AstrologyPDF()
    pdf.add_page()

    # === PAGE 1: Personal Profile & Daily ===

    # Profile section
    pdf.section_title("YOUR COSMIC PROFILE")
    pdf.info_box("Name", current_user.name or "Cosmic Traveler")
    pdf.info_box("Birth Date", birth_date.strftime("%B %d, %Y"))
    pdf.info_box("Sun Sign", f"{sign.title()} {zodiac_info['symbol']}")
    pdf.info_box("Element", zodiac_info['element'])
    pdf.info_box("Ruling Planet", zodiac_info['ruling'])

    birth_city = getattr(current_user, 'birth_city', None)
    if birth_city:
        pdf.info_box("Birth Place", birth_city)

    pdf.ln(8)

    # Daily horoscope
    daily = generate_daily_reading(sign_lower)
    pdf.section_title("TODAY'S HOROSCOPE")
    pdf.body_text(daily["reading"])

    pdf.rating_box(daily["rating"])

    pdf.info_box("Lucky Number", daily["lucky_number"])
    pdf.info_box("Lucky Color", daily["lucky_color"])

    pdf.ln(5)

    # Weekly overview
    pdf.section_title("THIS WEEK'S OVERVIEW")
    pdf.body_text(generate_weekly_reading(sign_lower))

    # === PAGE 2: Extended Forecasts ===
    pdf.add_page()

    # Monthly forecast
    pdf.section_title("MONTHLY FORECAST")
    pdf.body_text(generate_monthly_reading(sign_lower))

    pdf.ln(5)

    # Yearly outlook
    pdf.section_title("2026 YEARLY OUTLOOK")
    pdf.body_text(generate_yearly_reading(sign_lower))

    pdf.ln(5)

    # === Transits Section ===
    pdf.section_title("CURRENT COSMIC CLIMATE")
    pdf.body_text("Major planetary influences affecting everyone right now:")
    pdf.ln(2)

    for transit in get_current_transits():
        pdf.transit_row(transit['planet'], transit['sign'], transit['meaning'])

    pdf.ln(5)

    # Personalized advice
    pdf.section_title("PERSONALIZED GUIDANCE")

    # Highlight box for key advice
    pdf.highlight_box(
        "Your Key Theme",
        f"As a {sign.title()} with {zodiac_info['element']} energy guided by {zodiac_info['ruling']}, focus on transformation and growth.",
        240, 235, 250  # Light purple
    )

    pdf.body_text("Trust the cosmic timing - the universe is supporting your journey. Personal growth, authentic expression, and building meaningful connections are your path forward.")

    pdf.ln(3)
    pdf.highlight_box(
        "From Astra, Your AI Astrologer",
        "This report offers general guidance. For deeper personalized readings, chat with me in the Astrolia app!",
        255, 248, 220  # Light gold
    )

    # Generate PDF bytes
    pdf_bytes = pdf.output()

    # Return as streaming response
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=astrolia_report_{sign}_{date.today().isoformat()}.pdf"
        }
    )

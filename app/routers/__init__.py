from .auth import router as auth_router
from .users import router as users_router
from .journal import router as journal_router
from .tarot import router as tarot_router
from .horoscope import router as horoscope_router
from .geocoding import router as geocoding_router
from .natal_chart import router as natal_chart_router
from .numerology import router as numerology_router
from .transits import router as transits_router
from .subscription import router as subscription_router
from .astro_chat import router as astro_chat_router
from .synastry import router as synastry_router
from .pdf_report import router as pdf_report_router
from .moon_phases import router as moon_phases_router

__all__ = [
    "auth_router",
    "users_router",
    "journal_router",
    "tarot_router",
    "horoscope_router",
    "geocoding_router",
    "natal_chart_router",
    "numerology_router",
    "transits_router",
    "subscription_router",
    "astro_chat_router",
    "synastry_router",
    "pdf_report_router",
    "moon_phases_router",
]

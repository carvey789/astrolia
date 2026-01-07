from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .database import engine, Base
from .routers import (
    auth_router, users_router, journal_router, tarot_router,
    horoscope_router, geocoding_router, natal_chart_router,
    numerology_router, transits_router, subscription_router,
    astro_chat_router, synastry_router, pdf_report_router,
    moon_phases_router, affirmations_router
)

settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Backend API for Horoscope Flutter App",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(journal_router)
app.include_router(tarot_router)
app.include_router(horoscope_router)
app.include_router(geocoding_router)
app.include_router(natal_chart_router)
app.include_router(numerology_router)
app.include_router(transits_router)
app.include_router(subscription_router)
app.include_router(astro_chat_router)
app.include_router(synastry_router)
app.include_router(pdf_report_router)
app.include_router(moon_phases_router)
app.include_router(affirmations_router)


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/privacy-policy")
async def privacy_policy():
    from fastapi.responses import HTMLResponse
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Astrolia - Privacy Policy</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: -apple-system, Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }
            h1 { color: #6B46C1; }
            h2 { color: #553C9A; margin-top: 30px; }
        </style>
    </head>
    <body>
        <h1>🔮 Astrolia Privacy Policy</h1>
        <p><strong>Last Updated:</strong> January 2026</p>

        <h2>1. Information We Collect</h2>
        <p>We collect the following information to provide personalized astrology readings:</p>
        <ul>
            <li><strong>Account Info:</strong> Email address, name (optional)</li>
            <li><strong>Birth Details:</strong> Date, time, and location of birth (for natal chart calculations)</li>
            <li><strong>Journal Entries:</strong> Your personal journal notes (stored securely)</li>
        </ul>

        <h2>2. How We Use Your Information</h2>
        <ul>
            <li>Generate personalized horoscopes and birth charts</li>
            <li>Provide AI-powered astrology insights</li>
            <li>Save your preferences and journal entries</li>
        </ul>

        <h2>3. Data Storage & Security</h2>
        <p>Your data is stored securely on encrypted servers. We do not sell or share your personal information with third parties.</p>

        <h2>4. Third-Party Services</h2>
        <ul>
            <li><strong>Google AI (Gemini):</strong> Powers our AI astrologer chat</li>
            <li><strong>Authentication:</strong> Google Sign-In (optional)</li>
        </ul>

        <h2>5. Your Rights</h2>
        <p>You can request deletion of your account and all associated data at any time by contacting us.</p>
        <p><a href="mailto:carvey789@gmail.com?subject=Astrolia%20Account%20Deletion%20Request" style="color: #6B46C1; font-weight: bold;">📧 Request Account Deletion</a></p>

        <h2>6. Contact Us</h2>
        <p>For privacy concerns, contact: <strong><a href="mailto:carvey789@gmail.com" style="color: #6B46C1;">carvey789@gmail.com</a></strong></p>

        <p style="margin-top: 40px; color: #666;">© 2026 Astrolia. All rights reserved.</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

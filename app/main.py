from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .database import engine, Base
from .routers import (
    auth_router, users_router, journal_router, tarot_router,
    horoscope_router, geocoding_router, natal_chart_router,
    numerology_router, transits_router, subscription_router,
    astro_chat_router, synastry_router, pdf_report_router
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


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import get_settings

settings = get_settings()

# Connection pool settings to prevent SSL connection drops
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Test connection before use
    pool_recycle=300,    # Recycle connections after 5 minutes
    pool_size=5,         # Max connections in pool
    max_overflow=10,     # Extra connections when pool is full
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

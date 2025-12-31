import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from ..database import Base


class AuthProvider(enum.Enum):
    email = "email"
    google = "google"


class SubscriptionTier(enum.Enum):
    free = "free"
    premium = "premium"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Null for OAuth users
    google_id = Column(String(255), unique=True, nullable=True)
    auth_provider = Column(SQLEnum(AuthProvider), default=AuthProvider.email)

    # Profile
    name = Column(String(100), nullable=False)
    birth_date = Column(DateTime, nullable=False)
    birth_time = Column(String(10), nullable=False)  # HH:mm format
    birth_location = Column(String(255), nullable=False)
    birth_latitude = Column(Float, nullable=True)
    birth_longitude = Column(Float, nullable=True)
    zodiac_sign_id = Column(String(50), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(100), default="UTC")

    # Subscription
    subscription_tier = Column(
        SQLEnum(SubscriptionTier), default=SubscriptionTier.free
    )
    subscription_expires_at = Column(DateTime, nullable=True)
    subscription_platform = Column(String(20), nullable=True)  # "android", "ios"
    subscription_product_id = Column(String(100), nullable=True)
    revenuecat_id = Column(String(100), nullable=True)  # RevenueCat customer ID

    # Status
    is_email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Preferences
    notifications_enabled = Column(Boolean, default=True)
    daily_horoscope_time = Column(String(10), default="08:00")
    theme = Column(String(20), default="dark")
    language = Column(String(10), default="en")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    # Push notifications
    notification_token = Column(String(500), nullable=True)

    # Relationships
    journal_entries = relationship("JournalEntry", back_populates="user", cascade="all, delete-orphan")
    tarot_history = relationship("TarotHistory", back_populates="user", cascade="all, delete-orphan")

    @property
    def is_premium(self) -> bool:
        """Check if user has active premium subscription."""
        if self.subscription_tier != SubscriptionTier.premium:
            return False
        if self.subscription_expires_at is None:
            return False
        return self.subscription_expires_at > datetime.utcnow()

    def __repr__(self):
        return f"<User {self.email}>"


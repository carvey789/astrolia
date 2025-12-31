from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
import uuid


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    birth_date: datetime
    birth_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    birth_location: str = Field(..., min_length=1, max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    birth_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    birth_location: Optional[str] = Field(None, max_length=255)
    birth_latitude: Optional[float] = None
    birth_longitude: Optional[float] = None
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None


class UserPreferences(BaseModel):
    notifications_enabled: Optional[bool] = None
    daily_horoscope_time: Optional[str] = None
    theme: Optional[str] = None
    language: Optional[str] = None


class UserResponse(UserBase):
    id: uuid.UUID
    zodiac_sign_id: str
    avatar_url: Optional[str] = None
    timezone: str
    is_email_verified: bool
    notifications_enabled: bool
    daily_horoscope_time: str
    theme: str
    language: str
    created_at: datetime

    class Config:
        from_attributes = True

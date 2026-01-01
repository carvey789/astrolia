from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=100)
    birth_date: datetime
    birth_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    birth_location: str = Field(..., min_length=1, max_length=255)
    timezone: Optional[str] = None  # IANA timezone, e.g., "Asia/Bangkok"
    birth_latitude: Optional[float] = None
    birth_longitude: Optional[float] = None


class GoogleAuthRequest(BaseModel):
    id_token: str
    name: Optional[str] = None
    birth_date: Optional[datetime] = None
    birth_time: Optional[str] = None
    birth_location: Optional[str] = None
    birth_latitude: Optional[float] = None
    birth_longitude: Optional[float] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str

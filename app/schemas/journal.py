from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid


class JournalEntryBase(BaseModel):
    intention: str = Field(..., min_length=1, max_length=1000)
    gratitude: Optional[str] = Field(None, max_length=1000)
    category: str = Field(default="general", max_length=50)


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryUpdate(BaseModel):
    intention: Optional[str] = Field(None, max_length=1000)
    gratitude: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = None
    category: Optional[str] = None


class JournalEntryResponse(JournalEntryBase):
    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TarotHistoryResponse(BaseModel):
    id: uuid.UUID
    card_id: str
    is_reversed: bool
    position: str
    reading_date: datetime

    class Config:
        from_attributes = True

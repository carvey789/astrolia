import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from ..database import Base


class ManifestationStatus(enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    manifested = "manifested"


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    intention = Column(String(1000), nullable=False)
    gratitude = Column(String(1000), nullable=True)
    status = Column(SQLEnum(ManifestationStatus), default=ManifestationStatus.pending)
    category = Column(String(50), default="general")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="journal_entries")

    def __repr__(self):
        return f"<JournalEntry {self.id}>"

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base


class TarotHistory(Base):
    __tablename__ = "tarot_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    card_id = Column(String(50), nullable=False)
    is_reversed = Column(Boolean, default=False)
    position = Column(String(20), default="single")  # single, past, present, future

    reading_date = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="tarot_history")

    def __repr__(self):
        return f"<TarotHistory {self.card_id}>"

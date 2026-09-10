import uuid
from datetime import datetime, date, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Date, String, Integer, ForeignKey, DateTime
from app.database import Base

class EmotionLog(Base):
    __tablename__ = "emotion_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    reflection_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("reflections.id", ondelete="CASCADE"), nullable=True)
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    emotion: Mapped[str] = mapped_column(String, nullable=False)
    intensity: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)  # "user_reported" or "ai_detected"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

import uuid
from datetime import datetime, date, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from sqlalchemy import Date, String, Integer, Boolean, ForeignKey, UniqueConstraint, DateTime
from app.database import Base

class DailyReflection(Base):
    __tablename__ = "reflections"
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_user_daily_reflection"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    entry_mode: Mapped[str] = mapped_column(String, nullable=False)
    answers: Mapped[dict] = mapped_column(JSONB, nullable=False)
    mood_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    energy_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reported_emotions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    ai_detected_emotions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    followup_questions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    followup_answers: Mapped[str | None] = mapped_column(String, nullable=True)
    needs_followup: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_summary: Mapped[str | None] = mapped_column(String, nullable=True)
    ai_what_went_well: Mapped[str | None] = mapped_column(String, nullable=True)
    ai_what_was_difficult: Mapped[str | None] = mapped_column(String, nullable=True)
    ai_what_was_learned: Mapped[str | None] = mapped_column(String, nullable=True)
    ai_observations: Mapped[str | None] = mapped_column(String, nullable=True)
    ai_patterns: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ai_suggested_experiment: Mapped[str | None] = mapped_column(String, nullable=True)
    ai_goal_observations: Mapped[str | None] = mapped_column(String, nullable=True)
    ai_emotion_analysis: Mapped[str | None] = mapped_column(String, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

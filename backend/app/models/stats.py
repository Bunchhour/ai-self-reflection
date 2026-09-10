import uuid
from datetime import datetime, date, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Date, Integer, Float, ForeignKey, DateTime
from app.database import Base

class UserStats(Base):
    __tablename__ = "user_stats"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_reflections: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    streak_shields: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    growth_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    achievements: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    last_reflection_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

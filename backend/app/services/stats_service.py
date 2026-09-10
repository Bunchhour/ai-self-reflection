from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.stats import UserStats
import uuid
from datetime import datetime, timezone, timedelta

async def update_streak(db: AsyncSession, user_id: uuid.UUID) -> None:
    result = await db.execute(select(UserStats).where(UserStats.user_id == user_id))
    stats = result.scalars().first()

    if not stats:
        # Auto-create UserStats record on first reflection
        stats = UserStats(user_id=user_id, current_streak=1, longest_streak=1, total_reflections=1,
                          last_reflection_date=datetime.now(timezone.utc).date())
        db.add(stats)
        await db.commit()
        return

    today = datetime.now(timezone.utc).date()
    if stats.last_reflection_date == today:
        return  # Already counted today

    if stats.last_reflection_date == today - timedelta(days=1):
        stats.current_streak += 1
    elif stats.last_reflection_date is None:
        stats.current_streak = 1
    else:
        # Streak broken — check if user has streak shields
        if stats.streak_shields and stats.streak_shields > 0:
            days_missed = (today - stats.last_reflection_date).days - 1
            if days_missed <= stats.streak_shields:
                stats.streak_shields -= days_missed
                stats.current_streak += 1
            else:
                stats.current_streak = 1
                stats.streak_shields = 0
        else:
            stats.current_streak = 1

    if stats.current_streak > stats.longest_streak:
        stats.longest_streak = stats.current_streak
    stats.total_reflections += 1
    stats.last_reflection_date = today

    # Award streak shield at milestone streaks
    if stats.current_streak in (7, 14, 30, 60, 90):
        stats.streak_shields = (stats.streak_shields or 0) + 1

    await db.commit()

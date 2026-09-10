from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.stats import UserStats
from app.schemas.stats import UserStatsResponse, AchievementResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/stats", tags=["Stats"])

@router.get("/achievements", response_model=list[AchievementResponse])
async def get_achievements(
    current_user: User = Depends(get_current_user),
):
    # Potential achievement catalog
    return [
        AchievementResponse(
            name="First Step",
            description="Completed first reflection",
            unlocked_at="2026-09-01T00:00:00Z",
        ),
        AchievementResponse(
            name="Consistency Champion",
            description="Maintained a 7-day reflection streak",
            unlocked_at=None,
        ),
        AchievementResponse(
            name="Explorer",
            description="Completed first micro-experiment",
            unlocked_at=None,
        ),
    ]

@router.get("/", response_model=UserStatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(UserStats).where(UserStats.user_id == current_user.id))
    stats = result.scalars().first()
    if not stats:
        # Create stats if missing
        stats = UserStats(user_id=current_user.id)
        db.add(stats)
        await db.commit()
        await db.refresh(stats)
    return stats

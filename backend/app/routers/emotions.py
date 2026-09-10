from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.emotion import EmotionLog
from app.services.auth_service import get_current_user
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/api/emotions", tags=["Emotions"])

@router.get("/trends")
async def get_emotion_trends(
    range: str = "7d",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        days = int(range.replace("d", ""))
    except ValueError:
        days = 7
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).date()

    result = await db.execute(
        select(EmotionLog)
        .where(EmotionLog.user_id == current_user.id, EmotionLog.date >= start_date)
        .order_by(EmotionLog.date.asc())
    )
    logs = result.scalars().all()
    return logs

@router.get("/heatmap")
async def get_heatmap(
    range: str = "30d",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return []

@router.get("/triggers")
async def get_triggers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return []

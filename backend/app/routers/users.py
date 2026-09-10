from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.feedback import InsightFeedback
from app.models.reflection import DailyReflection
from app.models.experiment import Experiment
from app.models.goal import Goal
from app.models.stats import UserStats
from app.services.auth_service import get_current_user
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/api/user", tags=["User"])

class FeedbackInput(BaseModel):
    reflection_id: uuid.UUID
    insight_type: str
    rating: int
    feedback: str | None = None

@router.get("/export")
async def export_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reflections = (
        await db.execute(
            select(DailyReflection).where(DailyReflection.user_id == current_user.id)
        )
    ).scalars().all()
    experiments = (
        await db.execute(
            select(Experiment).where(Experiment.user_id == current_user.id)
        )
    ).scalars().all()
    goals = (
        await db.execute(select(Goal).where(Goal.user_id == current_user.id))
    ).scalars().all()
    stats = (
        await db.execute(select(UserStats).where(UserStats.user_id == current_user.id))
    ).scalars().first()

    return {
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name,
            "created_at": current_user.created_at.isoformat(),
        },
        "stats": {
            "current_streak": stats.current_streak if stats else 0,
            "longest_streak": stats.longest_streak if stats else 0,
            "total_reflections": stats.total_reflections if stats else 0,
        },
        "reflections_count": len(reflections),
        "experiments_count": len(experiments),
        "goals_count": len(goals),
    }

@router.delete("/account")
async def delete_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await db.delete(current_user)
    await db.commit()
    return {"detail": "Account deleted"}

@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    data: FeedbackInput,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fb = InsightFeedback(
        user_id=current_user.id,
        reflection_id=data.reflection_id,
        insight_type=data.insight_type,
        rating=data.rating,
        feedback=data.feedback,
    )
    db.add(fb)
    await db.commit()
    return {"detail": "Feedback saved"}

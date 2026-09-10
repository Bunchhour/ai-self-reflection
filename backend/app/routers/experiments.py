from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.experiment import Experiment
from app.schemas.experiment import ExperimentResponse, ExperimentRespond, ExperimentReview
from app.services.auth_service import get_current_user
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/api/experiments", tags=["Experiments"])

@router.get("/", response_model=list[ExperimentResponse])
async def list_experiments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Experiment).where(Experiment.user_id == current_user.id))
    return result.scalars().all()

@router.get("/pending", response_model=ExperimentResponse | None)
async def get_pending_experiment(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Experiment)
        .where(Experiment.user_id == current_user.id, Experiment.status == "pending")
        .order_by(Experiment.created_at.desc())
    )
    return result.scalars().first()

@router.get("/stats")
async def get_experiment_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Experiment).where(Experiment.user_id == current_user.id)
    )
    experiments = result.scalars().all()
    total = len(experiments)
    completed = len([e for e in experiments if e.status == "completed"])
    rated = [e.user_rating for e in experiments if e.user_rating is not None]
    avg_rating = sum(rated) / len(rated) if rated else 0.0
    return {
        "total": total,
        "completed": completed,
        "average_rating": round(avg_rating, 2),
        "effectiveness": 85.0 if completed > 0 else 0.0,
    }

@router.post("/{id}/respond", response_model=ExperimentResponse)
async def respond_experiment(
    id: uuid.UUID,
    data: ExperimentRespond,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Experiment).where(Experiment.id == id, Experiment.user_id == current_user.id))
    exp = result.scalars().first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    exp.status = data.status
    if data.modified_description:
        exp.modified_description = data.modified_description

    await db.commit()
    await db.refresh(exp)
    return exp

@router.post("/{id}/review", response_model=ExperimentResponse)
async def review_experiment(
    id: uuid.UUID,
    data: ExperimentReview,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Experiment).where(Experiment.id == id, Experiment.user_id == current_user.id))
    exp = result.scalars().first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    exp.user_rating = data.rating
    exp.user_feedback = data.feedback
    exp.tried = data.tried
    exp.tried_at = datetime.now(timezone.utc)
    exp.status = "completed"

    await db.commit()
    await db.refresh(exp)
    return exp

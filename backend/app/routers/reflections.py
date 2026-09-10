from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.database import get_db, AsyncSessionLocal
from app.models.user import User
from app.models.reflection import DailyReflection
from app.schemas.reflection import ReflectionCreate, ReflectionResponse, FollowupSubmit
from app.services.auth_service import get_current_user
from app.services.stats_service import update_streak
from app.agents.reflection_agent import run_reflection_agent, ReflectionState
from app.agents.summary_agent import generate_period_summary
from datetime import timezone, datetime, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reflections", tags=["Reflections"])

async def process_reflection_background(
    user_id: uuid.UUID,
    reflection_id: uuid.UUID,
    entry_mode: str,
    answers: dict,
    mood_score: int | None,
    energy_level: int | None,
    reported_emotions: list | None,
    followup_answers: str | None = None,
):
    try:
        async with AsyncSessionLocal() as session:
            state = ReflectionState(
                user_id=user_id,
                reflection_id=reflection_id,
                entry_mode=entry_mode,
                answers=answers,
                followup_answers=followup_answers,
                mood_score=mood_score,
                energy_level=energy_level,
                reported_emotions=reported_emotions,
                db_session=session,
            )
            await run_reflection_agent(state)
    except Exception as e:
        logger.error(f"Background agent execution error: {e}")

@router.post("/", response_model=ReflectionResponse, status_code=status.HTTP_201_CREATED)
async def create_reflection(
    data: ReflectionCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.now(timezone.utc).date()
    # Check if already reflected today
    result = await db.execute(
        select(DailyReflection).where(
            DailyReflection.user_id == current_user.id,
            DailyReflection.date == today,
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Reflection already exists for today")

    needs_followup = True if data.entry_mode == "deep_dive" else False
    reported_emotions = [e.model_dump() for e in data.reported_emotions] if data.reported_emotions else None

    reflection = DailyReflection(
        user_id=current_user.id,
        date=today,
        entry_mode=data.entry_mode,
        answers=data.answers,
        mood_score=data.mood_score,
        energy_level=data.energy_level,
        reported_emotions=reported_emotions,
        needs_followup=needs_followup,
        is_processed=False,
    )
    db.add(reflection)
    await db.commit()
    await db.refresh(reflection)

    # Update streak and reflection counts
    await update_streak(db, current_user.id)

    # Trigger agent in background
    background_tasks.add_task(
        process_reflection_background,
        user_id=current_user.id,
        reflection_id=reflection.id,
        entry_mode=reflection.entry_mode,
        answers=reflection.answers,
        mood_score=reflection.mood_score,
        energy_level=reflection.energy_level,
        reported_emotions=reflection.reported_emotions,
    )

    return reflection

@router.get("/", response_model=list[ReflectionResponse])
async def list_reflections(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(DailyReflection)
        .where(DailyReflection.user_id == current_user.id)
        .order_by(desc(DailyReflection.date))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.get("/today", response_model=ReflectionResponse)
async def get_today(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.now(timezone.utc).date()
    result = await db.execute(
        select(DailyReflection).where(
            DailyReflection.user_id == current_user.id,
            DailyReflection.date == today,
        )
    )
    reflection = result.scalars().first()
    if not reflection:
        raise HTTPException(status_code=404, detail="No reflection found for today")
    return reflection

@router.delete("/today")
async def delete_today(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.now(timezone.utc).date()
    result = await db.execute(
        select(DailyReflection).where(
            DailyReflection.user_id == current_user.id,
            DailyReflection.date == today,
        )
    )
    reflection = result.scalars().first()
    if not reflection:
        raise HTTPException(status_code=404, detail="No reflection found for today")
    await db.delete(reflection)
    await db.commit()
    return {"detail": "Deleted today's reflection"}

@router.get("/weekly")
async def get_weekly_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = datetime.now(timezone.utc).date() - timedelta(days=7)
    result = await db.execute(
        select(DailyReflection)
        .where(DailyReflection.user_id == current_user.id, DailyReflection.date >= since)
        .order_by(DailyReflection.date.asc())
    )
    reflections = result.scalars().all()
    reflection_dicts = [
        {"date": str(r.date), "mode": r.entry_mode, "answers": r.answers, "summary": r.ai_summary}
        for r in reflections
    ]
    summary_text = await generate_period_summary(reflection_dicts, "weekly")
    return {"period": "weekly", "count": len(reflections), "summary": summary_text}

@router.get("/monthly")
async def get_monthly_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = datetime.now(timezone.utc).date() - timedelta(days=30)
    result = await db.execute(
        select(DailyReflection)
        .where(DailyReflection.user_id == current_user.id, DailyReflection.date >= since)
        .order_by(DailyReflection.date.asc())
    )
    reflections = result.scalars().all()
    reflection_dicts = [
        {"date": str(r.date), "mode": r.entry_mode, "answers": r.answers, "summary": r.ai_summary}
        for r in reflections
    ]
    summary_text = await generate_period_summary(reflection_dicts, "monthly")
    return {"period": "monthly", "count": len(reflections), "summary": summary_text}

@router.get("/{id}", response_model=ReflectionResponse)
async def get_reflection(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(DailyReflection).where(
            DailyReflection.id == id,
            DailyReflection.user_id == current_user.id,
        )
    )
    reflection = result.scalars().first()
    if not reflection:
        raise HTTPException(status_code=404, detail="Reflection not found")
    return reflection

@router.delete("/{id}")
async def delete_reflection(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(DailyReflection).where(
            DailyReflection.id == id,
            DailyReflection.user_id == current_user.id,
        )
    )
    reflection = result.scalars().first()
    if not reflection:
        raise HTTPException(status_code=404, detail="Reflection not found")
    await db.delete(reflection)
    await db.commit()
    return {"detail": "Deleted"}

@router.post("/{id}/followup", response_model=ReflectionResponse)
async def submit_followup(
    id: uuid.UUID,
    data: FollowupSubmit,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(DailyReflection).where(
            DailyReflection.id == id,
            DailyReflection.user_id == current_user.id,
        )
    )
    reflection = result.scalars().first()
    if not reflection:
        raise HTTPException(status_code=404, detail="Reflection not found")

    reflection.followup_answers = data.followup_answers
    reflection.needs_followup = False
    await db.commit()
    await db.refresh(reflection)

    # Resume agent pipeline in background
    background_tasks.add_task(
        process_reflection_background,
        user_id=current_user.id,
        reflection_id=reflection.id,
        entry_mode=reflection.entry_mode,
        answers=reflection.answers,
        mood_score=reflection.mood_score,
        energy_level=reflection.energy_level,
        reported_emotions=reflection.reported_emotions,
        followup_answers=data.followup_answers,
    )

    return reflection

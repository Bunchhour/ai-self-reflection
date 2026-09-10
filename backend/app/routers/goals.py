from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.goal import Goal, InterestSignal
from app.schemas.goal import (
    GoalCreate,
    GoalUpdate,
    GoalResponse,
    InterestSignalResponse,
    InterestRespond,
)
from app.services.auth_service import get_current_user
import uuid

router = APIRouter(prefix="/api/goals", tags=["Goals"])

@router.get("/", response_model=list[GoalResponse])
async def list_goals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Goal).where(Goal.user_id == current_user.id))
    return result.scalars().all()

@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    data: GoalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = Goal(
        user_id=current_user.id,
        title=data.title,
        description=data.description,
        interest_signal_id=data.interest_signal_id,
        milestones=[],
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return goal

@router.get("/interests", response_model=list[InterestSignalResponse])
async def get_interests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(InterestSignal).where(
            InterestSignal.user_id == current_user.id,
            InterestSignal.surfaced == True,
        )
    )
    return result.scalars().all()

@router.post("/interests/{id}/respond")
async def respond_interest(
    id: uuid.UUID,
    data: InterestRespond,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(InterestSignal).where(
            InterestSignal.id == id,
            InterestSignal.user_id == current_user.id,
        )
    )
    signal = result.scalars().first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    signal.user_response = data.response
    await db.commit()
    return {"detail": "Responded"}

@router.patch("/{id}", response_model=GoalResponse)
async def update_goal(
    id: uuid.UUID,
    data: GoalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Goal).where(Goal.id == id, Goal.user_id == current_user.id)
    )
    goal = result.scalars().first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    if data.status is not None:
        goal.status = data.status
    if data.description is not None:
        goal.description = data.description
    if data.milestones is not None:
        goal.milestones = data.milestones

    await db.commit()
    await db.refresh(goal)
    return goal

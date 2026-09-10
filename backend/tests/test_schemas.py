import uuid
from datetime import datetime, timezone, date
import pytest
from pydantic import ValidationError

from app.schemas.auth import UserCreate, UserLogin, UserResponse, Token
from app.schemas.reflection import (
    EmotionInput,
    QuickPulseAnswers,
    GuidedAnswers,
    ReflectionCreate,
    FollowupSubmit,
    ReflectionResponse,
)
from app.schemas.experiment import (
    ExperimentRespond,
    ExperimentReview,
    ExperimentResponse,
)
from app.schemas.goal import GoalCreate, GoalUpdate, GoalResponse
from app.schemas.stats import UserStatsResponse

def test_user_create_validation():
    # Valid
    user = UserCreate(name="Alice", email="alice@example.com", password="secretpassword")
    assert user.name == "Alice"
    assert user.email == "alice@example.com"

    # Invalid email
    with pytest.raises(ValidationError):
        UserCreate(name="Bob", email="not-an-email", password="secretpassword")

def test_reflection_create_validation():
    ref = ReflectionCreate(
        entry_mode="quick_pulse",
        answers={"mood_score": 85, "energy_level": 4, "one_thought": "Productive day"},
        mood_score=85,
        energy_level=4,
        reported_emotions=[EmotionInput(emotion="energized", intensity=3)],
    )
    assert ref.entry_mode == "quick_pulse"
    assert ref.mood_score == 85
    assert len(ref.reported_emotions) == 1
    assert ref.reported_emotions[0].emotion == "energized"

def test_experiment_schemas():
    respond = ExperimentRespond(status="accepted", modified_description="Modified test")
    assert respond.status == "accepted"
    assert respond.modified_description == "Modified test"

    review = ExperimentReview(rating=5, feedback="Worked great!", tried=True)
    assert review.rating == 5
    assert review.tried is True

def test_goal_schemas():
    goal = GoalCreate(title="Meditate 10 mins daily", description="Improve mindfulness")
    assert goal.title == "Meditate 10 mins daily"

    update = GoalUpdate(status="achieved")
    assert update.status == "achieved"

def test_user_stats_schema():
    stats = UserStatsResponse(
        current_streak=5,
        longest_streak=10,
        total_reflections=15,
        streak_shields=1,
        growth_score=88.5,
        achievements=[{"name": "First Step"}],
        last_reflection_date=date(2026, 9, 6),
    )
    assert stats.current_streak == 5
    assert stats.growth_score == 88.5

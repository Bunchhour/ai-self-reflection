import uuid
from datetime import datetime, timezone, date
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.database import get_db
from app.models.user import User
from app.models.reflection import DailyReflection
from app.models.experiment import Experiment
from app.models.goal import Goal
from app.models.stats import UserStats
from app.services.auth_service import get_current_user, get_password_hash

# Fixed test user
TEST_USER_ID = uuid.uuid4()
test_user = User(
    id=TEST_USER_ID,
    email="tester@example.com",
    name="Test User",
    hashed_password=get_password_hash("password123"),
    created_at=datetime.now(timezone.utc),
)

async def override_get_current_user():
    return test_user

class MockScalars:
    def __init__(self, items):
        self._items = items

    def first(self):
        return self._items[0] if self._items else None

    def all(self):
        return self._items

class MockExecuteResult:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return MockScalars(self._items)

@pytest.fixture
def client_with_auth():
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

def test_auth_me(client_with_auth):
    response = client_with_auth.get("/api/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "tester@example.com"
    assert data["name"] == "Test User"
    assert data["id"] == str(TEST_USER_ID)

def test_stats_endpoint(client_with_auth):
    mock_db = AsyncMock()
    mock_stats = UserStats(
        id=uuid.uuid4(),
        user_id=TEST_USER_ID,
        current_streak=3,
        longest_streak=7,
        total_reflections=12,
        streak_shields=1,
        growth_score=85.0,
        achievements=[],
        last_reflection_date=date.today(),
        updated_at=datetime.now(timezone.utc),
    )
    mock_db.execute.return_value = MockExecuteResult([mock_stats])
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client_with_auth.get("/api/stats/")
    assert response.status_code == 200
    data = response.json()
    assert data["current_streak"] == 3
    assert data["growth_score"] == 85.0

def test_achievements_endpoint(client_with_auth):
    response = client_with_auth.get("/api/stats/achievements")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "First Step"

def test_create_goal(client_with_auth):
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    async def mock_refresh(instance):
        instance.id = uuid.uuid4()
        instance.status = "active"
        instance.created_at = datetime.now(timezone.utc)
        instance.updated_at = datetime.now(timezone.utc)

    mock_db.refresh = AsyncMock(side_effect=mock_refresh)
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client_with_auth.post(
        "/api/goals/",
        json={"title": "Read 10 pages", "description": "Daily reading habit"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Read 10 pages"
    assert data["status"] == "active"

def test_experiments_list(client_with_auth):
    mock_db = AsyncMock()
    mock_exp = Experiment(
        id=uuid.uuid4(),
        user_id=TEST_USER_ID,
        description="Try 5-minute breathing before work",
        status="pending",
        created_at=datetime.now(timezone.utc),
    )
    mock_db.execute.return_value = MockExecuteResult([mock_exp])
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client_with_auth.get("/api/experiments/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["description"] == "Try 5-minute breathing before work"

def test_feedback_submit(client_with_auth):
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client_with_auth.post(
        "/api/user/feedback",
        json={
            "reflection_id": str(uuid.uuid4()),
            "insight_type": "pattern",
            "rating": 5,
            "feedback": "Very accurate pattern detection",
        },
    )
    assert response.status_code == 201
    assert response.json() == {"detail": "Feedback saved"}

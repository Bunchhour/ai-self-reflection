import uuid
from datetime import datetime, timezone, date
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.database import get_db
from app.models.user import User
from app.models.reflection import DailyReflection
from app.services.auth_service import get_current_user

TEST_USER_ID = uuid.uuid4()
test_user = User(
    id=TEST_USER_ID,
    email="tester@example.com",
    name="Test User",
    hashed_password="fakehashedpassword",
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
def client():
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_create_reflection(client):
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    # First execute is check for today's reflection -> return empty
    # Next is update_streak select stats -> return empty
    mock_db.execute.return_value = MockExecuteResult([])

    async def mock_refresh(instance):
        instance.id = uuid.uuid4()
        instance.created_at = datetime.now(timezone.utc)
        instance.updated_at = datetime.now(timezone.utc)

    mock_db.refresh = AsyncMock(side_effect=mock_refresh)
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("app.routers.reflections.process_reflection_background", new=AsyncMock()):
        response = client.post(
            "/api/reflections/",
            json={
                "entry_mode": "quick_pulse",
                "answers": {"one_thought": "Feeling good", "win_of_day": "Shipped code"},
                "mood_score": 90,
                "energy_level": 5,
                "reported_emotions": [{"emotion": "inspired", "intensity": 3}],
            },
        )
    assert response.status_code == 201
    data = response.json()
    assert data["entry_mode"] == "quick_pulse"
    assert data["mood_score"] == 90
    assert data["needs_followup"] is False

def test_create_reflection_duplicate_rejected(client):
    today = datetime.now(timezone.utc).date()
    existing = DailyReflection(
        id=uuid.uuid4(),
        user_id=TEST_USER_ID,
        date=today,
        entry_mode="quick_pulse",
        answers={},
    )
    mock_db = AsyncMock()
    mock_db.execute.return_value = MockExecuteResult([existing])
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/api/reflections/",
        json={
            "entry_mode": "quick_pulse",
            "answers": {"one_thought": "Another entry"},
        },
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_get_today_reflection(client):
    today = datetime.now(timezone.utc).date()
    existing = DailyReflection(
        id=uuid.uuid4(),
        user_id=TEST_USER_ID,
        date=today,
        entry_mode="guided",
        answers={"reflection": "Great session"},
        needs_followup=False,
        is_processed=True,
        created_at=datetime.now(timezone.utc),
    )
    mock_db = AsyncMock()
    mock_db.execute.return_value = MockExecuteResult([existing])
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/api/reflections/today")
    assert response.status_code == 200
    data = response.json()
    assert data["entry_mode"] == "guided"
    assert data["id"] == str(existing.id)

def test_delete_today_reflection(client):
    today = datetime.now(timezone.utc).date()
    existing = DailyReflection(
        id=uuid.uuid4(),
        user_id=TEST_USER_ID,
        date=today,
        entry_mode="guided",
        answers={},
    )
    mock_db = AsyncMock()
    mock_db.execute.return_value = MockExecuteResult([existing])
    mock_db.delete = AsyncMock()
    mock_db.commit = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.delete("/api/reflections/today")
    assert response.status_code == 200
    assert response.json() == {"detail": "Deleted today's reflection"}

def test_submit_followup(client):
    ref_id = uuid.uuid4()
    existing = DailyReflection(
        id=ref_id,
        user_id=TEST_USER_ID,
        date=datetime.now(timezone.utc).date(),
        entry_mode="deep_dive",
        answers={},
        needs_followup=True,
        is_processed=False,
        created_at=datetime.now(timezone.utc),
    )
    mock_db = AsyncMock()
    mock_db.execute.return_value = MockExecuteResult([existing])
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("app.routers.reflections.process_reflection_background", new=AsyncMock()):
        response = client.post(
            f"/api/reflections/{ref_id}/followup",
            json={"followup_answers": "I realized that setting boundaries helps."},
        )
    assert response.status_code == 200
    assert existing.followup_answers == "I realized that setting boundaries helps."

def test_get_weekly_and_monthly_summaries(client):
    mock_db = AsyncMock()
    mock_db.execute.return_value = MockExecuteResult([])
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("app.routers.reflections.generate_period_summary", new=AsyncMock(return_value="Weekly overview")):
        res_weekly = client.get("/api/reflections/weekly")
        assert res_weekly.status_code == 200
        assert res_weekly.json()["period"] == "weekly"

    with patch("app.routers.reflections.generate_period_summary", new=AsyncMock(return_value="Monthly overview")):
        res_monthly = client.get("/api/reflections/monthly")
        assert res_monthly.status_code == 200
        assert res_monthly.json()["period"] == "monthly"

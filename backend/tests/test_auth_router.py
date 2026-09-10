import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.database import get_db
from app.models.user import User
from app.services.auth_service import get_password_hash

client = TestClient(app)

class MockScalars:
    def __init__(self, items):
        self._items = items

    def first(self):
        return self._items[0] if self._items else None

class MockExecuteResult:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return MockScalars(self._items)

def test_register_success():
    mock_db = AsyncMock()
    mock_db.execute.return_value = MockExecuteResult([])  # email not found
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    async def mock_refresh(user):
        user.id = uuid.uuid4()
        user.created_at = datetime.now(timezone.utc)

    mock_db.refresh = AsyncMock(side_effect=mock_refresh)
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/api/auth/register",
        json={"name": "New User", "email": "newuser@example.com", "password": "securepassword123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    app.dependency_overrides.clear()

def test_register_duplicate_email():
    existing_user = User(
        id=uuid.uuid4(),
        email="existing@example.com",
        name="Existing",
        hashed_password=get_password_hash("pass"),
        created_at=datetime.now(timezone.utc),
    )
    mock_db = AsyncMock()
    mock_db.execute.return_value = MockExecuteResult([existing_user])
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/api/auth/register",
        json={"name": "Duplicate", "email": "existing@example.com", "password": "securepassword123"},
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]
    app.dependency_overrides.clear()

def test_login_success():
    raw_pass = "correctpassword"
    user = User(
        id=uuid.uuid4(),
        email="login@example.com",
        name="Login User",
        hashed_password=get_password_hash(raw_pass),
        created_at=datetime.now(timezone.utc),
    )
    mock_db = AsyncMock()
    mock_db.execute.return_value = MockExecuteResult([user])
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": raw_pass},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    app.dependency_overrides.clear()

def test_login_invalid_credentials():
    user = User(
        id=uuid.uuid4(),
        email="login@example.com",
        name="Login User",
        hashed_password=get_password_hash("realpass"),
        created_at=datetime.now(timezone.utc),
    )
    mock_db = AsyncMock()
    mock_db.execute.return_value = MockExecuteResult([user])
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]
    app.dependency_overrides.clear()

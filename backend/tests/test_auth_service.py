from jose import jwt
from app.config import settings
from app.services.auth_service import (
    get_password_hash,
    verify_password,
    create_access_token,
)

def test_password_hashing():
    raw_password = "SecurePassword123!"
    hashed = get_password_hash(raw_password)
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_create_access_token():
    user_id = "12345678-1234-5678-1234-567812345678"
    token = create_access_token(data={"sub": user_id})
    assert isinstance(token, str)
    assert len(token) > 20

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload.get("sub") == user_id
    assert "exp" in payload

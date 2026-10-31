import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.utils.security import hash_password, verify_password, create_access_token, decode_token


def test_password_hashing():
    password = "TestPass123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpass", hashed) is False


def test_jwt_token_creation_and_decode():
    token = create_access_token(subject="123", role="user")
    assert isinstance(token, str)
    assert len(token) > 0
    decoded = decode_token(token, expected_type="access")
    assert decoded.user_id == 123
    assert decoded.role == "user"
    assert decoded.token_type == "access"

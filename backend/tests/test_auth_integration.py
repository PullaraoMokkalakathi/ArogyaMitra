import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def test_register_login_and_protected_me(client):
    # Register
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "StrongPass123!",
            "confirm_password": "StrongPass123!",
            "full_name": "New User",
        },
    )
    assert reg.status_code == 201, reg.text
    data = reg.json()
    assert data.get("success") is True
    tokens = data.get("tokens") or {}
    access = tokens.get("access_token")
    assert access

    # Access protected /me
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 200, me.text
    me_data = me.json()
    assert me_data.get("email") == "newuser@example.com"

    # Login
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "newuser@example.com", "password": "StrongPass123!"},
    )
    assert login.status_code == 200, login.text
    login_data = login.json()
    assert login_data.get("success") is True
    assert login_data.get("tokens", {}).get("access_token")

def test_register_and_login_flow(client):
    # Register
    payload = {
        "email": "testuser@example.com",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!",
        "full_name": "Test User"
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data.get("success") is True
    assert "tokens" in data
    assert "access_token" in data["tokens"]

    # Login
    login_payload = {"email": "testuser@example.com", "password": "TestPass123!"}
    resp2 = client.post("/api/v1/auth/login", json=login_payload)
    assert resp2.status_code == 200
    login_data = resp2.json()
    assert login_data.get("success") is True
    assert "tokens" in login_data

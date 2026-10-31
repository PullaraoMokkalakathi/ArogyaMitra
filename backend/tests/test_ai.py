def test_ai_endpoints(client):
    resp = client.post("/api/v1/ai/chat", json={})
    # Current implementation has no auth, different schema - validation error
    assert resp.status_code in [422, 400]

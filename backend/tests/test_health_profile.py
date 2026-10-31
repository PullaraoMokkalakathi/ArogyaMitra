def test_health_profile_endpoints(client):
    # Without auth - should be unauthorized
    resp = client.get("/api/v1/health/profile")
    assert resp.status_code == 401

    resp2 = client.post("/api/v1/health/profile", json={})
    assert resp2.status_code == 401

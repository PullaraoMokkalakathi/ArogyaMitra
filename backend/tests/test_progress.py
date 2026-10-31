def test_progress_endpoints(client):
    resp = client.get("/api/v1/progress/stats")
    assert resp.status_code in [401, 404]  # Requires auth
    resp2 = client.post("/api/v1/progress/log", json={})
    assert resp2.status_code in [401, 422]  # Requires auth or validation

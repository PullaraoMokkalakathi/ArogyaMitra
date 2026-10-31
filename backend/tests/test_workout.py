def test_workout_endpoints(client):
    resp = client.get("/api/v1/workout/plan")
    assert resp.status_code == 401  # Requires auth

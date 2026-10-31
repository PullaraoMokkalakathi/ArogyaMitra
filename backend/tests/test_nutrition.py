def test_nutrition_endpoints(client):
    resp = client.get("/api/v1/nutrition/plan")
    assert resp.status_code in [401, 404]  # Requires auth or not found if no profile

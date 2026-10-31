def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "healthy"
    assert "app" in data
    assert "services" in data
    assert data["services"]["database"] == "connected"

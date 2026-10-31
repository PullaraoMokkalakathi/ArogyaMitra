def test_posture_endpoints(client):
    resp = client.post("/api/v1/posture/analyze", json={})
    assert resp.status_code == 422  # Validation error per schema

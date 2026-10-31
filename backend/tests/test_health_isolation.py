import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def test_health_uses_test_database(client):
    response = client.get("/health")
    # With isolated test DB properly configured, health should check it
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "services" in data
    assert data["services"]["database"] in ["connected", "unreachable"]


def test_health_db_connected_in_test(client):
    response = client.get("/health")
    # In our test setup with proper DB override, should be connected
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "healthy"
    assert data["services"]["database"] == "connected"

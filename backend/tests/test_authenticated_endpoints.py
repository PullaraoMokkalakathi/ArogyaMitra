import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def test_ai_chat_validation(client):
    # AI chat exists but schema differs; test without auth - depends on implementation
    resp = client.post("/api/v1/ai/chat", json={})
    # Accept 422 (validation) or 401 (auth) depending on router
    assert resp.status_code in [401, 422]


def test_nutrition_plan_requires_auth(client):
    resp = client.get("/api/v1/nutrition/plan")
    assert resp.status_code == 401


def test_progress_stats_requires_auth(client):
    resp = client.get("/api/v1/progress/stats")
    assert resp.status_code == 401


def test_progress_log_requires_auth(client):
    resp = client.post("/api/v1/progress/log", json={})
    assert resp.status_code == 401


def test_posture_analyze_validation(client):
    resp = client.post("/api/v1/posture/analyze", json={})
    # No auth required per current impl, expects validation error
    assert resp.status_code == 422

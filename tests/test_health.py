from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_analyze_request_validation() -> None:
    client = TestClient(app)
    # Question too short -> 422
    res = client.post("/v1/analyze", json={"question": "hi"})
    assert res.status_code == 422

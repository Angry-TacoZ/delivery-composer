from app.config import Settings
from app.demo_data import DEMO_BRIEF
from app.main import create_app
from fastapi.testclient import TestClient


def test_health_does_not_expose_configuration() -> None:
    app = create_app(Settings(demo_mode=True))
    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database_configured": False,
        "gemini_configured": False,
        "demo_mode": True,
    }


def test_compose_returns_evidence_and_human_review_boundary() -> None:
    app = create_app(Settings(demo_mode=True))
    with TestClient(app) as client:
        response = client.post("/api/compose", json={"raw_brief": DEMO_BRIEF})

    assert response.status_code == 200
    payload = response.json()
    assert payload["retrieval_mode"] == "deterministic_demo"
    assert len(payload["assignments"]) == 3
    assert all(assignment["hard_constraints"] for assignment in payload["assignments"])
    assert all(assignment["explanation"] for assignment in payload["assignments"])


def test_rejects_too_short_briefs() -> None:
    app = create_app(Settings(demo_mode=True))
    with TestClient(app) as client:
        response = client.post("/api/compose", json={"raw_brief": "Too short"})

    assert response.status_code == 422

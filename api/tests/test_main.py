from uuid import UUID

from app.config import Settings
from app.demo_data import DEMO_BRIEF
from app.domain import BriefInput, ReviewInput
from app.main import create_app
from app.service import ComposerService
from fastapi.testclient import TestClient
from pydantic import SecretStr


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


def test_demo_review_returns_session_provenance() -> None:
    app = create_app(Settings(demo_mode=True))
    with TestClient(app) as client:
        composition = client.post("/api/compose", json={"raw_brief": DEMO_BRIEF}).json()
        response = client.post(
            f"/api/runs/{composition['run_id']}/review",
            json={
                "status": "needs_changes",
                "notes": "Add an operations lead with transport-sector evidence.",
            },
        )

    assert response.status_code == 200
    assert response.json()["status"] == "needs_changes"
    assert response.json()["persistence_mode"] == "session"


def test_demo_review_is_stored_for_the_api_session() -> None:
    service = ComposerService(Settings(demo_mode=True))
    composition = service.compose(BriefInput(raw_brief=DEMO_BRIEF))
    review = ReviewInput(
        status="needs_changes",
        notes="Add an operations lead with transport-sector evidence.",
    )

    persistence_mode = service.record_review(composition.run_id, review)

    assert persistence_mode == "session"
    assert service.demo_repository.reviews[composition.run_id] == review


def test_live_review_returns_postgres_provenance() -> None:
    service = ComposerService(
        Settings(
            database_url="postgresql://unused.example/test",
            gemini_api_key=SecretStr("configured-for-test"),
        )
    )
    recorded: list[tuple[UUID, ReviewInput]] = []

    class RecordingRepository:
        def record_review(self, run_id: UUID, review: ReviewInput) -> None:
            recorded.append((run_id, review))

    service.postgres_repository = RecordingRepository()
    review = ReviewInput(status="approved", notes="Evidence reviewed.")
    run_id = UUID("00000000-0000-0000-0000-000000000001")

    persistence_mode = service.record_review(run_id, review)

    assert persistence_mode == "postgres"
    assert recorded == [(run_id, review)]


def test_review_rejects_unknown_demo_run() -> None:
    app = create_app(Settings(demo_mode=True))
    with TestClient(app) as client:
        response = client.post(
            "/api/runs/00000000-0000-0000-0000-000000000000/review",
            json={"status": "approved", "notes": ""},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Composition run not found in the current session."


def test_review_rejects_notes_over_600_characters() -> None:
    app = create_app(Settings(demo_mode=True))
    with TestClient(app) as client:
        response = client.post(
            "/api/runs/00000000-0000-0000-0000-000000000000/review",
            json={"status": "approved", "notes": "x" * 601},
        )

    assert response.status_code == 422


def test_rejects_too_short_briefs() -> None:
    app = create_app(Settings(demo_mode=True))
    with TestClient(app) as client:
        response = client.post("/api/compose", json={"raw_brief": "Too short"})

    assert response.status_code == 422

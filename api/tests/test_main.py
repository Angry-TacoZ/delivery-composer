from io import BytesIO
from uuid import UUID

import pytest
from app.config import Settings
from app.demo_data import DEMO_BRIEF
from app.domain import BriefInput, ReviewInput
from app.main import create_app
from app.mock_briefs import MOCK_BRIEFS
from app.pdf_briefs import MAX_PDF_BYTES
from app.service import ComposerService
from fastapi.testclient import TestClient
from pydantic import SecretStr
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas


def _pdf_bytes(text: str = "", pages: int = 1) -> bytes:
    buffer = BytesIO()
    document = canvas.Canvas(buffer)
    for page_index in range(pages):
        if text:
            document.drawString(48, 760, text if page_index == 0 else f"Supporting page {page_index + 1}.")
        document.showPage()
    document.save()
    return buffer.getvalue()


def _encrypted_pdf_bytes(text: str) -> bytes:
    reader = PdfReader(BytesIO(_pdf_bytes(text)))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt("demonstration-password")
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def test_health_does_not_expose_configuration() -> None:
    app = create_app(Settings(demo_mode=True))
    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "execution_mode": "deterministic_demo",
        "database_configured": False,
        "gemini_configured": False,
        "live_path_configured": False,
        "demo_mode": True,
    }


def test_demo_brief_library_exposes_three_bounded_synthetic_cases() -> None:
    app = create_app(Settings(demo_mode=True))
    with TestClient(app) as client:
        response = client.get("/api/demo-briefs")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 3
    assert {brief["reference"] for brief in payload} == {
        "SYN-CNI-001",
        "SYN-FSI-002",
        "SYN-MED-003",
    }
    assert all(40 <= len(brief["brief"]) <= 1600 for brief in payload)
    assert all(set(brief) == {"slug", "reference", "title", "sector", "brief"} for brief in payload)


def test_demo_mode_does_not_initialize_configured_live_adapters() -> None:
    service = ComposerService(
        Settings(
            demo_mode=True,
            database_url="postgresql://configured-but-unused.example/test",
            gemini_api_key=SecretStr("configured-but-unused"),
        )
    )

    composition = service.compose(BriefInput(raw_brief=DEMO_BRIEF))

    assert service.postgres_repository is None
    assert service.provider.client is None
    assert service.uses_live_path is False
    assert composition.retrieval_mode == "deterministic_demo"
    assert composition.requirements.extraction_source == "deterministic_demo"


@pytest.mark.parametrize(
    ("database_url", "gemini_api_key"),
    [
        (None, None),
        ("postgresql://configured.example/test", None),
        (None, SecretStr("configured")),
    ],
)
def test_live_mode_requires_both_backend_services(database_url, gemini_api_key) -> None:
    with pytest.raises(RuntimeError, match="requires both DATABASE_URL and GEMINI_API_KEY"):
        ComposerService(
            Settings(
                demo_mode=False,
                database_url=database_url,
                gemini_api_key=gemini_api_key,
            )
        )


def test_extract_pdf_populates_bounded_brief_text() -> None:
    app = create_app(Settings(demo_mode=True))
    expected = MOCK_BRIEFS[0]["brief"]
    with TestClient(app) as client:
        response = client.post(
            "/api/extract-brief",
            files={"file": ("client-brief.pdf", _pdf_bytes(expected), "application/pdf")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["file_name"] == "client-brief.pdf"
    assert payload["page_count"] == 1
    assert payload["text"] == expected
    assert payload["character_count"] == len(expected)


def test_extract_pdf_rejects_untrusted_file_boundaries() -> None:
    app = create_app(Settings(demo_mode=True))
    valid_pdf = _pdf_bytes(MOCK_BRIEFS[0]["brief"])
    cases = [
        (("brief.pdf", valid_pdf, "text/plain"), 415, "application/pdf"),
        (("brief.txt", valid_pdf, "application/pdf"), 415, ".pdf filename"),
        (("brief.pdf", b"not a pdf", "application/pdf"), 422, "PDF signature"),
        (("brief.pdf", b"%PDF-1.7\nbroken", "application/pdf"), 422, "valid document"),
        (
            ("brief.pdf", b"%PDF-" + (b"x" * MAX_PDF_BYTES), "application/pdf"),
            413,
            "2 MiB",
        ),
        (
            ("brief.pdf", _encrypted_pdf_bytes(MOCK_BRIEFS[0]["brief"]), "application/pdf"),
            422,
            "Encrypted PDFs",
        ),
        (("brief.pdf", _pdf_bytes(pages=1), "application/pdf"), 422, "searchable text"),
        (("brief.pdf", _pdf_bytes("Short"), "application/pdf"), 422, "at least 40"),
        (("brief.pdf", _pdf_bytes("A valid page", pages=6), "application/pdf"), 422, "five-page"),
        (("brief.pdf", _pdf_bytes("x" * 1601), "application/pdf"), 422, "1,600-character"),
    ]

    with TestClient(app) as client:
        for file_payload, expected_status, expected_detail in cases:
            response = client.post("/api/extract-brief", files={"file": file_payload})
            assert response.status_code == expected_status
            assert expected_detail in response.json()["detail"]


def test_mock_briefs_produce_distinct_requirements_and_teams() -> None:
    app = create_app(Settings(demo_mode=True, rate_limit_requests=10))
    with TestClient(app) as client:
        compositions = [
            client.post("/api/compose", json={"raw_brief": mock_brief["brief"]}).json()
            for mock_brief in MOCK_BRIEFS
        ]

    titles = {composition["requirements"]["title"] for composition in compositions}
    teams = {
        tuple(assignment["consultant"]["name"] for assignment in composition["assignments"])
        for composition in compositions
    }
    assert len(titles) == len(MOCK_BRIEFS)
    assert len(teams) == len(MOCK_BRIEFS)
    assert all(
        composition["requirements"]["target_start"]
        for composition in compositions
    )
    media_requirements = next(
        composition["requirements"]
        for composition in compositions
        if composition["requirements"]["title"] == "Media and broadcast platform recovery team"
    )
    assert "ai engineering" not in media_requirements["required_skills"]


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
            demo_mode=False,
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

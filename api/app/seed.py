"""Seed synthetic profiles and generate their server-side Gemini embeddings."""

from psycopg import connect

from app.config import get_settings
from app.demo_data import CONSULTANTS
from app.providers import AnalysisProvider
from app.repository import CLEARANCE_RANK

UPSERT_SQL = """
INSERT INTO consultants (
    id, name, role, seniority, location, availability_date, clearance, clearance_rank,
    skills, sectors, profile_text, evidence, considerations, embedding
) VALUES (
    %(id)s, %(name)s, %(role)s, %(seniority)s, %(location)s, %(availability_date)s,
    %(clearance)s, %(clearance_rank)s, %(skills)s, %(sectors)s, %(profile_text)s,
    %(evidence)s, %(considerations)s, %(embedding)s::vector
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    role = EXCLUDED.role,
    seniority = EXCLUDED.seniority,
    location = EXCLUDED.location,
    availability_date = EXCLUDED.availability_date,
    clearance = EXCLUDED.clearance,
    clearance_rank = EXCLUDED.clearance_rank,
    skills = EXCLUDED.skills,
    sectors = EXCLUDED.sectors,
    profile_text = EXCLUDED.profile_text,
    evidence = EXCLUDED.evidence,
    considerations = EXCLUDED.considerations,
    embedding = EXCLUDED.embedding,
    updated_at = now();
"""


def main() -> None:
    settings = get_settings()
    if not settings.database_url:
        raise SystemExit("DATABASE_URL is required. Set it in an uncommitted .env file first.")
    if not settings.has_gemini:
        raise SystemExit("GEMINI_API_KEY is required to seed real semantic embeddings.")

    provider = AnalysisProvider(settings)
    with connect(settings.database_url) as connection, connection.cursor() as cursor:
        for consultant in CONSULTANTS:
            embedding = provider.embed_document(consultant.profile_text)
            vector = "[" + ",".join(f"{value:.8f}" for value in embedding) + "]"
            cursor.execute(
                UPSERT_SQL,
                {
                    **consultant.model_dump(),
                    "clearance_rank": CLEARANCE_RANK[consultant.clearance],
                    "embedding": vector,
                },
            )
        connection.commit()
    print(f"Seeded {len(CONSULTANTS)} synthetic consultant profiles with {settings.embedding_dimensions}-D embeddings.")


if __name__ == "__main__":
    main()

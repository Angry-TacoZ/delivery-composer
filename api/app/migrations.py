"""Idempotent bootstrap migration for the demonstration database."""

from psycopg import connect

from app.config import get_settings

SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS consultants (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    seniority TEXT NOT NULL,
    location TEXT NOT NULL,
    availability_date DATE NOT NULL,
    clearance TEXT NOT NULL CHECK (clearance IN ('baseline', 'sc', 'dv')),
    clearance_rank SMALLINT NOT NULL CHECK (clearance_rank BETWEEN 1 AND 3),
    skills TEXT[] NOT NULL DEFAULT '{}',
    sectors TEXT[] NOT NULL DEFAULT '{}',
    profile_text TEXT NOT NULL,
    evidence TEXT[] NOT NULL DEFAULT '{}',
    embedding vector(768) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS consultants_clearance_availability_idx
    ON consultants (clearance_rank, availability_date);
CREATE INDEX IF NOT EXISTS consultants_skills_gin_idx ON consultants USING gin (skills);
CREATE INDEX IF NOT EXISTS consultants_embedding_hnsw_idx
    ON consultants USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS engagement_briefs (
    id UUID PRIMARY KEY,
    raw_brief TEXT NOT NULL CHECK (char_length(raw_brief) BETWEEN 40 AND 1600),
    extracted_requirements JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS composition_runs (
    id UUID PRIMARY KEY,
    brief_id UUID NOT NULL REFERENCES engagement_briefs(id),
    result JSONB NOT NULL,
    retrieval_mode TEXT NOT NULL CHECK (retrieval_mode IN ('postgres_pgvector', 'deterministic_demo')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS review_decisions (
    id UUID PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES composition_runs(id),
    status TEXT NOT NULL CHECK (status IN ('approved', 'needs_changes')),
    notes TEXT NOT NULL DEFAULT '' CHECK (char_length(notes) <= 600),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


def main() -> None:
    settings = get_settings()
    if not settings.database_url:
        raise SystemExit("DATABASE_URL is required. Set it in an uncommitted .env file first.")
    with connect(settings.database_url) as connection, connection.cursor() as cursor:
        cursor.execute(SCHEMA_SQL)
        connection.commit()
    print("Database schema and pgvector extension are ready.")


if __name__ == "__main__":
    main()

from collections.abc import Iterable
from datetime import date
from uuid import UUID, uuid4

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool

from .demo_data import CONSULTANTS
from .domain import (
    BriefRequirements,
    ComposeResponse,
    ConstraintCheck,
    Consultant,
    ReviewInput,
    TeamAssignment,
)

CLEARANCE_RANK = {"baseline": 1, "sc": 2, "dv": 3}


def _constraint_checks(consultant: Consultant, requirements: BriefRequirements) -> list[ConstraintCheck]:
    clearance_passes = CLEARANCE_RANK[consultant.clearance] >= CLEARANCE_RANK[requirements.minimum_clearance]
    availability_passes = consultant.availability_date <= date(2026, 9, 7)
    skill_overlap = sorted(set(consultant.skills).intersection(requirements.required_skills))
    return [
        ConstraintCheck(
            label="Clearance",
            passed=clearance_passes,
            evidence=f"{consultant.clearance.upper()} recorded; {requirements.minimum_clearance.upper()} required.",
        ),
        ConstraintCheck(
            label="Availability",
            passed=availability_passes,
            evidence=f"Available {consultant.availability_date.isoformat()} before the delivery start window.",
        ),
        ConstraintCheck(
            label="Relevant capability",
            passed=bool(skill_overlap),
            evidence=(", ".join(skill_overlap) if skill_overlap else "No direct capability overlap recorded."),
        ),
    ]


class DemoRepository:
    def __init__(self) -> None:
        self.runs: dict[UUID, ComposeResponse] = {}
        self.reviews: dict[UUID, ReviewInput] = {}

    def rank(self, requirements: BriefRequirements) -> list[TeamAssignment]:
        assignments: list[TeamAssignment] = []
        used_ids: set[UUID] = set()
        for requested_role in requirements.requested_roles:
            ranked: list[tuple[float, Consultant, list[ConstraintCheck]]] = []
            for consultant in CONSULTANTS:
                checks = _constraint_checks(consultant, requirements)
                if not all(check.passed for check in checks[:2]):
                    continue
                skill_overlap = len(set(consultant.skills).intersection(requirements.required_skills))
                sector_overlap = len(set(consultant.sectors).intersection(requirements.preferred_sectors))
                role_bonus = 3 if consultant.role.lower() == requested_role.lower() else 0
                score = min(0.58 + (skill_overlap * 0.08) + (sector_overlap * 0.05) + (role_bonus * 0.04), 0.97)
                ranked.append((score, consultant, checks))
            ranked.sort(key=lambda item: item[0], reverse=True)
            unused = [item for item in ranked if item[1].id not in used_ids]
            exact_role_matches = [
                item for item in unused if item[1].role.lower() == requested_role.lower()
            ]
            chosen = (exact_role_matches or unused or [None])[0]
            if chosen is None:
                continue
            score, consultant, checks = chosen
            used_ids.add(consultant.id)
            assignments.append(
                TeamAssignment(
                    consultant=consultant,
                    role_on_team=requested_role,
                    semantic_score=round(score, 2),
                    hard_constraints=checks,
                    explanation="",
                )
            )
        return assignments

    def record_run(self, response: ComposeResponse) -> None:
        self.runs[response.run_id] = response

    def record_review(self, run_id: UUID, review: ReviewInput) -> None:
        if run_id not in self.runs:
            raise KeyError(run_id)
        self.reviews[run_id] = review


class PostgresRepository:
    """Small pool sized for Aiven's free-tier 20-connection limit."""

    def __init__(self, database_url: str) -> None:
        self.pool = ConnectionPool(conninfo=database_url, min_size=1, max_size=3, timeout=10, open=False)

    def open(self) -> None:
        self.pool.open(wait=True)

    def close(self) -> None:
        self.pool.close()

    def rank(self, requirements: BriefRequirements, query_embedding: Iterable[float]) -> list[TeamAssignment]:
        vector = "[" + ",".join(f"{value:.8f}" for value in query_embedding) + "]"
        required_skills = requirements.required_skills
        min_rank = CLEARANCE_RANK[requirements.minimum_clearance]
        sql = """
            SELECT id, name, role, seniority, location, availability_date, clearance,
                   skills, sectors, profile_text, evidence,
                   1 - (embedding <=> %(vector)s::vector) AS semantic_score
            FROM consultants
            WHERE clearance_rank >= %(minimum_clearance)s
              AND availability_date <= %(latest_start)s
              AND skills && %(required_skills)s::text[]
            ORDER BY embedding <=> %(vector)s::vector
            LIMIT 12
        """
        with self.pool.connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                sql,
                {
                    "vector": vector,
                    "minimum_clearance": min_rank,
                    "latest_start": date(2026, 9, 7),
                    "required_skills": required_skills,
                },
            )
            rows = cursor.fetchall()
        candidates = [
            Consultant(
                id=row["id"],
                name=row["name"],
                role=row["role"],
                seniority=row["seniority"],
                location=row["location"],
                availability_date=row["availability_date"],
                clearance=row["clearance"],
                skills=row["skills"],
                sectors=row["sectors"],
                profile_text=row["profile_text"],
                evidence=row["evidence"],
            )
            for row in rows
        ]
        return self._assign_roles(candidates, requirements, rows)

    def record_run(self, raw_brief: str, response: ComposeResponse) -> None:
        brief_id = uuid4()
        with self.pool.connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO engagement_briefs (id, raw_brief, extracted_requirements)
                VALUES (%s, %s, %s)
                """,
                (brief_id, raw_brief, Jsonb(response.requirements.model_dump(mode="json"))),
            )
            cursor.execute(
                """
                INSERT INTO composition_runs (id, brief_id, result, retrieval_mode)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    response.run_id,
                    brief_id,
                    Jsonb(response.model_dump(mode="json")),
                    response.retrieval_mode,
                ),
            )
            connection.commit()

    def record_review(self, run_id: UUID, review: ReviewInput) -> None:
        with self.pool.connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO review_decisions (id, run_id, status, notes)
                VALUES (%s, %s, %s, %s)
                """,
                (uuid4(), run_id, review.status, review.notes),
            )
            connection.commit()

    @staticmethod
    def _assign_roles(
        candidates: list[Consultant], requirements: BriefRequirements, rows: list[dict]
    ) -> list[TeamAssignment]:
        scores = {str(row["id"]): float(row["semantic_score"]) for row in rows}
        assignments: list[TeamAssignment] = []
        used_ids: set[UUID] = set()
        for role in requirements.requested_roles:
            candidates_for_role = sorted(
                candidates,
                key=lambda candidate: (
                    candidate.role.lower() != role.lower(),
                    -scores[str(candidate.id)],
                ),
            )
            consultant = next((candidate for candidate in candidates_for_role if candidate.id not in used_ids), None)
            if consultant is None:
                continue
            used_ids.add(consultant.id)
            assignments.append(
                TeamAssignment(
                    consultant=consultant,
                    role_on_team=role,
                    semantic_score=round(max(0.0, scores[str(consultant.id)]), 2),
                    hard_constraints=_constraint_checks(consultant, requirements),
                    explanation="",
                )
            )
        return assignments

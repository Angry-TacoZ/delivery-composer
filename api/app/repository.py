from collections.abc import Iterable
from datetime import date
from uuid import UUID, uuid4

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool

from .demo_data import CONSULTANTS
from .domain import (
    BriefRequirements,
    CandidateOption,
    ComposeResponse,
    ConstraintCheck,
    Consultant,
    ReviewInput,
    ScoreComponent,
    TeamAssignment,
)

CLEARANCE_RANK = {"baseline": 1, "sc": 2, "dv": 3}


def _constraint_checks(consultant: Consultant, requirements: BriefRequirements) -> list[ConstraintCheck]:
    clearance_passes = CLEARANCE_RANK[consultant.clearance] >= CLEARANCE_RANK[requirements.minimum_clearance]
    latest_start = requirements.target_start or date(2026, 9, 7)
    availability_passes = consultant.availability_date <= latest_start
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
            evidence=(
                f"Available {consultant.availability_date.isoformat()}; "
                f"required by {latest_start.isoformat()}."
            ),
        ),
        ConstraintCheck(
            label="Relevant capability",
            passed=bool(skill_overlap),
            evidence=(", ".join(skill_overlap) if skill_overlap else "No direct capability overlap recorded."),
        ),
    ]


def _deterministic_score(
    consultant: Consultant,
    requirements: BriefRequirements,
) -> tuple[float, list[ScoreComponent]]:
    skill_overlap = sorted(set(consultant.skills).intersection(requirements.required_skills))
    sector_overlap = sorted(set(consultant.sectors).intersection(requirements.preferred_sectors))
    components = [
        ScoreComponent(
            label="Exact role baseline",
            points=58,
            evidence=f"Profile role matches {consultant.role}.",
        ),
        ScoreComponent(
            label="Required capabilities",
            points=len(skill_overlap) * 8,
            evidence=(
                f"{', '.join(skill_overlap)} matched at 8 points each."
                if skill_overlap
                else "No required capability matches recorded."
            ),
        ),
        ScoreComponent(
            label="Preferred sectors",
            points=len(sector_overlap) * 5,
            evidence=(
                f"{', '.join(sector_overlap)} matched at 5 points each."
                if sector_overlap
                else "No preferred sector matches recorded."
            ),
        ),
    ]
    raw_points = sum(component.points for component in components)
    if raw_points > 97:
        components.append(
            ScoreComponent(
                label="Score cap",
                points=97 - raw_points,
                evidence="The deterministic alignment score is capped at 97 points.",
            )
        )
    total_points = sum(component.points for component in components)
    return total_points / 100, components


def _candidate_option(
    consultant: Consultant,
    requirements: BriefRequirements,
    semantic_score: float | None = None,
) -> CandidateOption:
    if semantic_score is None:
        final_score, score_breakdown = _deterministic_score(consultant, requirements)
        score_method = "deterministic_rubric"
    else:
        final_score = min(1.0, max(0.0, semantic_score))
        score_method = "pgvector_similarity"
        score_breakdown = [
            ScoreComponent(
                label="pgvector similarity",
                points=round(final_score * 100),
                evidence="Cosine similarity from the stored profile embedding; not decomposed into narrative evidence points.",
            )
        ]
    return CandidateOption(
        consultant=consultant,
        semantic_score=final_score,
        score_method=score_method,
        score_breakdown=score_breakdown,
        hard_constraints=_constraint_checks(consultant, requirements),
        explanation=(
            f"{consultant.name} brings role-specific evidence for this option; the recorded "
            "strengths, considerations, and constraint checks remain visible for human comparison."
        ),
    )


def _role_assignment(
    role: str,
    consultants: list[Consultant],
    requirements: BriefRequirements,
    scores: dict[str, float] | None = None,
) -> TeamAssignment:
    role_candidates = [candidate for candidate in consultants if candidate.role.lower() == role.lower()]
    if len(role_candidates) != 3:
        raise ValueError(f"Expected exactly three synthetic candidates for {role}.")
    options = [
        _candidate_option(
            candidate,
            requirements,
            max(0.0, scores[str(candidate.id)]) if scores is not None else None,
        )
        for candidate in role_candidates
    ]
    options.sort(
        key=lambda option: (
            not all(check.passed for check in option.hard_constraints[:2]),
            -option.semantic_score,
        )
    )
    recommended = next(
        (option for option in options if all(check.passed for check in option.hard_constraints[:2])),
        None,
    )
    if recommended is None:
        raise ValueError(f"No eligible {role} candidate meets clearance and availability.")
    recommended_data = recommended.model_dump()
    recommended_data["explanation"] = ""
    return TeamAssignment(**recommended_data, role_on_team=role, alternatives=options)


def _validate_review_overrides(response: ComposeResponse, review: ReviewInput) -> None:
    assignments = {assignment.role_on_team: assignment for assignment in response.assignments}
    seen_roles: set[str] = set()
    for override in review.overrides:
        if override.role in seen_roles:
            raise ValueError(f"Only one override may be recorded for {override.role}.")
        seen_roles.add(override.role)
        assignment = assignments.get(override.role)
        if assignment is None or assignment.consultant.id != override.original_consultant_id:
            raise ValueError("Override does not match the recorded recommendation.")
        allowed_ids = {option.consultant.id for option in assignment.alternatives}
        if override.selected_consultant_id not in allowed_ids:
            raise ValueError("Override candidate was not offered for this role.")


class DemoRepository:
    def __init__(self) -> None:
        self.runs: dict[UUID, ComposeResponse] = {}
        self.reviews: dict[UUID, ReviewInput] = {}

    def rank(self, requirements: BriefRequirements) -> list[TeamAssignment]:
        return [
            _role_assignment(role, CONSULTANTS, requirements)
            for role in requirements.requested_roles
        ]

    def record_run(self, response: ComposeResponse) -> None:
        self.runs[response.run_id] = response

    def record_review(self, run_id: UUID, review: ReviewInput) -> None:
        if run_id not in self.runs:
            raise KeyError(run_id)
        _validate_review_overrides(self.runs[run_id], review)
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
                   skills, sectors, profile_text, evidence, considerations,
                   1 - (embedding <=> %(vector)s::vector) AS semantic_score
            FROM consultants
            WHERE role = ANY(%(requested_roles)s::text[])
            ORDER BY
              (clearance_rank >= %(minimum_clearance)s
               AND availability_date <= %(latest_start)s
               AND skills && %(required_skills)s::text[]) DESC,
              embedding <=> %(vector)s::vector
            LIMIT 30
        """
        with self.pool.connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                sql,
                {
                    "vector": vector,
                    "minimum_clearance": min_rank,
                    "latest_start": requirements.target_start or date(2026, 9, 7),
                    "required_skills": required_skills,
                    "requested_roles": requirements.requested_roles,
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
                considerations=row["considerations"],
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
            cursor.execute("SELECT result FROM composition_runs WHERE id = %s", (run_id,))
            row = cursor.fetchone()
            if row is None:
                raise KeyError(run_id)
            _validate_review_overrides(ComposeResponse.model_validate(row[0]), review)
            cursor.execute(
                """
                INSERT INTO review_decisions (id, run_id, status, notes, overrides)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (run_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    notes = EXCLUDED.notes,
                    overrides = EXCLUDED.overrides
                """,
                (uuid4(), run_id, review.status, review.notes, Jsonb([item.model_dump(mode="json") for item in review.overrides])),
            )
            connection.commit()

    @staticmethod
    def _assign_roles(
        candidates: list[Consultant], requirements: BriefRequirements, rows: list[dict]
    ) -> list[TeamAssignment]:
        scores = {str(row["id"]): float(row["semantic_score"]) for row in rows}
        return [
            _role_assignment(role, candidates, requirements, scores)
            for role in requirements.requested_roles
        ]

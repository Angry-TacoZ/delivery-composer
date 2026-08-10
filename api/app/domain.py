from datetime import UTC, date, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

Clearance = Literal["baseline", "sc", "dv"]
ReviewStatus = Literal["approved", "needs_changes"]
ReviewPersistence = Literal["session", "postgres"]


class BriefInput(BaseModel):
    raw_brief: str = Field(min_length=40, max_length=1600)

    @field_validator("raw_brief")
    @classmethod
    def normalize_brief(cls, value: str) -> str:
        return " ".join(value.split())


class BriefRequirements(BaseModel):
    title: str = Field(max_length=120)
    required_skills: list[str] = Field(min_length=1, max_length=8)
    preferred_sectors: list[str] = Field(default_factory=list, max_length=5)
    minimum_clearance: Clearance = "baseline"
    target_start: date | None = None
    requested_roles: list[str] = Field(min_length=1, max_length=4)
    constraints: list[str] = Field(default_factory=list, max_length=6)
    extraction_source: Literal["gemini", "deterministic_demo"]


class Consultant(BaseModel):
    id: UUID
    name: str
    role: str
    seniority: str
    location: str
    availability_date: date
    clearance: Clearance
    skills: list[str]
    sectors: list[str]
    profile_text: str
    evidence: list[str]


class ConstraintCheck(BaseModel):
    label: str
    passed: bool
    evidence: str


class TeamAssignment(BaseModel):
    consultant: Consultant
    role_on_team: str
    semantic_score: float = Field(ge=0, le=1)
    hard_constraints: list[ConstraintCheck]
    explanation: str


class ComposeResponse(BaseModel):
    run_id: UUID = Field(default_factory=uuid4)
    requirements: BriefRequirements
    assignments: list[TeamAssignment]
    summary: str
    retrieval_mode: Literal["postgres_pgvector", "deterministic_demo"]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ReviewInput(BaseModel):
    status: ReviewStatus
    notes: str = Field(default="", max_length=600)


class ReviewResponse(BaseModel):
    run_id: UUID
    status: ReviewStatus
    persistence_mode: ReviewPersistence
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PDFBriefResponse(BaseModel):
    file_name: str
    page_count: int = Field(ge=1, le=5)
    character_count: int = Field(ge=40, le=1600)
    text: str = Field(min_length=40, max_length=1600)


class DemoBriefResponse(BaseModel):
    slug: str = Field(pattern=r"^[a-z0-9-]+$", max_length=80)
    reference: str = Field(pattern=r"^SYN-[A-Z]+-\d{3}$", max_length=20)
    title: str = Field(max_length=120)
    sector: str = Field(max_length=120)
    brief: str = Field(min_length=40, max_length=1600)

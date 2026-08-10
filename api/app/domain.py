from datetime import UTC, date, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

Clearance = Literal["baseline", "sc", "dv"]
ReviewStatus = Literal["approved", "needs_changes"]
ReviewPersistence = Literal["session", "postgres"]


class BriefInput(BaseModel):
    raw_brief: str = Field(min_length=40, max_length=1600)
    parent_run_id: UUID | None = None
    revision_feedback: str | None = Field(default=None, max_length=600)

    @field_validator("raw_brief")
    @classmethod
    def normalize_brief(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("revision_feedback")
    @classmethod
    def normalize_revision_feedback(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return " ".join(value.split())

    @model_validator(mode="after")
    def revision_context_must_be_complete(self) -> "BriefInput":
        has_parent = self.parent_run_id is not None
        has_feedback = self.revision_feedback is not None
        if has_parent != has_feedback:
            raise ValueError("Revision feedback and parent run must be supplied together.")
        if self.revision_feedback is not None and len(self.revision_feedback) < 10:
            raise ValueError("Revision feedback must contain at least 10 characters.")
        return self


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
    considerations: list[str]


class ConstraintCheck(BaseModel):
    label: str
    passed: bool
    evidence: str


class ScoreComponent(BaseModel):
    label: str = Field(max_length=80)
    points: int = Field(ge=-100, le=100)
    evidence: str = Field(max_length=240)


class CandidateOption(BaseModel):
    consultant: Consultant
    semantic_score: float = Field(ge=0, le=1)
    score_method: Literal["deterministic_rubric", "pgvector_similarity"]
    score_breakdown: list[ScoreComponent] = Field(min_length=1, max_length=5)
    hard_constraints: list[ConstraintCheck]
    explanation: str


class TeamAssignment(CandidateOption):
    role_on_team: str
    alternatives: list[CandidateOption] = Field(min_length=3, max_length=3)


class ComposeResponse(BaseModel):
    run_id: UUID = Field(default_factory=uuid4)
    requirements: BriefRequirements
    assignments: list[TeamAssignment]
    summary: str
    retrieval_mode: Literal["postgres_pgvector", "deterministic_demo"]
    parent_run_id: UUID | None = None
    revision_feedback: str | None = Field(default=None, max_length=600)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TeamOverride(BaseModel):
    role: str = Field(min_length=2, max_length=80)
    original_consultant_id: UUID
    selected_consultant_id: UUID

    @model_validator(mode="after")
    def selected_candidate_must_change(self) -> "TeamOverride":
        if self.original_consultant_id == self.selected_consultant_id:
            raise ValueError("An override must select a different consultant.")
        return self


class ReviewInput(BaseModel):
    status: ReviewStatus
    notes: str = Field(default="", max_length=600)
    overrides: list[TeamOverride] = Field(default_factory=list, max_length=4)

    @model_validator(mode="after")
    def revision_requires_actionable_notes(self) -> "ReviewInput":
        self.notes = " ".join(self.notes.split())
        if self.status == "needs_changes" and len(self.notes) < 10:
            raise ValueError("Revision feedback must contain at least 10 characters.")
        return self


class ReviewResponse(BaseModel):
    run_id: UUID
    status: ReviewStatus
    persistence_mode: ReviewPersistence
    override_count: int = Field(ge=0, le=4)
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

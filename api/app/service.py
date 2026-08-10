from .config import Settings
from .domain import BriefInput, ComposeResponse, ReviewInput, ReviewPersistence
from .providers import AnalysisProvider
from .repository import DemoRepository, PostgresRepository


class ComposerService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        if not settings.demo_mode and not settings.live_path_configured:
            raise RuntimeError(
                "Live mode requires both DATABASE_URL and GEMINI_API_KEY. "
                "Set DEMO_MODE=true for the deterministic preview."
            )
        self.provider = AnalysisProvider(settings)
        self.demo_repository = DemoRepository()
        self.postgres_repository = (
            PostgresRepository(settings.database_url) if settings.live_path_enabled else None
        )

    def startup(self) -> None:
        if self.postgres_repository is not None:
            self.postgres_repository.open()

    def shutdown(self) -> None:
        if self.postgres_repository is not None:
            self.postgres_repository.close()

    def compose(self, brief_input: BriefInput) -> ComposeResponse:
        requirements = self.provider.extract_requirements(brief_input.raw_brief)
        if self.uses_live_path:
            assignments = self.postgres_repository.rank(
                requirements, self.provider.embed_query(brief_input.raw_brief)
            )
            retrieval_mode = "postgres_pgvector"
        else:
            assignments = self.demo_repository.rank(requirements)
            retrieval_mode = "deterministic_demo"

        if not assignments:
            raise ValueError("No eligible team could be composed from the available profiles.")
        summary, explanations = self.provider.compose_explanations(requirements, assignments)
        completed_assignments = [
            assignment.model_copy(update={"explanation": explanation})
            for assignment, explanation in zip(assignments, explanations, strict=True)
        ]
        response = ComposeResponse(
            requirements=requirements,
            assignments=completed_assignments,
            summary=summary,
            retrieval_mode=retrieval_mode,
        )
        if self.uses_live_path:
            self.postgres_repository.record_run(brief_input.raw_brief, response)
        else:
            self.demo_repository.record_run(response)
        return response

    @property
    def uses_live_path(self) -> bool:
        return self.settings.live_path_enabled and self.postgres_repository is not None

    def record_review(self, run_id, review: ReviewInput) -> ReviewPersistence:
        if self.uses_live_path:
            self.postgres_repository.record_review(run_id, review)
            return "postgres"
        self.demo_repository.record_review(run_id, review)
        return "session"

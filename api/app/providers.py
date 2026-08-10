import json
import re
from collections.abc import Sequence
from datetime import date

from google import genai
from google.genai import types

from .config import Settings
from .domain import BriefRequirements, TeamAssignment


class AnalysisProvider:
    """Server-side AI boundary. Never instantiate this class in browser code."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = (
            genai.Client(api_key=settings.gemini_api_key.get_secret_value())
            if settings.live_path_enabled
            else None
        )

    def extract_requirements(
        self,
        brief: str,
        revision_feedback: str | None = None,
    ) -> BriefRequirements:
        if self.client is None:
            return self._deterministic_requirements(brief, revision_feedback)

        prompt = (
            "Extract delivery-team requirements from this consulting brief. Do not invent "
            "credentials, sectors, dates, or client facts. Normalise skills to concise "
            "lowercase labels. Apply the bounded revision feedback when present. Return only "
            "the requested schema.\n\nBRIEF:\n"
            + brief
            + (f"\n\nREVISION FEEDBACK:\n{revision_feedback}" if revision_feedback else "")
        )
        response = self.client.models.generate_content(
            model=self.settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=BriefRequirements,
                temperature=0.1,
            ),
        )
        requirements = BriefRequirements.model_validate_json(response.text)
        return requirements.model_copy(update={"extraction_source": "gemini"})

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text, "RETRIEVAL_QUERY")

    def embed_document(self, text: str) -> list[float]:
        return self._embed(text, "RETRIEVAL_DOCUMENT")

    def _embed(self, text: str, task_type: str) -> list[float]:
        if self.client is None:
            raise RuntimeError("GEMINI_API_KEY is required for pgvector retrieval.")
        response = self.client.models.embed_content(
            model=self.settings.embedding_model,
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=self.settings.embedding_dimensions,
                task_type=task_type,
            ),
        )
        embeddings = response.embeddings
        first_embedding = embeddings[0] if isinstance(embeddings, Sequence) else embeddings
        return list(first_embedding.values)

    def compose_explanations(
        self, requirements: BriefRequirements, assignments: list[TeamAssignment]
    ) -> tuple[str, list[str]]:
        """Return evidence-grounded prose without allowing the model to alter scores or checks."""
        roles = ", ".join(assignment.role_on_team for assignment in assignments)
        capabilities = ", ".join(requirements.required_skills[:4])
        fallback_summary = (
            f"The proposed {roles} team covers the recorded priorities of {capabilities}. "
            "The recommendation keeps availability, clearance, and evidence checks visible "
            "for human assurance."
        )
        fallback_explanations = [
            f"{assignment.consultant.name} is recommended because the verified profile evidence "
            f"matches the {assignment.role_on_team} role and recorded constraints."
            for assignment in assignments
        ]
        if self.client is None:
            return fallback_summary, fallback_explanations

        payload = {
            "requirements": requirements.model_dump(mode="json"),
            "assignments": [
                {
                    "name": assignment.consultant.name,
                    "role": assignment.role_on_team,
                    "evidence": assignment.consultant.evidence,
                    "checks": [check.model_dump() for check in assignment.hard_constraints],
                }
                for assignment in assignments
            ],
        }
        prompt = (
            "Write one concise, evidence-grounded team summary and one sentence per assigned "
            "consultant. Use only supplied evidence. Do not claim a consultant has a skill or "
            "credential that is not in the input. Return JSON with `summary` and `explanations`.\n\n"
            + json.dumps(payload)
        )
        response = self.client.models.generate_content(
            model=self.settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2),
        )
        try:
            result = json.loads(response.text)
            explanations = result.get("explanations", [])
            if isinstance(result.get("summary"), str) and len(explanations) == len(assignments):
                return result["summary"], [str(item) for item in explanations]
        except (TypeError, ValueError):
            pass
        return fallback_summary, fallback_explanations

    @staticmethod
    def _deterministic_requirements(
        brief: str,
        revision_feedback: str | None = None,
    ) -> BriefRequirements:
        normalized = brief.lower()
        searchable = re.sub(r"[-_/]+", " ", normalized)
        skills = []
        for label, triggers in {
            "zero trust": ("zero trust", "identity"),
            "cloud transformation": ("cloud", "platform"),
            "data governance": ("data governance", "governed data"),
            "security operations": ("security operations", "soc", "threat detection"),
            "ai engineering": (
                "artificial intelligence",
                "ai enabled",
                "ai assisted",
                "ai engineering",
                "retrieval",
                "automation",
            ),
            "platform engineering": ("platform engineering", "terraform", "infrastructure as code"),
            "incident response": ("incident response", "service recovery", "major incident"),
        }.items():
            if any(trigger in searchable for trigger in triggers):
                skills.append(label)
        if not skills:
            skills = ["delivery leadership", "cloud transformation"]

        clearance = (
            "dv"
            if re.search(r"\bdv\b", searchable)
            else "sc"
            if re.search(r"\bsc\b", searchable)
            else "baseline"
        )
        sector_triggers = {
            "critical infrastructure": ("critical infrastructure", "national infrastructure"),
            "public sector": ("public sector", "central government"),
            "financial services": ("financial services", "bank", "insurance"),
            "media": ("media", "broadcast"),
            "transport": ("transport", "rail", "aviation"),
            "defence": ("defence", "defense"),
        }
        sectors = [
            sector
            for sector, triggers in sector_triggers.items()
            if any(trigger in searchable for trigger in triggers)
        ]

        start_match = re.search(r"\b20\d{2}-\d{2}-\d{2}\b", normalized)
        target_start = date.fromisoformat(start_match.group()) if start_match else date(2026, 9, 7)

        if "media" in sectors:
            title = "Media and broadcast platform recovery team"
            requested_roles = ["Delivery Lead", "Cloud Engineer", "Security Consultant"]
        elif "financial services" in sectors:
            title = "Financial services AI governance delivery team"
            requested_roles = ["Delivery Lead", "Data & AI Engineer", "Security Consultant"]
        elif "critical infrastructure" in sectors or "public sector" in sectors:
            title = "Critical infrastructure resilience delivery team"
            requested_roles = ["Delivery Lead", "Security Architect", "Data & AI Engineer"]
        else:
            title = "Multi-sector technology delivery team"
            requested_roles = ["Delivery Lead", "Cloud Engineer", "Data & AI Engineer"]

        if revision_feedback:
            feedback = " ".join(re.sub(r"[-_/&]+", " ", revision_feedback.lower()).split())
            if "replace" in feedback and "with" in feedback:
                before, after = feedback.split("with", 1)
                role_triggers = {
                    "Delivery Lead": ("delivery lead",),
                    "Security Architect": ("security architect",),
                    "Data & AI Engineer": ("data and ai engineer", "data ai engineer"),
                    "Cloud Engineer": ("cloud engineer",),
                    "Security Consultant": ("security consultant",),
                }
                replaced_role = next(
                    (
                        role
                        for role, triggers in role_triggers.items()
                        if any(trigger in before for trigger in triggers)
                    ),
                    None,
                )
                replacement_role = next(
                    (
                        role
                        for role, triggers in role_triggers.items()
                        if any(trigger in after for trigger in triggers)
                    ),
                    None,
                )
                if (
                    replaced_role in requested_roles
                    and replacement_role is not None
                    and replacement_role not in requested_roles
                ):
                    requested_roles[requested_roles.index(replaced_role)] = replacement_role

        return BriefRequirements(
            title=title,
            required_skills=skills,
            preferred_sectors=sectors,
            minimum_clearance=clearance,
            target_start=target_start,
            requested_roles=requested_roles,
            constraints=[
                f"Available by {target_start.isoformat()}",
                "Use verified profile evidence",
            ],
            extraction_source="deterministic_demo",
        )

import json
import re
from collections.abc import Sequence

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
            if settings.has_gemini
            else None
        )

    def extract_requirements(self, brief: str) -> BriefRequirements:
        if self.client is None:
            return self._deterministic_requirements(brief)

        prompt = (
            "Extract delivery-team requirements from this consulting brief. Do not invent "
            "credentials, sectors, dates, or client facts. Normalise skills to concise "
            "lowercase labels. Return only the requested schema.\n\nBRIEF:\n" + brief
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
        fallback_summary = (
            "The proposed team covers delivery leadership, zero-trust architecture, and "
            "governed AI/security-operations delivery. Every selected consultant passes the "
            "recorded availability and clearance checks."
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
    def _deterministic_requirements(brief: str) -> BriefRequirements:
        normalized = brief.lower()
        skills = []
        for label, triggers in {
            "zero trust": ("zero trust", "identity"),
            "cloud transformation": ("cloud", "platform"),
            "data governance": ("data governance", "governed data"),
            "security operations": ("security operations", "soc", "threat detection"),
            "ai engineering": ("ai", "retrieval", "automation"),
        }.items():
            if any(trigger in normalized for trigger in triggers):
                skills.append(label)
        if not skills:
            skills = ["delivery leadership", "cloud transformation"]

        clearance = "dv" if re.search(r"\bdv\b", normalized) else "sc" if re.search(r"\bsc\b", normalized) else "baseline"
        sectors = [
            sector
            for sector in ("critical infrastructure", "public sector", "financial services")
            if sector in normalized
        ]
        return BriefRequirements(
            title="Critical infrastructure resilience delivery team",
            required_skills=skills,
            preferred_sectors=sectors,
            minimum_clearance=clearance,
            requested_roles=["Delivery Lead", "Security Architect", "Data & AI Engineer"],
            constraints=["Start within four weeks", "Use verified profile evidence"],
            extraction_source="deterministic_demo",
        )

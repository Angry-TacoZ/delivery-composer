from datetime import date
from uuid import UUID

from .domain import Consultant

DEMO_BRIEF = """Build a three-person delivery team for a critical-infrastructure resilience programme.
The client needs a security-first discovery and implementation plan covering zero trust,
cloud transformation, data governance, and an AI-assisted security operations use case.
The engagement starts in four weeks and requires SC-cleared consultants with public-sector
or regulated-infrastructure experience."""


CONSULTANTS: list[Consultant] = [
    Consultant(
        id=UUID("7f03d4f0-5582-4c00-8226-d4e9f7b9a001"),
        name="Maya Patel",
        role="Security Architect",
        seniority="Principal",
        location="London",
        availability_date=date(2026, 8, 24),
        clearance="sc",
        skills=["zero trust", "cloud transformation", "security architecture", "identity"],
        sectors=["critical infrastructure", "public sector"],
        profile_text="Principal security architect who has led zero-trust and identity modernisation for regulated national infrastructure programmes.",
        evidence=[
            "Led a zero-trust architecture assessment for a regulated infrastructure operator.",
            "SC cleared and available before the requested start date.",
        ],
    ),
    Consultant(
        id=UUID("7f03d4f0-5582-4c00-8226-d4e9f7b9a002"),
        name="Theo Morgan",
        role="Delivery Lead",
        seniority="Director",
        location="Manchester",
        availability_date=date(2026, 8, 17),
        clearance="sc",
        skills=["delivery leadership", "cloud transformation", "stakeholder management", "governance"],
        sectors=["public sector", "transport"],
        profile_text="Delivery director experienced in recovery, discovery, and multi-vendor governance for public-sector and transport programmes.",
        evidence=[
            "Recovered a cross-supplier cloud programme and established a delivery cadence.",
            "Has run discovery through implementation with senior public-sector stakeholders.",
        ],
    ),
    Consultant(
        id=UUID("7f03d4f0-5582-4c00-8226-d4e9f7b9a003"),
        name="Amina Okafor",
        role="Data & AI Engineer",
        seniority="Lead",
        location="Bristol",
        availability_date=date(2026, 8, 31),
        clearance="sc",
        skills=["data governance", "ai engineering", "security operations", "python", "postgresql"],
        sectors=["critical infrastructure", "financial services"],
        profile_text="Lead data and AI engineer who builds governed retrieval and automation workflows for security operations teams.",
        evidence=[
            "Built evidence-grounded retrieval workflows for security analysts.",
            "Combines data governance, Python delivery, and security operations experience.",
        ],
    ),
    Consultant(
        id=UUID("7f03d4f0-5582-4c00-8226-d4e9f7b9a004"),
        name="Jon Bell",
        role="Cloud Engineer",
        seniority="Senior",
        location="Leeds",
        availability_date=date(2026, 9, 21),
        clearance="baseline",
        skills=["cloud transformation", "platform engineering", "terraform", "aws"],
        sectors=["media"],
        profile_text="Senior cloud engineer specialising in platform automation and Terraform foundations.",
        evidence=["Strong cloud implementation experience but does not meet the clearance requirement."],
    ),
    Consultant(
        id=UUID("7f03d4f0-5582-4c00-8226-d4e9f7b9a005"),
        name="Elena Rossi",
        role="Security Consultant",
        seniority="Senior",
        location="Edinburgh",
        availability_date=date(2026, 8, 18),
        clearance="dv",
        skills=["zero trust", "security operations", "threat detection", "incident response"],
        sectors=["government", "defence"],
        profile_text="Senior security consultant focused on threat detection and SOC transformation in high-assurance environments.",
        evidence=["Exceeds the clearance threshold and brings SOC operating-model depth."],
    ),
]


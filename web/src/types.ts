export type Clearance = "baseline" | "sc" | "dv";

export interface BriefRequirements {
  title: string;
  required_skills: string[];
  preferred_sectors: string[];
  minimum_clearance: Clearance;
  requested_roles: string[];
  constraints: string[];
  extraction_source: "gemini" | "deterministic_demo";
}

export interface ConstraintCheck {
  label: string;
  passed: boolean;
  evidence: string;
}

export interface Consultant {
  id: string;
  name: string;
  role: string;
  seniority: string;
  location: string;
  availability_date: string;
  clearance: Clearance;
  skills: string[];
  sectors: string[];
  evidence: string[];
}

export interface TeamAssignment {
  consultant: Consultant;
  role_on_team: string;
  semantic_score: number;
  hard_constraints: ConstraintCheck[];
  explanation: string;
}

export interface ComposeResponse {
  run_id: string;
  requirements: BriefRequirements;
  assignments: TeamAssignment[];
  summary: string;
  retrieval_mode: "postgres_pgvector" | "deterministic_demo";
  generated_at: string;
}

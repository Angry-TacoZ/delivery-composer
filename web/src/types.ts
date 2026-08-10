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
  considerations: string[];
}

export interface CandidateOption {
  consultant: Consultant;
  semantic_score: number;
  hard_constraints: ConstraintCheck[];
  explanation: string;
}

export interface TeamAssignment extends CandidateOption {
  role_on_team: string;
  alternatives: CandidateOption[];
}

export interface ComposeResponse {
  run_id: string;
  requirements: BriefRequirements;
  assignments: TeamAssignment[];
  summary: string;
  retrieval_mode: "postgres_pgvector" | "deterministic_demo";
  generated_at: string;
}

export interface ReviewResponse {
  run_id: string;
  status: "approved" | "needs_changes";
  persistence_mode: "session" | "postgres";
  override_count: number;
  recorded_at: string;
}

export interface TeamOverride {
  role: string;
  original_consultant_id: string;
  selected_consultant_id: string;
}

export interface PDFBriefResponse {
  file_name: string;
  page_count: number;
  character_count: number;
  text: string;
}

export interface DemoBrief {
  slug: string;
  reference: string;
  title: string;
  sector: string;
  brief: string;
}

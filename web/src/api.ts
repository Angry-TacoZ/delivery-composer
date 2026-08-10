import type { ComposeResponse, PDFBriefResponse, ReviewResponse } from "./types";

const API_BASE = "/api";

export async function fetchDemoBrief(): Promise<string> {
  const response = await fetch(`${API_BASE}/demo-brief`);
  if (!response.ok) throw new Error("The demo brief could not be loaded.");
  const data = (await response.json()) as { brief: string };
  return data.brief;
}

export async function composeTeam(rawBrief: string): Promise<ComposeResponse> {
  const response = await fetch(`${API_BASE}/compose`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_brief: rawBrief }),
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as { detail?: string };
    throw new Error(body.detail ?? "The team composition could not be completed.");
  }
  return (await response.json()) as ComposeResponse;
}

export async function extractPDFBrief(file: File): Promise<PDFBriefResponse> {
  const body = new FormData();
  body.append("file", file);
  const response = await fetch(`${API_BASE}/extract-brief`, {
    method: "POST",
    body,
  });
  if (!response.ok) {
    const payload = (await response.json().catch(() => ({}))) as { detail?: string };
    throw new Error(payload.detail ?? "The PDF brief could not be extracted.");
  }
  return (await response.json()) as PDFBriefResponse;
}

export async function recordReview(
  runId: string,
  status: "approved" | "needs_changes",
  notes: string,
): Promise<ReviewResponse> {
  const response = await fetch(`${API_BASE}/runs/${runId}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status, notes }),
  });
  if (!response.ok) throw new Error("The review decision could not be recorded.");
  return (await response.json()) as ReviewResponse;
}

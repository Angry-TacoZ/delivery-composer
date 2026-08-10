import { useEffect, useMemo, useState } from "react";

import { composeTeam, fetchDemoBrief, recordReview } from "./api";
import type { ComposeResponse, TeamAssignment } from "./types";

const FALLBACK_BRIEF = `Build a three-person delivery team for a critical-infrastructure resilience programme.
The client needs a security-first discovery and implementation plan covering zero trust,
cloud transformation, data governance, and an AI-assisted security operations use case.
The engagement starts in four weeks and requires SC-cleared consultants with public-sector
or regulated-infrastructure experience.`;

function percent(score: number): string {
  return `${Math.round(score * 100)}%`;
}

function AssignmentRow({ assignment, index }: { assignment: TeamAssignment; index: number }) {
  const [open, setOpen] = useState(index === 0);
  const allChecksPass = assignment.hard_constraints.every((check) => check.passed);

  return (
    <article className={`assignment ${open ? "is-open" : ""}`}>
      <button className="assignment-trigger" onClick={() => setOpen((value) => !value)} aria-expanded={open}>
        <span className="role-index">0{index + 1}</span>
        <span className="assignment-primary">
          <strong>{assignment.role_on_team}</strong>
          <span>{assignment.consultant.name} · {assignment.consultant.seniority}</span>
        </span>
        <span className="score-block" aria-label={`${percent(assignment.semantic_score)} semantic alignment`}>
          <span>{percent(assignment.semantic_score)}</span>
          <i style={{ "--score": assignment.semantic_score } as React.CSSProperties} />
        </span>
        <span className={allChecksPass ? "verified" : "exception"}>{allChecksPass ? "Verified" : "Review"}</span>
      </button>
      {open && (
        <div className="assignment-detail">
          <div className="evidence-copy">
            <p>{assignment.explanation}</p>
            <ul>
              {assignment.consultant.evidence.map((evidence) => <li key={evidence}>{evidence}</li>)}
            </ul>
          </div>
          <dl className="constraint-list">
            {assignment.hard_constraints.map((check) => (
              <div key={check.label}>
                <dt>{check.label}</dt>
                <dd className={check.passed ? "pass" : "fail"}>{check.evidence}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}
    </article>
  );
}

export default function App() {
  const [brief, setBrief] = useState(FALLBACK_BRIEF);
  const [result, setResult] = useState<ComposeResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reviewState, setReviewState] = useState<"approved" | "needs_changes" | null>(null);

  useEffect(() => {
    void fetchDemoBrief().then(setBrief).catch(() => undefined);
  }, []);

  const processLabel = useMemo(() => {
    if (result?.retrieval_mode === "postgres_pgvector") return "PostgreSQL + pgvector";
    return "Local deterministic preview";
  }, [result]);

  async function runComposition() {
    setIsRunning(true);
    setError(null);
    setReviewState(null);
    try {
      setResult(await composeTeam(brief));
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Analysis failed.");
    } finally {
      setIsRunning(false);
    }
  }

  async function submitReview(status: "approved" | "needs_changes") {
    if (!result) return;
    try {
      await recordReview(result.run_id, status);
      setReviewState(status);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Review could not be saved.");
    }
  }

  return (
    <main className="workspace">
      <header className="topbar">
        <a className="brand" href="/" aria-label="Delivery Composer home">
          <svg viewBox="0 0 28 28" aria-hidden="true"><path d="M3 3h13v13H3zM12 12h13v13H12z" /></svg>
          <span>Delivery<br />Composer</span>
        </a>
        <div className="topbar-context">
          <span>Staffing intelligence</span>
          <span className="live-marker"><i />Synthetic demo environment</span>
        </div>
        <span className="run-code">RUN / 01</span>
      </header>

      <section className="workspace-heading">
        <div>
          <p className="eyebrow">Evidence-first delivery composition</p>
          <h1>Build the team.<br /><em>Show the reasoning.</em></h1>
        </div>
        <p className="heading-note">Hard constraints are evaluated before semantic similarity. A person makes the final decision.</p>
      </section>

      <section className="composer-grid" aria-label="Delivery team composition workspace">
        <section className="brief-pane">
          <div className="pane-heading">
            <span>01 / Client brief</span>
            <button onClick={() => setBrief(FALLBACK_BRIEF)} className="text-button">Reset sample</button>
          </div>
          <textarea
            value={brief}
            onChange={(event) => setBrief(event.target.value)}
            maxLength={1600}
            aria-label="Client brief"
          />
          <div className="brief-meta">
            <span>{brief.length} / 1600</span>
            <span>Unstructured input</span>
          </div>
          <button className="compose-button" onClick={runComposition} disabled={isRunning || brief.trim().length < 40}>
            <span>{isRunning ? "Composing evidence…" : "Compose delivery team"}</span>
            <b>→</b>
          </button>
          {error && <p className="error-message" role="alert">{error}</p>}
        </section>

        <section className="recommendation-pane">
          <div className="pane-heading">
            <span>02 / Recommended composition</span>
            <span className="mode-label">{result ? processLabel : "Awaiting brief"}</span>
          </div>

          {!result ? (
            <div className="empty-state">
              <span className="empty-mark">↘</span>
              <p>Run the sample brief to inspect the proposed team, hard-constraint checks, and supporting evidence.</p>
            </div>
          ) : (
            <div className="result-content">
              <p className="result-summary">{result.summary}</p>
              <div className="assignment-list">
                {result.assignments.map((assignment, index) => <AssignmentRow key={assignment.consultant.id} assignment={assignment} index={index} />)}
              </div>
            </div>
          )}
        </section>

        <aside className="review-pane">
          <div className="pane-heading"><span>03 / Human review</span></div>
          {result ? (
            <>
              <dl className="requirements-list">
                <div><dt>Skills</dt><dd>{result.requirements.required_skills.join(" · ")}</dd></div>
                <div><dt>Clearance</dt><dd>{result.requirements.minimum_clearance.toUpperCase()} minimum</dd></div>
                <div><dt>Source</dt><dd>{result.requirements.extraction_source === "gemini" ? "Structured AI extraction" : "Deterministic preview"}</dd></div>
              </dl>
              <div className="review-actions">
                <p>Recommendation is advisory. Confirm with accountable delivery leadership.</p>
                <button onClick={() => void submitReview("approved")} className="approve-button" disabled={reviewState !== null}>Approve team <b>↗</b></button>
                <button onClick={() => void submitReview("needs_changes")} className="revise-button" disabled={reviewState !== null}>Request revision</button>
                {reviewState && <span className="review-confirmation">Decision recorded: {reviewState === "approved" ? "approved" : "revision requested"}.</span>}
              </div>
            </>
          ) : (
            <p className="review-empty">Human approval stays inactive until a proposed team is backed by recorded constraints.</p>
          )}
        </aside>
      </section>

      <footer className="system-footer">
        <span>Rules first</span><i />
        <span>Semantic retrieval second</span><i />
        <span>Human decision always</span>
      </footer>
    </main>
  );
}


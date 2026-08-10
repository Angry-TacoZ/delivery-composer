import { useEffect, useMemo, useState } from "react";

import { composeTeam, fetchDemoBrief, recordReview } from "./api";
import type { ComposeResponse, ReviewResponse, TeamAssignment } from "./types";

const FALLBACK_BRIEF = `Build a three-person delivery team for a critical-infrastructure resilience programme.
The client needs a security-first discovery and implementation plan covering zero trust,
cloud transformation, data governance, and an AI-assisted security operations use case.
The engagement starts in four weeks and requires SC-cleared consultants with public-sector
or regulated-infrastructure experience.`;

const IDEAL_STAGES = [
  { name: "Identify", detail: "Environment, stakeholders & impact" },
  { name: "Define", detail: "Roles, constraints & delivery path" },
  { name: "Execute", detail: "Eligible team composed with pace" },
  { name: "Assure", detail: "Evidence, security & validation" },
  { name: "Learn", detail: "Decision and feedback captured" },
] as const;

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
          <span>{percent(assignment.semantic_score)} alignment</span>
          <i style={{ "--score": assignment.semantic_score } as React.CSSProperties} />
        </span>
        <span className={allChecksPass ? "verified" : "exception"}>{allChecksPass ? "Verified" : "Review"}</span>
        <span className="expand-label">{open ? "Close evidence" : "View evidence"}</span>
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
  const [reviewState, setReviewState] = useState<ReviewResponse | null>(null);
  const [reviewNotes, setReviewNotes] = useState("");

  useEffect(() => {
    void fetchDemoBrief().then(setBrief).catch(() => undefined);
  }, []);

  const processLabel = useMemo(() => {
    if (result?.retrieval_mode === "postgres_pgvector") return "PostgreSQL + pgvector";
    return "Deterministic preview";
  }, [result]);

  const idealStageStates = useMemo(() => IDEAL_STAGES.map((_, index) => {
    if (reviewState) return "complete";
    if (result) return index < 3 ? "complete" : index === 3 ? "active" : "queued";
    if (isRunning) return index === 0 ? "complete" : index === 1 ? "active" : "queued";
    return index === 0 ? "active" : "queued";
  }), [isRunning, result, reviewState]);

  async function runComposition() {
    setIsRunning(true);
    setError(null);
    setReviewState(null);
    setReviewNotes("");
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
      setReviewState(await recordReview(result.run_id, status, reviewNotes.trim()));
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Review could not be saved.");
    }
  }

  return (
    <main className="site-shell">
      <section className="hero" aria-labelledby="page-title">
        <header className="masthead">
          <a className="wordmark" href="/" aria-label="Delivery Composer home">Delivery Composer</a>
          <div className="masthead-meta">
            <span>Concept for C86</span>
            <span>Synthetic data only</span>
          </div>
          <span className="edition">MVP / 01</span>
        </header>

        <div className="hero-layout">
          <div className="hero-title">
            <p className="eyebrow">Delivery intelligence</p>
            <h1 id="page-title">Compose the team.<br /><em>Keep the evidence.</em></h1>
          </div>
          <div className="hero-statement">
            <p>Turn an unstructured client brief into a defensible delivery-team recommendation—without turning AI into the decision maker.</p>
            <span>Rules first / Retrieval second / Human decision always</span>
          </div>
        </div>

        <ol className="method-strip" aria-label="C86 IDEAL delivery cycle">
          {IDEAL_STAGES.map((stage, index) => {
            const stageState = idealStageStates[index];
            return (
              <li key={stage.name} className={stageState} aria-current={stageState === "active" ? "step" : undefined}>
                <span className="stage-number">0{index + 1}</span>
                <span className="stage-copy"><strong>{stage.name}</strong><small>{stage.detail}</small></span>
                <span className="stage-state">{stageState === "complete" ? "Complete" : stageState === "active" ? "Active" : "Queued"}</span>
              </li>
            );
          })}
        </ol>
      </section>

      <section className="workbench" aria-label="Delivery team composition workspace">
        <header className="section-intro">
          <div>
            <p className="section-number">01 / Identify · 02 / Define · 03 / Execute</p>
            <h2>From client need to accountable recommendation.</h2>
          </div>
          <p>The system separates deterministic constraints from semantic relevance, then shows the evidence a delivery leader needs to challenge the result.</p>
        </header>

        <div className="composer-grid">
          <section className="brief-pane">
            <div className="pane-heading">
              <span>Identify / Client brief</span>
              <button onClick={() => setBrief(FALLBACK_BRIEF)} className="text-button">Restore sample</button>
            </div>
            <label htmlFor="client-brief">Engagement requirements</label>
            <textarea
              id="client-brief"
              value={brief}
              onChange={(event) => setBrief(event.target.value)}
              maxLength={1600}
            />
            <div className="brief-meta">
              <span>{brief.length} / 1600 characters</span>
              <span>Unstructured input</span>
            </div>
            <button className="compose-button" onClick={runComposition} disabled={isRunning || brief.trim().length < 40}>
              {isRunning ? "Composing evidence…" : "Compose delivery team"}
            </button>
            <p className="action-note">Runs against synthetic consultant profiles for this demonstration.</p>
            {error && <p className="error-message" role="alert">{error}</p>}
          </section>

          <section className="recommendation-pane" aria-live="polite">
            <div className="pane-heading">
              <span>Execute / Recommended composition</span>
              <span className="mode-label">{result ? processLabel : "Awaiting brief"}</span>
            </div>

            {!result ? (
              <div className="empty-state">
                <p className="empty-kicker">Ready for analysis</p>
                <p>Run the sample brief to inspect the proposed team, hard-constraint checks, and source evidence.</p>
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
        </div>
      </section>

      <section className="review-section" aria-label="Human review">
        <header className="review-heading">
          <p className="section-number">04 / Assure · 05 / Learn</p>
          <h2>Assure the outcome. Learn from the decision.</h2>
        </header>

        {result ? (
          <div className="review-grid">
            <dl className="requirements-list">
              <div><dt>Defined roles</dt><dd>{result.requirements.requested_roles.join(" · ")}</dd></div>
              <div><dt>Required skills</dt><dd>{result.requirements.required_skills.join(" · ")}</dd></div>
              <div><dt>Minimum clearance</dt><dd>{result.requirements.minimum_clearance.toUpperCase()}</dd></div>
              <div><dt>Requirement source</dt><dd>{result.requirements.extraction_source === "gemini" ? "Structured AI extraction" : "Deterministic preview"}</dd></div>
            </dl>
            <div className="review-actions">
              <p>Recommendation is advisory. Confirm fit, availability, and accountability with delivery leadership.</p>
              <label className="review-notes-label" htmlFor="review-notes">
                Learn / Review notes <span>Optional</span>
              </label>
              <textarea
                id="review-notes"
                className="review-notes"
                value={reviewNotes}
                onChange={(event) => setReviewNotes(event.target.value)}
                maxLength={600}
                disabled={reviewState !== null}
                placeholder="Capture a lesson, missing capability, or reason for the decision."
              />
              <div className="review-notes-meta">
                <span>{reviewNotes.length} / 600</span>
                <span>{result.retrieval_mode === "postgres_pgvector" ? "Stored with the run" : "Current API session"}</span>
              </div>
              <div className="decision-buttons">
                <button onClick={() => void submitReview("approved")} className="approve-button" disabled={reviewState !== null}>Approve proposed team</button>
                <button onClick={() => void submitReview("needs_changes")} className="revise-button" disabled={reviewState !== null}>Request revision</button>
              </div>
              {reviewState && (
                <span className="review-confirmation">
                  {reviewState.status === "approved" ? "Team approved" : "Revision requested"}. Feedback stored {reviewState.persistence_mode === "postgres" ? "in PostgreSQL" : "for this API session"}.
                </span>
              )}
            </div>
          </div>
        ) : (
          <p className="review-empty">Human approval remains inactive until the recommendation is backed by recorded constraints and evidence.</p>
        )}
      </section>

      <footer className="site-footer">
        <span>Delivery Composer</span>
        <span>Evidence-backed staffing intelligence</span>
        <span>Private MVP / Synthetic data</span>
      </footer>
    </main>
  );
}

import { useEffect, useMemo, useRef, useState } from "react";

import { composeTeam, fetchDemoBriefs, recordReview } from "./api";
import type { CandidateOption, ComposeResponse, DemoBrief, ReviewResponse, TeamAssignment, TeamOverride } from "./types";

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

function AssignmentRow({
  assignment,
  index,
  selectedOption,
  onSelect,
  disabled,
}: {
  assignment: TeamAssignment;
  index: number;
  selectedOption: CandidateOption;
  onSelect: (option: CandidateOption) => void;
  disabled: boolean;
}) {
  const [open, setOpen] = useState(index === 0);
  const [compareOpen, setCompareOpen] = useState(false);
  const allChecksPass = selectedOption.hard_constraints.every((check) => check.passed);
  const isOverridden = selectedOption.consultant.id !== assignment.consultant.id;

  return (
    <article className={`assignment ${open ? "is-open" : ""} ${isOverridden ? "is-overridden" : ""}`}>
      <button className="assignment-trigger" onClick={() => setOpen((value) => !value)} aria-expanded={open}>
        <span className="role-index">0{index + 1}</span>
        <span className="assignment-primary">
          <strong>{assignment.role_on_team}</strong>
          <span>{selectedOption.consultant.name} · {selectedOption.consultant.seniority}</span>
        </span>
        <span className="score-block" aria-label={`${percent(selectedOption.semantic_score)} semantic alignment`}>
          <span>{percent(selectedOption.semantic_score)} alignment</span>
          <i style={{ "--score": selectedOption.semantic_score } as React.CSSProperties} />
        </span>
        <span className={allChecksPass ? "verified" : "exception"}>
          {isOverridden ? "Human override" : allChecksPass ? "Verified" : "Review"}
        </span>
        <span className="expand-label">{open ? "Close evidence" : "View evidence"}</span>
      </button>
      {open && (
        <div className="assignment-expanded">
          <div className="assignment-detail">
            <div className="evidence-copy">
              <p>{selectedOption.explanation}</p>
              <span className="evidence-label">Positive evidence</span>
              <ul>
                {selectedOption.consultant.evidence.map((evidence) => <li key={evidence}>{evidence}</li>)}
              </ul>
              <span className="evidence-label consideration-label">Considerations</span>
              <ul className="consideration-list">
                {selectedOption.consultant.considerations.map((item) => <li key={item}>{item}</li>)}
              </ul>
            </div>
            <dl className="constraint-list">
              {selectedOption.hard_constraints.map((check) => (
                <div key={check.label}>
                  <dt>{check.label}</dt>
                  <dd className={check.passed ? "pass" : "fail"}>{check.evidence}</dd>
                </div>
              ))}
            </dl>
          </div>
          <button
            type="button"
            className="compare-trigger"
            onClick={() => setCompareOpen((value) => !value)}
            aria-expanded={compareOpen}
          >
            <span>Compare candidates</span>
            <span>{assignment.alternatives.length} options · {compareOpen ? "Close" : "Open ledger"}</span>
          </button>
          {compareOpen && (
            <div className="candidate-ledger" aria-label={`Candidate options for ${assignment.role_on_team}`}>
              {assignment.alternatives.map((option, optionIndex) => {
                const isSelected = selectedOption.consultant.id === option.consultant.id;
                const isRecommendation = assignment.consultant.id === option.consultant.id;
                const passes = option.hard_constraints.every((check) => check.passed);
                return (
                  <div className={`candidate-option ${isSelected ? "is-selected" : ""}`} key={option.consultant.id}>
                    <span className="candidate-option-index">0{optionIndex + 1}</span>
                    <div className="candidate-option-summary">
                      <strong>{option.consultant.name}</strong>
                      <span>{option.consultant.seniority} · {percent(option.semantic_score)} alignment</span>
                      <small>+ {option.consultant.evidence[0]}</small>
                      <small className="candidate-concern">– {option.consultant.considerations[0]}</small>
                    </div>
                    <div className="candidate-option-decision">
                      <span className={passes ? "candidate-eligible" : "candidate-exception"}>
                        {passes ? "Eligible" : "Exception visible"}
                      </span>
                      <button type="button" onClick={() => onSelect(option)} disabled={disabled || isSelected}>
                        {isSelected
                          ? "Current"
                          : isRecommendation
                            ? "Restore recommendation"
                            : passes
                              ? "Use candidate"
                              : "Select with exception"}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
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
  const [isReviewSaving, setIsReviewSaving] = useState(false);
  const reviewSaveInFlight = useRef(false);
  const [demoBriefs, setDemoBriefs] = useState<DemoBrief[]>([]);
  const [selectedDemoBrief, setSelectedDemoBrief] = useState<DemoBrief | null>(null);
  const [briefSourceEdited, setBriefSourceEdited] = useState(false);
  const [isBriefLibraryOpen, setIsBriefLibraryOpen] = useState(false);
  const [briefLibraryError, setBriefLibraryError] = useState<string | null>(null);
  const [teamOverrides, setTeamOverrides] = useState<Record<string, CandidateOption>>({});

  useEffect(() => {
    void fetchDemoBriefs()
      .then((briefs) => {
        setDemoBriefs(briefs);
        const firstBrief = briefs[0];
        if (firstBrief) {
          setSelectedDemoBrief(firstBrief);
          setBrief(firstBrief.brief);
        }
      })
      .catch(() => setBriefLibraryError("The synthetic brief library could not be loaded."));
  }, []);

  const overrideCount = Object.keys(teamOverrides).length;

  const reviewOverrides = useMemo<TeamOverride[]>(() => {
    if (!result) return [];
    return result.assignments.flatMap((assignment) => {
      const selected = teamOverrides[assignment.role_on_team];
      if (!selected) return [];
      return [{
        role: assignment.role_on_team,
        original_consultant_id: assignment.consultant.id,
        selected_consultant_id: selected.consultant.id,
      }];
    });
  }, [result, teamOverrides]);

  const processLabel = useMemo(() => {
    const mode = result?.retrieval_mode === "postgres_pgvector" ? "PostgreSQL + pgvector" : "Deterministic preview";
    return overrideCount > 0 ? `${mode} · ${overrideCount} human ${overrideCount === 1 ? "override" : "overrides"}` : mode;
  }, [overrideCount, result]);

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
    setTeamOverrides({});
    try {
      setResult(await composeTeam(brief));
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Analysis failed.");
    } finally {
      setIsRunning(false);
    }
  }

  function resetEvaluation() {
    setResult(null);
    setReviewState(null);
    setReviewNotes("");
    setTeamOverrides({});
  }

  function restoreSample() {
    const firstBrief = demoBriefs[0];
    setBrief(firstBrief?.brief ?? FALLBACK_BRIEF);
    setSelectedDemoBrief(firstBrief ?? null);
    setBriefSourceEdited(false);
    setIsBriefLibraryOpen(false);
    setError(null);
    resetEvaluation();
  }

  function editBrief(nextBrief: string) {
    setBrief(nextBrief);
    if (selectedDemoBrief) setBriefSourceEdited(true);
    setError(null);
    resetEvaluation();
  }

  function chooseDemoBrief(demoBrief: DemoBrief) {
    setBrief(demoBrief.brief);
    setSelectedDemoBrief(demoBrief);
    setBriefSourceEdited(false);
    setIsBriefLibraryOpen(false);
    setError(null);
    resetEvaluation();
  }

  function selectCandidate(assignment: TeamAssignment, option: CandidateOption) {
    setTeamOverrides((current) => {
      const next = { ...current };
      if (option.consultant.id === assignment.consultant.id) {
        delete next[assignment.role_on_team];
      } else {
        next[assignment.role_on_team] = option;
      }
      return next;
    });
    setReviewState(null);
    setError(null);
  }

  async function submitReview(status: "approved" | "needs_changes") {
    if (!result || reviewState || reviewSaveInFlight.current) return;

    reviewSaveInFlight.current = true;
    setIsReviewSaving(true);
    setError(null);
    try {
      setReviewState(await recordReview(result.run_id, status, reviewNotes.trim(), reviewOverrides));
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Review could not be saved.");
    } finally {
      reviewSaveInFlight.current = false;
      setIsReviewSaving(false);
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
              <button onClick={restoreSample} className="text-button">Restore sample</button>
            </div>
            <div className="brief-source-row">
              <div className="brief-source-copy" id="brief-source-note">
                <span>Brief source</span>
                <strong>{selectedDemoBrief ? selectedDemoBrief.title : "Manual text"}</strong>
                <small>
                  {selectedDemoBrief
                    ? `${selectedDemoBrief.reference} · ${selectedDemoBrief.sector}${briefSourceEdited ? " · edited" : ""}`
                    : "Paste a concise brief or choose a synthetic scenario."}
                </small>
              </div>
              <button
                className="brief-library-trigger"
                type="button"
                onClick={() => setIsBriefLibraryOpen((open) => !open)}
                disabled={isRunning}
                aria-expanded={isBriefLibraryOpen}
                aria-controls="demo-brief-library"
              >
                {isBriefLibraryOpen ? "Close library" : "Choose demo brief"}
              </button>
            </div>
            {isBriefLibraryOpen && (
              <div className="brief-library" id="demo-brief-library">
                <div className="brief-library-heading">
                  <span>Simulated client briefs</span>
                  <span>{demoBriefs.length} scenarios</span>
                </div>
                {briefLibraryError ? (
                  <p className="brief-library-error" role="alert">{briefLibraryError}</p>
                ) : demoBriefs.map((demoBrief, index) => (
                  <button
                    type="button"
                    className="brief-library-item"
                    key={demoBrief.slug}
                    onClick={() => chooseDemoBrief(demoBrief)}
                    disabled={isRunning}
                    aria-pressed={selectedDemoBrief?.slug === demoBrief.slug}
                  >
                    <span className="brief-library-index">0{index + 1}</span>
                    <span className="brief-library-copy">
                      <strong>{demoBrief.title}</strong>
                      <small>{demoBrief.reference} · {demoBrief.sector}</small>
                    </span>
                    <span className="brief-library-state">
                      {selectedDemoBrief?.slug === demoBrief.slug ? "Selected" : "Load brief"}
                    </span>
                  </button>
                ))}
              </div>
            )}
            <label htmlFor="client-brief">Engagement requirements</label>
            <textarea
              id="client-brief"
              value={brief}
              onChange={(event) => editBrief(event.target.value)}
              maxLength={1600}
              disabled={isRunning}
              aria-describedby="brief-source-note"
            />
            <div className="brief-meta">
              <span>{brief.length} / 1600 characters</span>
              <span>Unstructured input</span>
            </div>
            <button className="compose-button" onClick={runComposition} disabled={isRunning || brief.trim().length < 40}>
              {isRunning ? "Composing evidence…" : "Compose delivery team"}
            </button>
            <p className="action-note">Meeting mode uses synthetic briefs. A greenlit workflow can accept searchable PDFs through the same validated evaluation contract.</p>
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
                  {result.assignments.map((assignment, index) => (
                    <AssignmentRow
                      key={assignment.consultant.id}
                      assignment={assignment}
                      index={index}
                      selectedOption={teamOverrides[assignment.role_on_team] ?? assignment}
                      onSelect={(option) => selectCandidate(assignment, option)}
                      disabled={reviewState !== null || isReviewSaving}
                    />
                  ))}
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
              {overrideCount > 0 && (
                <p className="override-summary" role="status">
                  {overrideCount} human {overrideCount === 1 ? "override" : "overrides"} recorded for review. Constraint exceptions remain visible.
                </p>
              )}
              <label className="review-notes-label" htmlFor="review-notes">
                Learn / Review notes <span>Optional</span>
              </label>
              <textarea
                id="review-notes"
                className="review-notes"
                value={reviewNotes}
                onChange={(event) => setReviewNotes(event.target.value)}
                maxLength={600}
                disabled={reviewState !== null || isReviewSaving}
                placeholder="Capture a lesson, missing capability, or reason for the decision."
              />
              <div className="review-notes-meta">
                <span>{reviewNotes.length} / 600</span>
                <span>{result.retrieval_mode === "postgres_pgvector" ? "Stored with the run" : "Current API session"}</span>
              </div>
              <div className="decision-buttons" aria-busy={isReviewSaving}>
                <button onClick={() => void submitReview("approved")} className="approve-button" disabled={reviewState !== null || isReviewSaving}>Approve proposed team</button>
                <button onClick={() => void submitReview("needs_changes")} className="revise-button" disabled={reviewState !== null || isReviewSaving}>Request revision</button>
              </div>
              {isReviewSaving && <span className="review-saving" role="status">Saving decision...</span>}
              {reviewState && (
                <span className="review-confirmation">
                  {reviewState.status === "approved" ? "Team approved" : "Revision requested"}. Feedback stored {reviewState.persistence_mode === "postgres" ? "in PostgreSQL" : "for this API session"}{reviewState.override_count > 0 ? ` with ${reviewState.override_count} human ${reviewState.override_count === 1 ? "override" : "overrides"}` : ""}.
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

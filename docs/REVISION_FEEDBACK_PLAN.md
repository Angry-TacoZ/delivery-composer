# Revision feedback loop plan

## Outcome

Replace the current terminal `Request revision` state with a real, traceable feedback loop. A reviewer records actionable feedback, re-evaluates from that feedback, and can compare the new result with the preserved prior recommendation. Submitted decisions always expose a next action.

## Product direction

- **Visual thesis:** preserve the sparse graphite review lane; use one compact decision-state rail and an inline result-delta disclosure instead of new cards or dashboard chrome.
- **Content plan:** actionable review note, decision, saved provenance, re-evaluation action, and prior-versus-current result delta.
- **Interaction thesis:** submission changes the available actions rather than freezing the surface; re-evaluation transitions back through Define and Execute; prior-result disclosure expands in place and respects reduced motion.

## Workflow

1. Approval notes remain optional; revision feedback requires at least ten non-whitespace characters.
2. `Approve proposed team` and `Request revision` record a real review through FastAPI.
3. A recorded approval exposes `Change decision` and `Start new evaluation`.
4. A recorded revision exposes `Change decision` and `Re-evaluate with feedback`.
5. Re-evaluation sends the prior run identifier and bounded revision feedback to FastAPI.
6. FastAPI requires that feedback to match the recorded review notes and uses the stored notes as the authoritative analysis input.
7. The new composition records its parent run and applied feedback, while the browser preserves the prior response for a compact role/team delta.
8. In deterministic mode, explicit role-replacement feedback changes the requested role set; live mode supplies the same bounded context to Gemini and pgvector retrieval.

## Trust boundaries

- The browser supplies an untrusted prior run ID and revision text.
- FastAPI validates text shape and length, verifies that the prior run exists, requires a recorded `needs_changes` review, rejects mismatched submitted feedback, and uses the persisted review notes for composition.
- PostgreSQL stores the parent run and revision feedback server-side when live mode is enabled.
- Paid-model credentials remain server-only; deterministic portfolio mode makes no external calls.

## Acceptance criteria

- [x] Empty or short revision feedback is rejected clearly in the client and API.
- [x] A revision decision no longer leaves disabled controls as the only visible actions.
- [x] `Change decision` permits a corrected approval or revision and overwrites the run's current review safely.
- [x] `Re-evaluate with feedback` creates a new run linked to the reviewed parent run.
- [x] Submitted revision feedback must match the persisted `needs_changes` notes; mismatches are rejected before analysis.
- [x] Explicit deterministic role-replacement feedback materially changes the resulting composition.
- [x] The prior result remains available through an interactive result-delta disclosure.
- [x] Approval exposes a working new-evaluation path.
- [x] Duplicate submissions remain guarded while a request is in flight.
- [x] API tests, frontend build, browser workflow, secret scan, and canonical verifier pass.
- [x] PR CI passes on the pushed implementation commit.

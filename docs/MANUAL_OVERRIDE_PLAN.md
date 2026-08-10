# Candidate comparison and manual override plan

## Outcome

Expand the synthetic roster from five to fifteen profiles: three candidates for each role used by the demo scenarios. Let a delivery leader compare evidence and trade-offs, replace a recommendation, and carry the explicit human override into the review record.

## Product direction

- **Visual thesis:** extend the graphite operations workbench with a compact comparison ledger, not candidate cards or recruitment UI.
- **Content plan:** recommended consultant first, three role-specific options second, auditable score arithmetic and trade-offs third, explicit human decision last.
- **Interaction thesis:** opening a person reveals the two runners-up and their scores in place; choosing Compare opens a focused current-versus-challenger overlay with RPG-style stat deltas and attributable point rows; an override updates the selected team and leaves a visible decision marker.

## Synthetic roster

| Role | Candidate focus | Candidate focus | Candidate focus |
| --- | --- | --- | --- |
| Delivery Lead | public-sector recovery | financial-services governance | media programme recovery |
| Security Architect | critical-infrastructure zero trust | high-assurance architecture | financial/media cloud security |
| Data & AI Engineer | governed security retrieval | financial-services AI delivery | public-sector data assurance |
| Cloud Engineer | media platform automation | regulated cloud foundations | transport/financial platform delivery |
| Security Consultant | high-assurance SOC transformation | media/financial incident response | critical-infrastructure zero trust |

Every profile remains fictional and includes verified-style evidence plus explicit considerations such as sector depth, clearance, availability, or capability gaps.

## Decision rules

1. The server returns exactly three candidates for every requested role.
2. The default recommendation must satisfy clearance and availability; exact role matches outrank unrelated profiles.
3. Failed constraints remain visible in the comparison rather than being hidden.
4. A human may compare the current assignment with either runner-up in a focused dialog, then select another candidate, including one with a visible exception; the UI must never relabel that exception as verified.
5. Overrides record the role, original recommendation, and selected consultant with the final review.
6. Changing the brief or composing again clears all prior overrides.
7. Deterministic alignment is auditable as `58 base + 8 per required-capability match + 5 per preferred-sector match`, capped at 97.
8. Clearance and availability remain hard gates rather than score deductions; considerations remain decision context unless a real scoring rule uses them.

## Backend-ready contract

- Candidate options and considerations are returned by FastAPI, not invented in the browser.
- Every score component is computed and returned by FastAPI; the browser may not reverse-engineer or invent point attribution.
- Demo reviews validate override identifiers against the stored composition run.
- PostgreSQL review storage retains the same bounded override payload when the live path is enabled later.
- Gemini remains unable to change hard-constraint results or candidate identifiers.

## Acceptance criteria

- [x] Fifteen synthetic profiles exist: three for each of five role families.
- [x] Every returned role has exactly three distinct options with positives and considerations.
- [x] The recommended option is derived from constraints and deterministic scoring.
- [x] Opening evidence shows both runners-up and their alignment scores.
- [x] Compare opens an accessible current-versus-challenger dialog with score delta, evidence, considerations, and constraint states.
- [x] A user can make or restore a manual override from the comparison dialog.
- [x] Every displayed deterministic total equals the sum of its returned score components.
- [x] The comparison explains the candidate delta through side-by-side attributable point rows.
- [x] Narrative considerations and hard-gate exceptions are explicitly labeled as not scored.
- [x] The selected assignment, summary state, and review payload reflect the override.
- [x] Invalid or fabricated override identifiers are rejected server-side.
- [x] Recomposition clears overrides.
- [x] Keyboard, reduced-motion, loading, and responsive behavior remain intact.
- [x] API tests, frontend build, secret scan, canonical verifier, and browser workflow pass.

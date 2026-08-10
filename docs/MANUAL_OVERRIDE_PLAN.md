# Candidate comparison and manual override plan

## Outcome

Expand the synthetic roster from five to fifteen profiles: three candidates for each role used by the demo scenarios. Let a delivery leader compare evidence and trade-offs, replace a recommendation, and carry the explicit human override into the review record.

## Product direction

- **Visual thesis:** extend the graphite operations workbench with a compact comparison ledger, not candidate cards or recruitment UI.
- **Content plan:** recommended consultant first, three role-specific options second, visible trade-offs third, explicit human decision last.
- **Interaction thesis:** evidence expands in place; candidate rows reveal comparison detail; an override updates the selected team and leaves a visible decision marker.

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
4. A human may select another candidate, including one with a visible exception, but the UI must never relabel that exception as verified.
5. Overrides record the role, original recommendation, and selected consultant with the final review.
6. Changing the brief or composing again clears all prior overrides.

## Backend-ready contract

- Candidate options and considerations are returned by FastAPI, not invented in the browser.
- Demo reviews validate override identifiers against the stored composition run.
- PostgreSQL review storage retains the same bounded override payload when the live path is enabled later.
- Gemini remains unable to change hard-constraint results or candidate identifiers.

## Acceptance criteria

- [ ] Fifteen synthetic profiles exist: three for each of five role families.
- [ ] Every returned role has exactly three distinct options with positives and considerations.
- [ ] The recommended option is derived from constraints and deterministic scoring.
- [ ] A user can compare all three options and make a manual override.
- [ ] The selected assignment, summary state, and review payload reflect the override.
- [ ] Invalid or fabricated override identifiers are rejected server-side.
- [ ] Recomposition clears overrides.
- [ ] Keyboard, reduced-motion, loading, and responsive behavior remain intact.
- [ ] API tests, frontend build, secret scan, canonical verifier, and browser workflow pass.

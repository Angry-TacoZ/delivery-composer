# Goal

Maintain Delivery Composer as a polished, public portfolio application demonstrating governed delivery-team composition from synthetic client briefs.

# Current status

The deterministic React and FastAPI workflow is implemented, tested, and hosted. It uses fictional profiles and synthetic briefs, performs no paid-model calls, and retains review state only for the API process lifetime. PostgreSQL/pgvector and Gemini remain disabled, unverified extension points.

# Decisions

- Declared scope: public, low-risk portfolio demo using synthetic data only.
- Product identity is vendor- and consultancy-neutral.
- Workflow: Identify, Define, Execute, Assure, Learn.
- Hard constraints remain separate from attributable alignment scoring.
- Recommendations are advisory and require human approval.
- Browser code receives no database or model-provider credentials.
- Public deployment remains capped at one Cloud Run instance with a budget-alert acknowledgement.

# Changed files

- `README.md`, `LICENSE`, and public documentation: generalized portfolio framing and clear reuse terms.
- `web/src/App.tsx` and `web/src/styles.css`: neutral product copy and asset naming.
- `scripts/verify.ps1` and `scripts/deploy-demo.ps1`: repository-owned, machine-independent verification.
- `docs/PORTFOLIO_DEMO.md`, `docs/DELIVERY_WORKFLOW.md`, and `docs/VISUAL_DIRECTION.md`: reusable product, workflow, and visual rationale.
- `.env.example` and `api/tests/test_main.py`: accurate public origins and configuration-isolated health-contract coverage.

# Verification

- Repository-owned verifier: Ruff, 25 API tests, and frontend production build passed.
- Canonical verifier: passed for the declared public-low-risk scope.
- Predeployment secret/API exposure scan: passed.
- Frontend production dependency audit: zero vulnerabilities.
- Generalization scan: no tailored-company, interview, private-MVP, local-username, or stale session-copy references found in current repository text.
- Browser QA: neutral identity, documented synthetic brief, composition, eligible labels, temporary-session copy, desktop/mobile rendering, and zero console warnings or errors passed.
- Updated public screenshots were visually inspected; obsolete company-specific screenshots were removed.
- PR #12 verification: Ruff, 25 API tests, frontend production build, and predeployment secret/API exposure scan passed after isolating the health test from ambient credentials.
- CI must pass on the PR head before merge.

# Next task

Deploy the reviewed neutral `main` build so the hosted site matches the repository's vendor-neutral portfolio framing.

# Risks or blockers

- The hosted path is a deterministic demonstration, not a production staffing or hiring system.
- Do not submit real client, employee, consultant, candidate, regulated, or confidential data.
- PostgreSQL/pgvector and Gemini are documented architecture seams, not verified hosted capabilities.
- The hosted site currently serves an older bundle with tailored-company copy. Deploying the reviewed neutral build is required before presenting the live URL to other consulting firms.
- Earlier Git history retains the original tailored design rationale; no credentials were found, but removing that historical record would require a separately authorized history rewrite or a fresh public repository.

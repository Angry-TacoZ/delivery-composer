# Goal

Ship a hosted, polished Delivery Composer MVP for a short consulting conversation. The app recommends a synthetic delivery team from a client brief and makes constraints, evidence, and the human-review boundary visible.

# Current status

The private GitHub repository is published at `Angry-TacoZ/delivery-composer`. PR #1 through PR #5 are merged; PR #5's squash commit is `73eb3b9c83881cbd159656f3d3e3f19478979983`. Draft PR #6 now targets `main` for Americas-facing copy localization.

The local MVP is implemented and fully verified in deterministic preview mode. Firebase project `composermvp` exists and Aiven PostgreSQL service `delivery-composer-db` is running. Today's build intentionally does not require or initialize PostgreSQL or Gemini. The live PostgreSQL/pgvector + Gemini path remains an explicit post-validation upgrade until server-side secrets and Google Cloud billing are ready.

# Decisions

- Public-low-risk application boundary with synthetic data only; the GitHub repository remains private for the meeting.
- React on Firebase Hosting; FastAPI on Cloud Run; Aiven PostgreSQL with pgvector; Gemini called only from the backend.
- Database URI and Gemini key are server-only secrets. They may not enter the browser build, Git history, screenshots, or this handoff.
- Firebase Hosting rewrites `/api/**` to Cloud Run service `delivery-composer-api` in `us-east1`.
- UI follows C86's graphite editorial language without using its logo or implying endorsement.
- The generated raster trajectory field is animated by a slow transform layer and becomes still under reduced-motion preferences.
- Recommendations remain advisory: rules first, semantic retrieval second, human decision always.
- IDEAL is a stateful product workflow, not a decorative graphic: Identify, Define, Execute, Assure, and Learn map to actual composition and human-review behavior.
- Demo reviews are retained only for the API process lifetime and labeled `session`; configured live-path reviews are labeled `postgres`.
- Review submissions use an immediate in-flight guard, disable both decisions and notes while saving, and expose an accessible saving status to prevent rapid duplicate requests.
- Today's UI selects one of three backend-served synthetic briefs; the bounded, non-persistent PDF extraction endpoint remains tested but is intentionally not exposed until the workflow is greenlit.
- The deterministic preview now derives sector-specific roles, target dates, summaries, and ordered teams for critical-infrastructure, financial-services, and media/broadcast scenarios.
- `DEMO_MODE=true` now enforces adapter isolation even when credentials exist; `DEMO_MODE=false` fails fast unless both PostgreSQL and Gemini are configured.
- The brief library uses full-width editorial rows with explicit synthetic references and sectors; it does not imitate or claim a real upload.
- The synthetic roster contains three exact-role candidates for each of five role families. Hard-gate-eligible recommendations are presented first, while all alternatives retain visible positive evidence and considerations.
- Human overrides are advisory decisions, not constraint rewrites: clearance and availability exceptions remain visible, and review identifiers are validated against the stored composition run.
- Opening an assignment reveals both scored runners-up. Each runner opens a native current-versus-challenger comparison dialog with RPG-style score deltas, evidence, concerns, constraints, and the override action.
- Deterministic comparison scores are server-attributed as a 58-point exact-role baseline, 8 points per required-capability match, and 5 points per preferred-sector match. Narrative considerations and eligibility gates are explicitly not scored.
- Recorded decisions always expose a next action. Revision feedback must be actionable, is linked to a reviewed parent run, can alter deterministic role composition, and remains inspectable through a prior-result delta.
- Recorded review notes are authoritative for revisions: the server rejects browser-submitted feedback that differs from the stored `needs_changes` notes, then uses the stored value for analysis, lineage, and persistence.
- Meeting-facing synthetic briefs, candidate evidence, and generated PDF artifacts use American English because the audience is C86's President of the Americas; input parsing continues to accept UK and US sector spellings.

# Changed files

- `web/src/App.tsx` and `web/src/styles.css`: C86-aligned responsive workflow, evidence expansion, decision state, and animated trajectory field.
- `web/public/assets/c86-trajectory-field.png`: original text-free raster visual used by the hero and review section.
- `README.md`: meeting-ready product case study, architecture, setup, verification, and accurate demo boundary.
- `.github/workflows/ci.yml`: API lint/tests and web production build on pull requests and main.
- `docs/C86_VISUAL_ALIGNMENT.md`: planning-first acceptance criteria and completed checklist.
- `docs/IDEAL_ALIGNMENT.md`: planning-first methodology mapping and acceptance criteria for PR #2.
- `api/app/domain.py`, `api/app/repository.py`, `api/app/service.py`, and `api/app/main.py`: review provenance plus real in-process demo persistence.
- `api/tests/test_main.py`: review storage, provenance, and unknown-run coverage.
- `web/src/App.tsx`, `web/src/api.ts`, `web/src/types.ts`, and `web/src/styles.css`: five IDEAL stages, state transitions, bounded notes, and persistence-specific confirmation without changing the approved visual direction.
- `api/app/pdf_briefs.py` and `/api/extract-brief`: bounded server-side PDF validation and extraction.
- `api/app/mock_briefs.py`, `scripts/generate_mock_briefs.py`, and `output/pdf/`: shared synthetic scenarios and polished one-page artifacts.
- `api/app/providers.py` and `api/app/repository.py`: input-dependent roles, sectors, dates, summaries, and availability checks.
- `api/app/pdf_briefs.py`, `web/src/api.ts`, and shared types preserve the bounded PDF adapter and editable-text contract for a future exposed upload flow.
- `docs/PDF_BRIEF_INGESTION.md`, `docs/pdf-qa.md`, and `docs/screenshots/delivery-composer-pdf-evaluation.png`: plan and visual/functional evidence for PR #3.
- `docs/TODAYS_DEMO.md`: explicit meeting scope, architecture boundary, visual/content/interaction thesis, and 15-minute walkthrough.
- `api/app/config.py`, `api/app/providers.py`, and `api/app/service.py`: explicit deterministic/live execution switch with fail-fast live configuration.
- `api/app/domain.py`, `api/app/main.py`, `web/src/api.ts`, and `web/src/types.ts`: typed synthetic brief-library contract shared across the API boundary.
- `web/src/App.tsx` and `web/src/styles.css`: accessible inline demo brief selector replacing the meeting UI file picker.
- `docs/design-qa.md` and `docs/screenshots/`: same-size visual comparison record plus desktop/mobile evidence.
- `docs/MANUAL_OVERRIDE_PLAN.md`: planning-first comparison, decision-rule, and verification contract for PR #4.
- `api/app/demo_data.py`, `api/app/domain.py`, `api/app/repository.py`, `api/app/migrations.py`, and `api/app/seed.py`: fifteen fictional profiles, three-option assignments, validated override payloads, and PostgreSQL-ready persistence.
- `web/src/App.tsx`, `web/src/api.ts`, `web/src/types.ts`, and `web/src/styles.css`: scored runners-up, accessible comparison dialog, visible exception selection, override provenance, and review submission.
- `api/app/domain.py` and `api/app/repository.py`: typed score components and auditable deterministic arithmetic returned with every candidate option.
- `docs/REVISION_FEEDBACK_PLAN.md`: behavior, trust-boundary, and acceptance contract for PR #5.
- `api/app/domain.py`, `api/app/providers.py`, `api/app/service.py`, `api/app/repository.py`, and `api/app/migrations.py`: bounded revision context, parent-run validation, deterministic role replacement, and PostgreSQL-ready lineage.
- `api/app/service.py` and `api/app/repository.py`: server-authoritative revision feedback retrieval and exact-match enforcement across session and PostgreSQL repositories.
- `web/src/App.tsx`, `web/src/api.ts`, `web/src/types.ts`, and `web/src/styles.css`: actionable recorded-decision state, re-evaluation, corrected decisions, and interactive prior-result delta.
- `api/app/mock_briefs.py`, `api/app/demo_data.py`, `web/src/App.tsx`, and `output/pdf/`: Americas-localized synthetic briefs, candidate evidence, fallback copy, and regenerated demo artifacts.

# Verification

- Design QA: C86 reference and application capture compared together at 2048 × 1200; no P0, P1, or P2 findings.
- Animated trajectory field: computed transform changed across a 1.2-second observation; reduced-motion override is present.
- Browser workflow: compose, evidence expansion, and approve-review confirmation passed.
- IDEAL browser workflow: composition moved Assure active; revision and approval completed Learn; review notes and session provenance were visible.
- Responsive check: 390 × 844 viewport passed with no unintended horizontal overflow.
- Browser console: no warnings or errors during desktop or mobile primary workflow.
- Ruff: pass.
- Pytest: 24 passed; two dependency deprecation warnings on local Python 3.14.
- Frontend TypeScript/Vite production build: pass.
- npm production dependency audit: 0 vulnerabilities.
- Predeploy secret/API exposure scan: pass.
- Canonical verifier: pass with `PYTHONUTF8=1` on Windows.
- GitHub Actions on draft PR #2: API lint/tests pass; web production build pass.
- GitHub Actions on merged PR #3: API lint/tests pass; web production build pass.
- PDF parser tests: valid, MIME, extension, signature, malformed, oversized, encrypted, image-only, short, overlong, and page-limit cases pass.
- Actual PDF comparison: 1,054/985/997 extracted characters and three distinct ordered teams.
- Prior PDF adapter browser workflow: desktop and mobile upload/evaluate/error-recovery passed before the control was intentionally replaced by the synthetic meeting library.
- Review hardening browser check: a rapid double-click completed one approval state and left both decision controls and notes disabled.
- Deterministic-mode browser replay: compose, evidence, IDEAL completion, review notes, and session-provenance confirmation passed after adapter isolation changes.
- Execution-boundary tests: demo mode ignores configured live credentials; live mode rejects missing PostgreSQL or Gemini configuration.
- Demo-library browser check: three synthetic cases were visible with references and sectors; financial-services selection changed the brief, requirements, roles, scores, and ordered team without layout clipping at the inspected desktop viewport.
- Manual-override browser check: critical-infrastructure composition returned three Delivery Lead options; the higher-scoring ineligible candidate remained labeled with clearance and date exceptions, selection produced a visible human-override state, and approval confirmed one stored override.
- Override-reset browser check: restoring the sample and recomposing removed the human-override state.
- PR #4 canonical verifier: Ruff, 20 API tests, frontend production build, and predeploy secret/API exposure scan all passed on 2026-08-10.
- GitHub Actions on draft PR #4: API lint/tests and web production build pass.
- Comparison-dialog browser check: opening evidence exposed both scored runners-up; Priya opened against Theo with a `+8 pts` delta and two visible hard-constraint exceptions; Escape closed the dialog; selecting the challenger created the human-override state.
- Score-audit browser check: the `+8 pts` delta names required capabilities as its driver; Theo renders `58 + 8 + 0 = 66`, Priya renders `58 + 16 + 0 = 74`, and considerations plus eligibility gates are labeled not scored.
- Revision-loop browser check: empty feedback produced a clear validation error; a stored revision exposed working Change and Re-evaluate actions; role-replacement feedback swapped Data & AI Engineer for Cloud Engineer; prior-result disclosure showed both role deltas; approval exposed Change decision and Start new evaluation.
- PR #5 canonical verifier: Ruff, 25 API tests, frontend production build, and predeploy secret/API exposure scan pass on 2026-08-10 after revision-feedback trust-boundary hardening.
- Revision-feedback mismatch regression: a parent with recorded `needs_changes` notes rejects different submitted feedback with HTTP 422; the matching-feedback workflow remains green.
- GitHub Actions on draft PR #5: API lint/tests and web production build pass.
- Post-merge stack check: local `main` matches `origin/main` at PR #3's squash commit; rebased PR #4 and PR #5 are mergeable with passing GitHub Actions.
- PR #4 merge check: local `main` matches `origin/main` at `c876ea944b46876e9e5a71ba5d1a6511a6b0293e`; PR #5 was rebased onto that commit and retargeted to `main`.
- PR #5 merge check: local `main` matches `origin/main` at `73eb3b9c83881cbd159656f3d3e3f19478979983`; PR #6 was rebased onto that commit.
- PR #6 canonical verifier: Ruff, 25 API tests, frontend production build, and predeploy secret/API exposure scan pass on 2026-08-10.
- PR #6 rendered-copy check: critical-infrastructure and media briefs display `program`; the critical-infrastructure brief displays `modernize`. Historical Vite hot-reload errors from branch switching remained in the browser log, but a clean reload rendered correctly and the production build passed.

# Next task

1. Obtain external review for draft PR #6, address actionable feedback, and merge.
2. If the product direction is greenlit, enable the configured Aiven PostgreSQL/pgvector and Gemini adapters, then prove run, review, and revision persistence.
3. When ready to host: complete the documented billing, secret, migration, deployment, smoke-test, rollback, and custom-domain gates.

# Risks or blockers

- Readiness status: `NOT PRODUCTION-READY` for public hosting until billing, server-side secrets, live database/model verification, deployment smoke tests, and rollback checks are complete.
- Google Cloud CLI is not installed yet and Blaze billing must be linked before Cloud Run deployment.
- Public access is intentionally low-risk only: anonymous requests are bounded but not authenticated, and the rate limiter is per Cloud Run instance. Do not use real client or personnel data.
- The generated visual is C86-inspired concept art; it is not an official brand asset.
- PDF parsing is a demonstration boundary, not a production document-security pipeline: OCR, antivirus scanning, content disarm, parser isolation, and persistent document lifecycle controls are out of scope.
- The PostgreSQL migration, seed, vector ranking, and override upsert are implemented but not yet exercised against the live Aiven service; today's verified path remains deterministic session storage.
- Revision lineage and feedback columns are migration-ready but have not been applied to or exercised against the live Aiven service.

# Goal

Ship a hosted, polished Delivery Composer MVP for a short consulting conversation. The app recommends a synthetic delivery team from a client brief and makes constraints, evidence, and the human-review boundary visible.

# Current status

The private GitHub repository is published at `Angry-TacoZ/delivery-composer`. PR #1 was opened from a planning-only commit before implementation, externally reviewed with an `Approve` verdict, and squash-merged to `main` as `34edc84`. Draft PR #2 was also opened from a planning-only commit before implementation and now aligns the real workflow with C86's published IDEAL methodology.

The local MVP is implemented and fully verified in deterministic preview mode. Firebase project `composermvp` exists and Aiven PostgreSQL service `delivery-composer-db` is running. The live PostgreSQL/pgvector + Gemini path remains unconfigured until server-side secrets and Google Cloud billing are ready.

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
- `docs/design-qa.md` and `docs/screenshots/`: same-size visual comparison record plus desktop/mobile evidence.

# Verification

- Design QA: C86 reference and application capture compared together at 2048 × 1200; no P0, P1, or P2 findings.
- Animated trajectory field: computed transform changed across a 1.2-second observation; reduced-motion override is present.
- Browser workflow: compose, evidence expansion, and approve-review confirmation passed.
- IDEAL browser workflow: composition moved Assure active; revision and approval completed Learn; review notes and session provenance were visible.
- Responsive check: 390 × 844 viewport passed with no unintended horizontal overflow.
- Browser console: no warnings or errors during desktop or mobile primary workflow.
- Ruff: pass.
- Pytest: 8 passed; two dependency deprecation warnings on local Python 3.14.
- Frontend TypeScript/Vite production build: pass.
- npm production dependency audit: 0 vulnerabilities.
- Predeploy secret/API exposure scan: pass.
- Canonical verifier: pass with `PYTHONUTF8=1` on Windows.
- GitHub Actions: API lint/tests pass; web production build pass.

# Next task

1. Obtain external review for draft PR #2, address actionable feedback, and merge after CI passes.
2. Replace the deterministic local evaluation path with the configured Aiven PostgreSQL/pgvector and Gemini path, then prove run and review persistence.
3. When ready to host: link Blaze billing, install Google Cloud CLI, create server-side `DATABASE_URL` and `GEMINI_API_KEY` secrets, run the Aiven migration/seed, deploy Cloud Run and Firebase Hosting, smoke-test the live workflow, then attach `composer.jameai.space`.

# Risks or blockers

- Readiness status: `NOT PRODUCTION-READY` for public hosting until billing, server-side secrets, live database/model verification, deployment smoke tests, and rollback checks are complete.
- Google Cloud CLI is not installed yet and Blaze billing must be linked before Cloud Run deployment.
- Public access is intentionally low-risk only: anonymous requests are bounded but not authenticated, and the rate limiter is per Cloud Run instance. Do not use real client or personnel data.
- The generated visual is C86-inspired concept art; it is not an official brand asset.

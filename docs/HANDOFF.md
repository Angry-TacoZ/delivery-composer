# Goal

Ship a hosted, polished Delivery Composer MVP for a short consulting conversation. The app recommends a synthetic delivery team from a client brief and makes its evidence and human-review boundary visible.

# Current status

The local MVP is implemented and verified. Firebase project `composermvp` was created. Aiven PostgreSQL service `delivery-composer-db` is running. The app runs locally in deterministic preview mode until the Aiven and Gemini secrets are configured server-side.

# Decisions

- Public, low-risk demo using synthetic data only.
- React on Firebase Hosting; FastAPI on Cloud Run; Aiven PostgreSQL with pgvector; Gemini called only from the backend.
- Service URI and Gemini key are server-only secrets. Do not put either in a browser build, commit, or handoff.
- Firebase Hosting rewrites `/api/**` to Cloud Run service `delivery-composer-api` in `us-east1`.
- UI direction: restrained dark operations workspace, not generic pill/card SaaS styling.

# Changed files

- `api/app/`: FastAPI API, bounded public input, per-instance rate limit, Gemini provider boundary, controlled three-connection PostgreSQL pool, pgvector bootstrap migration, and synthetic data seed process.
- `web/`: React/Vite operations workspace with evidence expansion and a recorded human-review action.
- `firebase.json` and `.firebaserc`: Firebase Hosting SPA and `/api/**` Cloud Run rewrite configuration.
- `.codex/verify.json`: Canonical verification contract for the declared public-low-risk scope.

# Verification

- Firebase CLI authenticated as the project owner; `composermvp` was created successfully.
- Ruff: pass.
- Pytest: 3 pass; two warnings are from third-party packages on Python 3.14.
- Frontend TypeScript/Vite production build: pass.
- Browser check: compose, evidence expansion, and approve-review workflow passed with no console errors.
- Predeploy secret/API exposure scan: pass.
- Canonical verifier: pass when run with `PYTHONUTF8=1` because Windows cp1252 cannot print Vite's checkmark.

# Next task

- Link Cloud Billing/Blaze to `composermvp`; install Google Cloud CLI.
- Create server-side `DATABASE_URL` and `GEMINI_API_KEY` secrets, run the Aiven migration, and seed six synthetic profiles with Gemini embeddings.
- Deploy FastAPI to Cloud Run, deploy Firebase Hosting, verify the live workflow, then attach `composer.jameai.space`.

# Risks or blockers

- Google Cloud CLI is not installed yet.
- Billing must be linked to `composermvp` before Cloud Run deployment.
- Aiven and Gemini secrets must be configured outside source control; no real credentials have been added to the repository.
- Public access is intentionally low-risk only: anonymous requests are bounded but not authenticated, and the rate limiter is per Cloud Run instance. Do not load real client or candidate data into this MVP.

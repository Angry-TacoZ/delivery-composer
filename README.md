# Delivery Composer

Delivery Composer is a public, synthetic-data portfolio application for assembling consulting delivery teams from unstructured client briefs. It combines transparent constraints, auditable scoring, candidate comparison, and human approval in one governed workflow.

![Delivery Composer interface](docs/screenshots/delivery-composer-hero.png)

## The problem

Consultancies often know the experience an engagement needs but struggle to turn a brief into a consistent, defensible team recommendation. Delivery Composer demonstrates a safer division of labor:

1. Structure an ambiguous brief into explicit requirements.
2. Apply non-negotiable clearance and availability constraints.
3. Rank relevant experience with attributable scoring.
4. Expose supporting evidence, trade-offs, and exceptions.
5. Keep approval and revision with a human delivery leader.

> **Constraints first. Evidence second. Human decision always.**

## Delivery workflow

The interface uses a five-stage delivery-assurance cycle:

1. **Identify** captures the environment, outcome, and highest-impact need.
2. **Define** converts that need into roles, capabilities, clearance, and timing.
3. **Execute** composes an eligible team using deterministic rules or configured live adapters.
4. **Assure** exposes constraints and evidence for human review.
5. **Learn** records the decision and actionable revision feedback.

The stage strip represents real application state. In portfolio mode, feedback is retained only for the current API process and is labeled as temporary. The planned live path stores compositions and reviews in PostgreSQL. Neither path claims autonomous model training.

## What the public demo proves

- Three synthetic briefs produce different requirements, roles, scores, and team compositions.
- Fifteen fictional profiles provide three candidates for each supported role family.
- Every score is attributable: `58` points for exact-role fit, `8` per required-capability match, and `5` per preferred-sector match, capped at `97`.
- Clearance and availability remain eligibility gates rather than hidden score adjustments.
- A reviewer can compare candidates, select a visible exception, approve the team, or request a revision.
- Revision feedback creates a linked re-evaluation with an inspectable before-and-after delta.
- The browser receives no database credential or model-provider key.

The demo library is intentionally synthetic and editable. A bounded PDF extraction adapter is implemented and tested, but file upload is not exposed in the public interface.

## Architecture

The hosted portfolio build uses the deterministic path:

```text
React -> FastAPI -> deterministic requirements and scoring -> temporary review storage
```

The same FastAPI boundary owns the planned live adapters:

```text
React + Firebase Hosting
          |
          | /api/* rewrite
          v
FastAPI on Cloud Run ---- Gemini API (server-side only)
          |
          v
PostgreSQL + pgvector
```

`DEMO_MODE=true` prevents PostgreSQL and Gemini adapters from initializing even if credentials exist. `DEMO_MODE=false` requires both server-side services and fails at startup if configuration is incomplete.

## Repository map

```text
api/                    FastAPI service, domain logic, adapters, and tests
web/                    React/Vite operations interface
docs/                   Architecture, workflow, QA, and deployment documentation
output/pdf/             Synthetic brief fixtures
scripts/                Reproducible verification, deployment, and fixture tools
.github/workflows/      Pull-request and main-branch verification
```

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r api\requirements.txt -r api\requirements-dev.txt
npm.cmd --prefix web ci
```

Start the API and web application in separate terminals:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir api --reload --port 8000
npm.cmd --prefix web run dev
```

Open `http://127.0.0.1:5173` and choose any synthetic brief.

## Verify

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify.ps1
```

The repository-owned verifier runs Ruff, the API tests, and the frontend production build. CI runs the same core checks.

## Deployment

The current deterministic demo is hosted through Firebase Hosting and Cloud Run. The deployment script enforces a clean, synchronized `main`, confirms budget-alert acknowledgement, caps Cloud Run at one instance, and verifies the deterministic health response. See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Optional live adapters

Copy `.env.example` to an uncommitted `.env`, provide `DATABASE_URL` and `GEMINI_API_KEY` server-side, and set `DEMO_MODE=false`. The migration enables pgvector and creates the schema; the seed command creates embeddings for the fictional roster.

The live PostgreSQL/pgvector and Gemini path is an architectural extension point, not a verified capability of the public hosted demo.

## Safety boundary

This repository is a public, low-risk demonstration using fictional people and synthetic engagement data. It is not a production staffing or hiring system. Do not submit real client, employee, consultant, candidate, regulated, or confidential information.

## License

Released under the [MIT License](LICENSE).

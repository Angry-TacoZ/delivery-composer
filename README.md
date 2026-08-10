# Delivery Composer

An evidence-backed staffing MVP for consulting delivery teams. Delivery Composer turns an unstructured client brief into validated requirements, applies non-negotiable constraints, retrieves relevant experience, and leaves the final decision with a human delivery leader.

![Delivery Composer C86-aligned interface](docs/screenshots/delivery-composer-hero.png)

## Why this exists

Consultancies often know the experience they need but cannot consistently turn a brief into a defensible team recommendation. This MVP demonstrates a safer division of labor:

1. AI structures ambiguous requirements.
2. PostgreSQL enforces hard constraints.
3. pgvector ranks semantically relevant experience.
4. The interface exposes evidence and exceptions.
5. A person approves or revises the recommendation.

> **Rules first. Semantic retrieval second. Human decision always.**

## What the demo proves

- A realistic client brief can be converted into a three-person delivery recommendation.
- Every proposed consultant is accompanied by the evidence and hard-constraint checks used to support the match.
- AI-generated reasoning is advisory and cannot bypass clearance or availability rules.
- The same interface supports a deterministic, no-cost preview and the configured PostgreSQL/pgvector + Gemini path.
- The public-facing concept uses synthetic people and engagement data only.

## Architecture

```text
React + Firebase Hosting
          |
          | /api/* rewrite
          v
FastAPI on Cloud Run ---- Gemini API (server-side only)
          |
          v
Aiven PostgreSQL + pgvector
```

The browser never receives the Aiven connection URI or Gemini API key. FastAPI validates the brief, bounds request size, and owns all database and model-provider access.

## Repository map

```text
api/                    FastAPI service, domain logic, migration, seed, tests
web/                    React/Vite client and C86-aligned visual system
docs/                   Architecture handoff, visual criteria, QA evidence
.codex/verify.json      Canonical local verification contract
.github/workflows/      Pull-request and main-branch CI
firebase.json           Hosting and Cloud Run rewrite configuration
```

## Run locally

1. Create a virtual environment and install API dependencies:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r api\requirements.txt -r api\requirements-dev.txt
   ```

2. Install frontend dependencies:

   ```powershell
   npm.cmd --prefix web ci
   ```

3. Start the API in deterministic preview mode. This path makes no paid model calls:

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir api --reload --port 8000
   ```

4. Start the frontend:

   ```powershell
   npm.cmd --prefix web run dev
   ```

Open `http://127.0.0.1:5173` and run the populated sample brief.

## Enable PostgreSQL, pgvector, and Gemini

Copy `.env.example` to `.env` and add the real values locally. Never commit `.env`, a database URI, or a model API key.

After `DATABASE_URL` and `GEMINI_API_KEY` are available server-side:

```powershell
Push-Location api
..\.venv\Scripts\python.exe -m app.migrations
..\.venv\Scripts\python.exe -m app.seed
Pop-Location
```

`migrations.py` enables pgvector and creates the schema. `seed.py` generates embeddings for a small set of synthetic consultant profiles.

## Verification

Run the same required checks used by the repository contract:

```powershell
.\.venv\Scripts\python.exe -m ruff check api
.\.venv\Scripts\python.exe -m pytest api\tests
npm.cmd --prefix web run build
```

The visual workflow is also checked at desktop and mobile widths for composition, evidence expansion, review recording, console errors, unintended overflow, and the animated trajectory field. See [`docs/design-qa.md`](docs/design-qa.md).

## Current boundary

This repository is a **public-low-risk demo implementation using synthetic data**, not a production staffing or hiring decision system. The hosted PostgreSQL, model, and deployment path still requires server-side secret configuration, billing safeguards, live integration verification, and deployment smoke testing. Do not load real client, candidate, or employee information into this MVP.

The interface is a tailored concept for a C86 conversation. It is not an official C86 product and does not claim C86 endorsement or ownership.

# Delivery Composer

An AI-assisted staffing-composition MVP for consulting delivery teams. It turns a client brief into validated requirements, applies hard constraints in PostgreSQL, uses pgvector for semantic retrieval, and presents a human-reviewable recommendation with evidence.

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

The browser never receives the Aiven connection URI or Gemini API key.

## Local setup

1. Create a virtual environment and install the API dependencies:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r api\requirements.txt -r api\requirements-dev.txt
   ```

2. Copy `.env.example` to `.env` and enter the real values locally. Do not commit `.env`.

3. Install frontend dependencies:

   ```powershell
   npm.cmd --prefix web install
   ```

4. Start the API in deterministic demo mode (no paid calls):

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir api --reload --port 8000
   ```

5. Start the frontend:

   ```powershell
   npm.cmd --prefix web run dev
   ```

## Connect Aiven and Gemini

Run these only after setting `DATABASE_URL` and `GEMINI_API_KEY` in your local `.env` or server-side secrets:

```powershell
   Push-Location api
   ..\.venv\Scripts\python.exe -m app.migrations
   ..\.venv\Scripts\python.exe -m app.seed
   Pop-Location
```

`migrations.py` enables `pgvector` and creates the schema. `seed.py` makes a small number of embedding API calls for synthetic consultant profiles.

## Verification

```powershell
.\.venv\Scripts\python.exe -m ruff check api
.\.venv\Scripts\python.exe -m pytest api\tests
npm.cmd --prefix web run build
```

## Demo boundary

This MVP is a public, low-risk demonstration with synthetic data only. It has a small per-instance rate limiter, strict brief size limits, server-side validation, and a low Cloud Run instance cap. It is not an ATS, a system of record, or a decision system for real hiring.

# Code Optimizer

> Analyze code and propose measured optimizations.

Runs analyses over a codebase, proposes optimizations with expected impact, shows diffs before adoption, and keeps a history of applied changes.

## Features

- Static and dynamic analysis passes
- Optimization proposals with impact estimates
- Diff preview before applying
- History of applied optimizations

## Architecture

| Layer | Stack | Path |
|---|---|---|
| Frontend | Astro (file-based routing) | `frontend/` |
| Backend | FastAPI + SQLAlchemy + Pydantic | `backend/` |
| Tests | pytest | `backend/tests/` |

Frontend routes: `analysis, diff, history, settings`.

## Quick start

Backend (from `backend/`):

```bash
pip install -r requirements.txt
cp .env.example .env        # optional — works with no keys
python3 -m uvicorn app.main:app --port 8001
```

Frontend (from `frontend/`):

```bash
npm install
npm run dev
```

Tests: `python3 -m pytest backend/tests/ -v`

## Deployment

The frontend builds to a static bundle and deploys to GitHub Pages on every
push to `main` (`.github/workflows/deploy.yml`):

**https://adineo-cmd2.github.io/code-optimizer/**

## Project structure

```
backend/
  app/          FastAPI application
  tests/        pytest suite
frontend/
  src/pages/    Astro routes
```

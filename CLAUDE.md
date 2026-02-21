# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LessonLines is a web application for K-12 teachers to create historical timelines. It combines a timeline builder with a curated database of historical events aligned to curriculum standards (Common Core, AP US History, Texas TEKS).

**Status:** Implementation in progress - design docs in `/specs/`, core backend and frontend implemented.

## Architecture

```
Frontend (React + Vite + Tailwind) → API Gateway → Lambda (FastAPI + Mangum) → RDS Proxy → PostgreSQL
```

- **Frontend:** React with TypeScript, hosted on AWS Amplify
- **Backend:** FastAPI with Mangum adapter for Lambda, SQLAlchemy ORM
- **Database:** PostgreSQL on RDS with RDS Proxy for Lambda connection pooling
- **Auth:** AWS Cognito (JWT tokens in Authorization header)
- **Payments:** Stripe (one-time $25-35 pro purchase)

## Development Commands

### Backend

```bash
# Start local PostgreSQL
docker run --name lessonlines-db -e POSTGRES_USER=lessonlines -e POSTGRES_PASSWORD=localdev -e POSTGRES_DB=lessonlines -p 5432:5432 -d postgres:15

# Setup and run
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

**Local (SQLite):**
```bash
# Create a new migration
cd backend
alembic revision --autogenerate -m "description"

# Apply locally
alembic upgrade head
alembic downgrade -1
```

Note: Local dev uses SQLite. When adding columns, you may need to delete `backend/lessonlines.db` and re-seed (`python -m app.seed`) since SQLite doesn't support all ALTER TABLE operations.

**Production (RDS via Lambda):**

The Lambda handler (`handler.py`) supports migration commands via direct invocation:

```bash
# Run all pending migrations
aws lambda invoke --function-name lessonlines-dev-api \
  --cli-binary-format raw-in-base64-out \
  --payload '{"action": "migrate", "command": "upgrade", "revision": "head"}' \
  /tmp/migrate-out.json && cat /tmp/migrate-out.json

# Check current migration version
aws lambda invoke --function-name lessonlines-dev-api \
  --cli-binary-format raw-in-base64-out \
  --payload '{"action": "migrate", "command": "current"}' \
  /tmp/migrate-out.json && cat /tmp/migrate-out.json

# Downgrade one revision
aws lambda invoke --function-name lessonlines-dev-api \
  --cli-binary-format raw-in-base64-out \
  --payload '{"action": "migrate", "command": "downgrade", "revision": "-1"}' \
  /tmp/migrate-out.json && cat /tmp/migrate-out.json

# Seed the database
aws lambda invoke --function-name lessonlines-dev-api \
  --cli-binary-format raw-in-base64-out \
  --payload '{"action": "seed"}' \
  /tmp/migrate-out.json && cat /tmp/migrate-out.json
```

### Deployment

```bash
# Backend (CDK)
cd infra && npx cdk deploy --all --require-approval never

# Frontend auto-deploys via Amplify on push to main
```

## Key Database Relationships

- `events` belong to `topics` (Civil War, Revolution, WWII)
- `events` link to `curriculum_standards` via `event_standards` junction table
- `events` have `tags` via `event_tags` junction table
- `timelines` belong to `users` and contain `timeline_events`
- `timeline_events` can reference curated events OR be custom (event_id NULL)

## API Structure

- `/api/events` - Search curated events (filters: topic, keyword, standard, tag, grade)
- `/api/topics` - List available topics
- `/api/standards` - Search curriculum standards
- `/api/timelines` - User timeline CRUD
- `/api/timelines/{id}/export/pdf` - PDF export (pro feature)

## Frontend State

Uses React Context + useReducer for timeline editor state. Key hooks:
- `useTimeline` - Timeline state management with auto-save (1s debounce)
- `useEvents` - Event database queries
- `useDragDrop` - @dnd-kit integration for drag-and-drop

## Git Conventions

- Do not include mentions of Claude or AI in commit messages
- Use conventional commit style (e.g., "Add user authentication", "Fix bcrypt compatibility")

## Important Implementation Notes

- RDS Proxy is required for Lambda - prevents connection exhaustion
- Use SQLAlchemy async with asyncpg for Lambda performance
- Full-text search uses PostgreSQL `to_tsvector` (no Elasticsearch needed)
- Events should align to multiple curriculum standards where appropriate
- UI mockup reference: `specs/lessonlines_ui_mockup.html`

## git wotkflow

Make all changes in fresh PRs.
Don't mention claude in the PR descriptions


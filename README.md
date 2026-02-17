# LessonLines

A web application for K-12 teachers to create historical timelines, combining a timeline builder with a curated database of historical events aligned to curriculum standards (Common Core, AP US History, Texas TEKS).

## Architecture

```
Frontend (React + Vite + Tailwind) → API Gateway → Lambda (FastAPI + Mangum) → RDS Proxy → PostgreSQL
```

- **Frontend:** React with TypeScript, hosted on AWS Amplify
- **Backend:** FastAPI with Mangum adapter for Lambda, SQLAlchemy ORM
- **Database:** PostgreSQL on RDS (private subnet, no public access)
- **Auth:** JWT tokens
- **Infra:** AWS CDK (TypeScript)

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for local PostgreSQL)

### Backend

```bash
# Start local PostgreSQL
docker run --name lessonlines-db \
  -e POSTGRES_USER=lessonlines \
  -e POSTGRES_PASSWORD=localdev \
  -e POSTGRES_DB=lessonlines \
  -p 5432:5432 -d postgres:15

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

## Deployment

### Deploy Infrastructure (CDK)

```bash
cd infra
npx cdk deploy --all                      # Deploy all stacks
npx cdk deploy LessonLines-dev-Backend    # Deploy backend only
```

The CDK bundling automatically packages the backend code, dependencies, and Alembic migrations into the Lambda deployment artifact.

Frontend auto-deploys via Amplify on push to `main`.

### Database Migrations (Remote)

The RDS database is in a private subnet with no public access. Migrations are run via Lambda invoke.

```bash
# Run all pending migrations
aws lambda invoke --function-name lessonlines-dev-api \
  --cli-binary-format raw-in-base64-out \
  --payload '{"action": "migrate"}' /tmp/out.json && cat /tmp/out.json

# Migrate to a specific revision
aws lambda invoke --function-name lessonlines-dev-api \
  --cli-binary-format raw-in-base64-out \
  --payload '{"action": "migrate", "revision": "001"}' /tmp/out.json && cat /tmp/out.json

# Check current migration revision
aws lambda invoke --function-name lessonlines-dev-api \
  --cli-binary-format raw-in-base64-out \
  --payload '{"action": "migrate", "command": "current"}' /tmp/out.json && cat /tmp/out.json

# View migration history
aws lambda invoke --function-name lessonlines-dev-api \
  --cli-binary-format raw-in-base64-out \
  --payload '{"action": "migrate", "command": "history"}' /tmp/out.json && cat /tmp/out.json

# Downgrade one revision
aws lambda invoke --function-name lessonlines-dev-api \
  --cli-binary-format raw-in-base64-out \
  --payload '{"action": "migrate", "command": "downgrade", "revision": "-1"}' /tmp/out.json && cat /tmp/out.json
```

### Database Migrations (Local)

```bash
cd backend
source venv/bin/activate

alembic upgrade head          # Run all pending migrations
alembic downgrade -1          # Roll back one migration
alembic current               # Show current revision
alembic revision --autogenerate -m "description"  # Generate new migration
```

### Database Seeding (Remote)

Seed the database with curated historical events (Civil War, American Revolution, WWII), curriculum standards, and tags:

```bash
aws lambda invoke --function-name lessonlines-dev-api \
  --cli-binary-format raw-in-base64-out \
  --payload '{"action": "seed"}' /tmp/out.json && cat /tmp/out.json
```

The seed script is idempotent -- it skips seeding if data already exists.

### Database Seeding (Local)

```bash
cd backend
source venv/bin/activate
python -m app.seed
```

## Typical First Deploy Workflow

```bash
# 1. Deploy infrastructure
cd infra && npx cdk deploy --all

# 2. Run database migrations
aws lambda invoke --function-name lessonlines-dev-api \
  --cli-binary-format raw-in-base64-out \
  --payload '{"action": "migrate"}' /tmp/out.json && cat /tmp/out.json

# 3. Seed the database
aws lambda invoke --function-name lessonlines-dev-api \
  --cli-binary-format raw-in-base64-out \
  --payload '{"action": "seed"}' /tmp/out.json && cat /tmp/out.json

# 4. Verify
curl https://5rbw7mcz8k.execute-api.us-east-1.amazonaws.com/api/topics
```

## Code Review

All pull requests are automatically reviewed by Claude via the [Claude Code GitHub Action](https://github.com/anthropics/claude-code-action). Reviews run on PR open and on each new push.

## API Endpoints

- `GET /api/events` - Search curated events (filters: topic, keyword, standard, tag, grade)
- `GET /api/topics` - List available topics
- `GET /api/standards` - Search curriculum standards
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Log in
- `GET /api/timelines` - User timeline CRUD
- `GET /api/timelines/{id}/export/pdf` - PDF export (pro feature)

## Environments

| Environment | API URL | Frontend URL |
|---|---|---|
| dev | `https://5rbw7mcz8k.execute-api.us-east-1.amazonaws.com` | `https://main.d2x0esfdyptcmb.amplifyapp.com` |

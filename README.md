# AI Social Media SaaS

Production-oriented, multi-tenant social media SaaS foundation using Next.js, FastAPI, Neon PostgreSQL, Celery, and Redis. Product behavior and architecture are defined in `PRODUCT_OVERVIEW.md` and `docs/`.

## Prerequisites

- Node.js 22 or 24 and npm
- Python 3.12 and `uv`
- Docker Desktop with Docker Compose
- A non-production Neon branch when testing database connectivity or migrations

Copy `.env.example` to `.env` only when local credentials are available. Use a pooled Neon URL for `DATABASE_URL` and the matching direct URL for `DATABASE_URL_UNPOOLED`. Never use production credentials for local agent work.

## Local development

Backend:

```powershell
cd backend
uv sync
uv run uvicorn social_saas.main:app --reload
```

Frontend in another terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Redis and a Celery worker:

```powershell
docker compose up -d redis
cd backend
uv run celery --app=social_saas.worker.celery_app:celery_app worker --loglevel=INFO
```

Full composed foundation:

```powershell
docker compose up --build
```

Open `http://localhost:8080`. Liveness is available at `http://localhost:8080/api/v1/health/live`; readiness also checks configured database and Redis dependencies.

## Verification

```powershell
cd backend
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest

cd ../frontend
npm run lint
npm run typecheck
npm test
npm run build
```

Run Alembic only with a direct connection to an authorized development branch:

```powershell
cd backend
uv run alembic current
```

## Agent workflow

Shared instructions live in `AGENTS.md`, Cursor frontend rules in `.cursor/rules/frontend.mdc`, and the read-only OpenCode reviewer in `.opencode/agents/reviewer.md`. Follow the active milestone in `docs/IMPLEMENTATION_PLAN.md` and use separate Git worktrees for parallel backend and frontend tasks.

After the reviewed baseline has an initial commit, create milestone worktrees from the same base commit:

```powershell
git worktree add ..\ai-social-media-saas-backend -b feat/m2-auth-backend main
git worktree add ..\ai-social-media-saas-frontend -b feat/m2-auth-frontend main
git worktree add --detach ..\ai-social-media-saas-review <commit-to-review>
```

Assign one owner and a non-overlapping file set to each task. Freeze backend API contracts before frontend integration. The reviewer inspects the exact completed commit and sends findings to the original implementation owner for fixes.

An AI-powered social media workspace that turns a campaign goal into researched, brand-aware, ready-to-review posts, with human-controlled publishing.

## Documentation

- [`PRODUCT_OVERVIEW.md`](PRODUCT_OVERVIEW.md) — confirmed product definition and V1 scope baseline.
- [`docs/PRODUCT_REQUIREMENTS.md`](docs/PRODUCT_REQUIREMENTS.md) — end-to-end V1 product requirements, lifecycle rules, acceptance criteria, risks, launch gates, and open decisions.
- [`docs/TECH_STACK.md`](docs/TECH_STACK.md) — finalized technology responsibilities and constraints.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — approved system architecture and security boundaries.
- [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md) — milestone sequence, acceptance criteria, and Definitions of Done.
- [`AGENTS.md`](AGENTS.md) — constraints for contributors and coding agents.

## Confirmed V1 boundaries

- One automatically provisioned private workspace per authenticated user.
- One reusable brand profile per workspace.
- Hybrid campaign creation through a natural-language prompt and optional structured inputs.
- Coordinated AI responsibilities for planning, conditional research, writing, visual recommendations, and review.
- Per-post editing, targeted revision, and explicit human approval.
- A maximum of two AI image-generation events per campaign, including regenerations.
- Scheduling and publishing of approved posts through Zernio, subject to integration validation.
- No teams, shared workspaces, AI-generated video, unlimited image generation, or approval-bypassing autonomous publishing in V1.

## Current status

The development foundation is implemented. Product features, authentication, domain schema, and provider integrations remain milestone-gated and are not part of this foundation.


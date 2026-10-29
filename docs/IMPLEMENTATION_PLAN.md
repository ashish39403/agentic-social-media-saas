# AI Social Media SaaS — V1 Implementation Plan

| Field | Value |
|---|---|
| Status | Proposed execution baseline; implementation requires explicit user approval |
| Version | 1.0 |
| Prepared | 29 October 2026 |
| Product authority | `PRODUCT_OVERVIEW.md` and `docs/PRODUCT_REQUIREMENTS.md` |
| Architecture authority | `docs/ARCHITECTURE.md` |
| Technology authority | `docs/TECH_STACK.md` |
| Delivery method | Milestone-gated, vertical-slice development |
| Default workflow | Plan → Implement → Test → Review → Fix → Commit |

> This plan creates no application code and authorizes no infrastructure changes. It defines the order, ownership, contracts, tests, and gates for later AI-assisted implementation. A milestone may begin only after its dependencies are complete and its bounded task is approved.

---

## 1. Purpose and delivery principles

The goal is a secure, understandable, deployed V1 in which two real users can independently sign up, receive isolated workspaces, configure brands, generate campaigns, review and approve exact post versions, connect LinkedIn and Instagram through Zernio, schedule approved content, and observe truthful publishing results.

Implementation follows these principles:

1. **Deliver vertical slices.** Connect backend, database, and frontend behavior inside each product milestone.
2. **Preserve architecture.** Do not reopen finalized stack decisions during implementation unless a verified incompatibility blocks delivery.
3. **Keep changes bounded.** One agent task should have one primary outcome, explicit file ownership, and executable verification.
4. **Build security into each slice.** Tenant isolation, approval validity, idempotency, and failure behavior are not end-stage hardening work.
5. **Verify external contracts early.** Neon Auth, AI Credits, Tavily, Zernio, and S3 assumptions receive focused integration spikes before broad dependent work.
6. **Use migrations as code.** SQLAlchemy models and Alembic revisions evolve together; no ad hoc production schema changes.
7. **Treat PostgreSQL as authoritative.** Redis, Celery metadata, frontend state, LangGraph state, and provider identifiers cannot override durable application state.
8. **Avoid speculative scale.** No microservices, Kubernetes, real-time infrastructure, additional databases, or enterprise features in V1.
9. **Stop at gates.** A milestone does not become “done” because code exists; tests, runtime verification, review, and acceptance criteria must pass.
10. **Keep humans in control.** AI-generated content remains draft content until explicit approval of the current publishable version.

---

## 2. Source reconciliation and scope

The prompt refers to `docs/PRODUCT_OVERVIEW.md` and `docs/PRD.md`; the actual repository sources are:

- `PRODUCT_OVERVIEW.md`;
- `docs/PRODUCT_REQUIREMENTS.md`;
- `docs/TECH_STACK.md`;
- `docs/ARCHITECTURE.md`;
- `AGENTS.md`.

No earlier `docs/IMPLEMENTATION_PLAN.md` existed when this plan was prepared.

### 2.1 In-scope V1 outcomes

- public landing and authentication experience;
- Neon Managed Better Auth with email/password and Google OAuth;
- one automatically provisioned private workspace per user;
- one saved brand profile;
- hybrid campaign creation;
- Celery-backed LangGraph generation;
- conditional Tavily research and retained sources;
- LinkedIn/Instagram post drafts;
- S3 uploads, web-image rights confirmation, and at most two provider-started AI image generations per campaign;
- immutable post versions, manual/AI editing, and explicit approval;
- Zernio account connections, scheduling, publishing, signed webhooks, and manual failed-post retry;
- dashboard, job progress, calendar/status, export, and account deletion;
- security, recovery, deployment, and two-user acceptance verification.

### 2.2 Explicitly excluded

- teams, invitations, roles, or shared/multiple workspaces;
- multiple reusable brands per workspace;
- platforms beyond LinkedIn and Instagram;
- AI video;
- unlimited image generation;
- automatic failed-post republishing;
- approval-free autonomous publishing;
- billing, pricing, advanced analytics, competitor monitoring, and social listening;
- microservices, Kubernetes, ECS, managed Redis, or high-availability topology unless separately approved after V1 evidence.

---

## 3. Roles and file ownership

### 3.1 Default agent responsibilities

| Agent | Primary ownership | Typical review relationship |
|---|---|---|
| **Codex** | Python/FastAPI, SQLAlchemy/Alembic, Neon integration, LangChain/LangGraph, Celery/Redis, provider adapters, S3, infrastructure, CI/CD, complex cross-cutting changes | Implements backend/infra; responds to OpenCode and human review |
| **Cursor** | Next.js App Router, TypeScript, Tailwind CSS, shadcn/ui, frontend HTTP integration, forms, interaction, accessibility, responsive behavior | Implements frontend against frozen contracts; responds to OpenCode and human review |
| **OpenCode** | Independent code review, adversarial tests, bug discovery, security/tenant review, architecture compliance, regression verification | Must not rewrite implementation while reviewing; reports findings to owner |

These are defaults, not a requirement to invoke all three agents for every task.

### 3.2 Ownership boundaries

| Path/area | Primary writer | Coordination rule |
|---|---|---|
| `backend/**` | Codex | Cursor reads generated/frozen contracts but does not edit backend implementation |
| `backend/migrations/**` | Codex | One migration author at a time; no parallel heads without an explicit merge revision plan |
| `frontend/**` | Cursor | Codex may review contract usage but does not edit UI concurrently |
| `infra/**`, `docker-compose.yml`, `.github/workflows/**` | Codex | Infrastructure changes require OpenCode review before production use |
| `docs/ARCHITECTURE.md`, `docs/TECH_STACK.md`, `docs/PRODUCT_REQUIREMENTS.md` | Human-approved architecture owner | Implementation agents do not silently change product/architecture sources |
| `docs/IMPLEMENTATION_PLAN.md` | Technical lead | Update only after a milestone decision or discovered verified dependency change |
| Shared contract artifact/OpenAPI output | Codex generates; Cursor consumes | Contract change lands before or with compatible frontend change; no divergent handwritten duplicate |

### 3.3 Parallel-work rules

- Use isolated Git branches and preferably isolated worktrees for concurrently active agents.
- Never assign two agents write ownership of the same file set in the same time window.
- Backend and frontend may proceed in parallel only after the affected HTTP contract is agreed and recorded.
- A database migration and code depending on it remain in the same integration sequence.
- Provider adapter work may proceed with fakes, but live-contract findings must be merged before dependent acceptance is claimed.
- OpenCode reviews a commit/branch diff from a fixed base; it does not review a moving working tree.
- If a review identifies a contract or architecture conflict, stop dependent parallel work until the owner resolves it.

---

## 4. Development workflow and Git strategy

### 4.1 Required loop

Every bounded task follows:

1. **Plan:** restate scope, files, contract, tests, risks, and non-goals.
2. **Implement:** change only owned files; preserve unrelated work.
3. **Test:** run targeted tests first, then the milestone gate suite.
4. **Review:** self-review plus mandatory independent review where specified.
5. **Fix:** address findings and rerun affected verification.
6. **Commit:** create a focused commit only after evidence is clean.

No task is handed off with “tests not run” when the required tests are runnable.

### 4.2 Branch model

- `main`: protected, releasable, no direct AI-agent commits.
- `milestone/mXX-short-name`: optional integration branch for a milestone with multiple parallel tasks.
- `feat/mXX-task-short-name`: bounded implementation branch from the current milestone base.
- `fix/mXX-short-name`: correction discovered during milestone review.
- `spike/mXX-provider-contract`: disposable integration spike; useful results are converted into tests/contracts before merge.

Rules:

- Rebase or merge the latest milestone base before final verification.
- Require passing CI and human approval before merging to `main`.
- Squash only when it preserves useful migration/history clarity; otherwise use focused commits.
- Never combine unrelated cleanup with a milestone task.
- Tag the accepted V1 deployment after production acceptance.

### 4.3 Commit expectations

Each commit should state the behavioral outcome and include:

- implementation;
- its relevant tests;
- migration when required;
- safe configuration/example updates;
- contract/docs update when behavior changed.

Secrets, generated exports, local databases, `.env*` credentials, Neon connection strings, and provider payload captures containing private data must not be committed.

---

## 5. Neon development and safety workflow

### 5.1 Confirmed Neon approach

- Neon Managed Better Auth and Lakebase Postgres are used; AWS S3 remains the media store.
- The Next.js application uses the managed Neon Auth wrapper and same-origin auth proxy appropriate to the installed SDK.
- The browser obtains a short-lived JWT for FastAPI bearer authentication.
- FastAPI verifies EdDSA/JWKS, issuer, audience where defined, expiry, and stable subject, then checks application user/workspace status.
- Auth-managed data stays in Neon's managed `neon_auth` schema; Alembic owns only application schemas.
- FastAPI and Celery use a pooled application connection URL.
- Alembic, dumps, restores, and session-dependent administration use the direct/unpooled URL.

Current official Neon documentation states that Managed Better Auth browser flows primarily use secure HTTP-only sessions, while raw JWTs are intended for separate backends; Managed access tokens currently expire after 15 minutes and use EdDSA by default. These details must be verified against the installed SDK and actual branch during Milestone 2.

### 5.2 Environment and branch model

| Environment | Neon branch/data policy | Who may modify it |
|---|---|---|
| Local feature development | Normal branch from synthetic/non-production development baseline; 7-day expiry recommended | Assigned developer/agent through reviewed CLI operations |
| Pull request/CI | Ephemeral normal branch with synthetic fixtures; 1-day expiry recommended | CI identity with branch-limited task scope |
| Migration rehearsal | Normal production-like branch only when data policy permits; otherwise schema-only branch plus synthetic fixtures | Codex/human-approved CI workflow |
| Staging | Persistent protected staging branch with test identities/accounts | Controlled deployment identity |
| Production | Protected default/production branch | CI protected environment and human approval only |

Neon branches are copy-on-write and isolated from their parent. Once production contains personal data, agent-accessible branches must not copy raw production PII. Use a schema-only branch or a sanitized non-production parent when privacy requires it. Schema-only branching behavior and plan availability must be verified before relying on it.

### 5.3 Branch-first development loop

For a task that changes schema:

1. create/checkout the matching Git feature branch/worktree;
2. create/checkout a matching non-production Neon branch with explicit expiration;
3. point `DATABASE_URL` to the pooled branch URL and `DATABASE_URL_UNPOOLED` to the direct branch URL;
4. generate/review an Alembic revision;
5. apply migrations through the direct URL;
6. run migration, integration, and rollback/roll-forward checks;
7. inspect the schema diff;
8. merge only after CI applies the revision to a fresh ephemeral branch successfully;
9. delete/expire the feature branch after merge.

Never overwrite an existing local environment file or connection key without explicit confirmation. Prefer runtime injection or a dedicated gitignored env file when agents should not persist credentials.

### 5.4 Neon CLI and MCP

- Prefer the Neon CLI for branch lifecycle and repeatable development commands.
- Use Neon MCP for documentation, inspection, and development/testing only.
- Configure MCP with OAuth, project scope, category filtering, and `readonly=true` for exploration where possible.
- Never connect an AI MCP session to the production database.
- Never give an agent a production owner connection string.
- Schema changes use reviewed Alembic revisions, not unrestricted agent-generated production SQL.
- Mutating development-branch operations require explicit task scope and human review.
- Production migrations run through protected CI with `DATABASE_URL_UNPOOLED` and a human approval gate.

### 5.5 Neon infrastructure configuration

Milestone 1/2 should establish a version-controlled Neon configuration only for selected Neon capabilities:

- Managed Auth enabled;
- branch policy for new development/preview branches where supported;
- no Data API;
- no Neon Functions;
- no Neon Object Storage;
- no Neon AI Gateway, because the finalized model gateway is AI Credits.

Do not run broad `neon init` or environment pulls until existing configuration and environment files are inspected. Do not create a second Neon project when a valid project/connection already exists.

### 5.6 Official Neon references

- [Managed Better Auth with Next.js](https://neon.com/docs/auth/quick-start/nextjs-api-only)
- [Managed Better Auth JWT](https://neon.com/docs/auth/guides/plugins/jwt)
- [Neon branching](https://neon.com/docs/introduction/branching)
- [Branch expiration](https://neon.com/docs/guides/branch-expiration)
- [Connection pooling](https://neon.com/docs/connect/connection-pooling)
- [Neon MCP Server and access controls](https://neon.com/docs/ai/neon-mcp-server)

---

## 6. Quality gates

### 6.1 Gate applied to every milestone

A milestone is complete only when all applicable checks pass:

- functional acceptance demonstrated against the integrated slice;
- targeted automated tests pass;
- the broader affected backend/frontend suites pass;
- tenant-isolation and security negatives pass for private data changes;
- migrations apply to an empty/fresh branch and the intended existing-state branch;
- provider integration is live-tested when the milestone claims provider behavior;
- architecture and source-of-truth review finds no silent divergence;
- user-visible loading, empty, error, and retry states are verified;
- human review accepts the behavior and evidence;
- Definition of Done checklist is fully satisfied.

### 6.2 Mandatory OpenCode reviews

Independent OpenCode review is mandatory for:

- authentication, JWT/JWKS, session, and workspace provisioning;
- every migration establishing or changing tenant ownership;
- Celery idempotency, dispatch recovery, concurrency, and cancellation;
- image-budget reservation/accounting;
- content versioning and approval;
- Zernio connections, scheduling, webhooks, idempotency, and retry;
- S3 authorization and presigned access;
- export/deletion/retention;
- Nginx, secrets, CI/CD, migrations, backup, and deployment;
- the final security/release candidate.

For low-risk isolated UI composition or copy changes, OpenCode review is optional unless the change affects auth, approval, publishing, media rights, or deletion.

### 6.3 Review output format

OpenCode reports findings by severity with:

- path and line;
- violated requirement/invariant;
- concrete impact;
- reproducible evidence;
- recommended fix;
- verification required after the fix.

Style preferences do not block a milestone unless they violate repository standards, accessibility, maintainability, or an approved interface.

---

## 7. Milestone dependency map

```text
M0 prerequisites and contract register
  ↓
M1 executable repository foundation
  ↓
M2 Neon Auth + isolated workspace vertical slice
  ↓
M3 brand profile vertical slice
  ↓
M4 campaign creation + persistent Celery job shell
  ↓
M5 LangGraph text campaign generation
  ↓
M6 conditional Tavily research and citations
  ↓
M7 S3 media + AI image quota
  ↓
M8 post editing, versions, and approval
  ↓
M9 Zernio profiles and social connections
  ↓
M10 scheduling, publishing, webhooks, and manual retry
  ↓
M11 dashboard/calendar and end-to-end UX consolidation
  ↓
M12 export, deletion, and retention
  ↓
M13 security, reliability, and release-candidate validation
  ↓
M14 AWS deployment, CI/CD, and production acceptance
```

M2–M12 each deliver visible behavior across the necessary backend and frontend instead of postponing all frontend integration.

---

## 8. Milestone 0 — Prerequisites and implementation contract register

### Objective

Remove external-account and contract blockers before code is generated. This is a planning/readiness milestone, not application implementation.

### Dependencies

- Approved PRD, technology stack, architecture, and this plan.
- Human access to required provider accounts.

### Ownership

- Technical lead/human: accounts, plan choices, secrets authority, approvals.
- Codex: read-only inventory and contract checklist.
- OpenCode: not required unless a security configuration is proposed.

### Exact tasks

- [ ] M0-T01 Confirm the repository will use the architecture's `frontend/`, `backend/`, `infra/`, and `docs/` convention.
- [ ] M0-T02 Confirm GitHub repository, protected `main`, required reviews, and environment names.
- [ ] M0-T03 Confirm Neon organization/project or record that project creation requires human action.
- [ ] M0-T04 Confirm the selected Neon region supports Managed Auth and that IP Allow/Private Networking does not conflict with Managed Auth.
- [ ] M0-T05 Confirm development, staging, and production branch naming and PII policy.
- [ ] M0-T06 Confirm Google OAuth app ownership and planned development/production redirect origins.
- [ ] M0-T07 Confirm AI Credits account, Tavily account, and non-production credentials are available without exposing values.
- [ ] M0-T08 Confirm Zernio account/plan, LinkedIn test account, Instagram test account, webhook endpoint requirements, and documented capabilities.
- [ ] M0-T09 Confirm AWS account, target region, domain/DNS ownership, EC2/S3/Secrets Manager permissions, and deployment approver.
- [ ] M0-T10 Create a verification register listing each provider assumption, owner, evidence, and milestone deadline.
- [ ] M0-T11 Freeze the common HTTP error envelope, correlation ID convention, and application status terminology from the architecture.
- [ ] M0-T12 Record provisional runtime versions to validate in M1 rather than allowing agents to choose independently.

### Relevant modules/files

- `docs/IMPLEMENTATION_PLAN.md` only if readiness facts require an approved update.
- No application directories or infrastructure are created in M0.

### Database changes

- None.

### API contracts

- No application API is created or changed.
- The shared error-envelope, correlation-ID, and status conventions are recorded as implementation constraints for M1 and later milestones.

### External integrations

- Provider access and documented contract assumptions are checked read-only.
- No provider resource, credential, webhook, OAuth application, cloud resource, or production configuration is created or changed.

### Automated tests

- None; this milestone is verified through evidence and access checks without printing secrets.

### Acceptance criteria

- All required provider accounts have an owner and readiness status.
- No unresolved account/setup blocker is hidden inside an implementation milestone.
- Agents know which environments they may access.
- Production credentials and production Neon access are explicitly outside AI-agent access.

### Definition of Done

- [ ] Readiness register is complete.
- [ ] Missing human actions are assigned.
- [ ] Runtime/version decisions have an owner and M1 deadline.
- [ ] Human approves beginning repository setup.

---

## 9. Milestone 1 — Executable repository and development foundation

### Objective

Create the smallest reproducible application that starts locally and proves the frontend, FastAPI, PostgreSQL connection, Redis/Celery wiring, tests, and container topology without implementing product features.

### Dependencies

- M0 complete.
- Human approval to begin coding.

### Ownership

- Codex: root/backend/infra/tooling and container setup.
- Cursor: minimal Next.js shell and frontend quality setup.
- OpenCode: optional initial standards review; mandatory if security-sensitive config is introduced.

### Exact tasks

- [ ] M1-T01 Initialize Git metadata if still absent; add safe ignore rules for secrets, build output, exports, local volumes, and tool caches.
- [ ] M1-T02 Create the approved monorepo directories without speculative modules.
- [ ] M1-T03 Pin Python, Node.js, package-manager, Postgres driver, FastAPI, SQLAlchemy, Alembic, Next.js, TypeScript, Tailwind, shadcn/ui, Celery, and Redis client versions after compatibility checks.
- [ ] M1-T04 Configure `uv` for backend dependencies and locked development/test groups.
- [ ] M1-T05 Create FastAPI composition root, configuration validation, safe error envelope, correlation middleware, liveness, and readiness interfaces.
- [ ] M1-T06 Configure async SQLAlchemy application engine against pooled `DATABASE_URL` and Alembic against direct `DATABASE_URL_UNPOOLED`.
- [ ] M1-T07 Initialize Alembic with application-schema ownership conventions and no domain tables yet beyond an optional migration smoke marker.
- [ ] M1-T08 Create Celery application and a non-domain smoke task; keep PostgreSQL out of the smoke task unless testing the configured job session.
- [ ] M1-T09 Create Next.js App Router shell with Tailwind/shadcn baseline, public landing placeholder, health/status development view, and typed FastAPI client seam.
- [ ] M1-T10 Create Dockerfiles and Docker Compose services: Nginx, frontend, backend, Celery worker, Redis.
- [ ] M1-T11 Configure Nginx local routing for `/`, `/api/`, and health without TLS production assumptions.
- [ ] M1-T12 Add backend/frontend test runners, linting, type checks, and one smoke test per process.
- [ ] M1-T13 Add `.env.example` containing names and descriptions only; never real credentials.
- [ ] M1-T14 Add developer commands for install, migrate, run, test, and compose startup.
- [ ] M1-T15 Validate Windows/PowerShell commands used by the team as well as container execution.

### Relevant modules/files

- Root dependency/configuration files and `.gitignore`.
- `backend/src/social_saas/main.py`, `config.py`, `platform/`, Alembic configuration.
- `frontend/app/`, `frontend/lib/`, frontend configuration.
- `infra/nginx/`, Dockerfiles, `docker-compose.yml`.
- Backend/frontend smoke tests.

### Database changes

- Alembic baseline only.
- No application domain schema before M2.
- Migration command must use the direct Neon connection.

### API contracts

- `GET /api/v1/health/live`: process liveness, no dependency details.
- `GET /api/v1/health/ready`: safe readiness summary for database/Redis where appropriate; no credentials or topology leakage.

### External integrations

- Neon Postgres connection only.
- Redis local/private container.
- No Auth, AI, Tavily, Zernio, or S3 calls.

### Automated tests

- FastAPI liveness/readiness tests.
- Configuration rejects missing required variables with safe messages.
- SQLAlchemy connection smoke on a non-production Neon branch.
- Alembic upgrade from empty branch and current-head check.
- Celery smoke task executes through Redis.
- Next.js build/type/lint and public-page render test.
- Docker Compose services become healthy.

### Acceptance criteria

- One documented command starts the local stack.
- Frontend can call FastAPI health through Nginx.
- Backend connects to the non-production Neon branch using pooled connection.
- Alembic applies through direct connection.
- Celery worker consumes a smoke task.
- No secret appears in source, logs, frontend bundle, or committed files.

### Definition of Done

- [ ] Clean install succeeds from repository instructions.
- [ ] Backend tests/lint/type checks pass.
- [ ] Frontend build/tests/lint/type checks pass.
- [ ] Alembic empty-branch verification passes.
- [ ] Docker Compose health passes.
- [ ] Human can reproduce startup.
- [ ] Focused commits are merged through review.

---

## 10. Milestone 2 — Neon Auth and isolated workspace vertical slice

### Objective

Deliver signup/login/logout, JWT-authenticated FastAPI access, and exactly one automatically provisioned private workspace, visible in a minimal authenticated dashboard.

### Dependencies

- M1 complete.
- Neon Managed Auth development branch enabled.
- Google OAuth development credentials/trusted origins available.

### Ownership

- Codex: Neon configuration, FastAPI JWT/JWKS, identity/workspace persistence, migrations, security tests.
- Cursor: auth proxy/client, signup/login/recovery/OAuth UI, protected dashboard, session/loading/error behavior.
- OpenCode: mandatory independent auth and tenant-isolation review.

### Exact tasks

- [ ] M2-T01 Add/review `neon.ts` for `auth: true` and development-branch policy only; do not enable unselected Neon products.
- [ ] M2-T02 Enable Auth on a development branch through a human-approved Neon operation and record branch Auth URL/JWKS variables safely.
- [ ] M2-T03 Install the current supported `@neondatabase/auth` wrapper and implement the Next.js catch-all auth proxy.
- [ ] M2-T04 Implement email/password signup/signin, Google OAuth, email verification, password reset, signout, session restoration, and protected-route UX.
- [ ] M2-T05 Implement JWT acquisition for FastAPI requests using the installed SDK's documented token method.
- [ ] M2-T06 Implement FastAPI bearer verification with EdDSA-capable library, JWKS caching/refresh, issuer, audience if defined, expiry/not-before, and stable subject checks.
- [ ] M2-T07 Create `application_users`, `workspaces`, and initial audit/migration structures defined by architecture.
- [ ] M2-T08 Implement transactional idempotent `resolve_or_provision_workspace` with unique constraints.
- [ ] M2-T09 Implement active account/workspace status dependency used by all private interfaces.
- [ ] M2-T10 Implement `GET /api/v1/me` and `PATCH /api/v1/workspace` timezone.
- [ ] M2-T11 Show authenticated identity/workspace/timezone in minimal dashboard.
- [ ] M2-T12 Register local/preview trusted domains and test callback routing; record production-domain work for M14.
- [ ] M2-T13 Verify signout ends browser session and document that issued JWT expiry/application-status checks handle backend access.
- [ ] M2-T14 Add two-user negative tests across direct IDs and repeated provisioning races.

### Relevant modules/files

- `neon.ts` if selected by setup.
- `frontend/app/api/auth/[...path]/`, auth pages, auth client/server modules, protected layout.
- `backend/src/social_saas/identity/`, `workspaces/`, authentication dependencies.
- Identity/workspace SQLAlchemy models and Alembic revision.
- Auth/security/integration tests.

### Database changes

- `app.application_users`.
- `app.workspaces`.
- Minimum safe `app.audit_events` if audit foundation is included now.
- Unique stable Auth subject and one workspace per user.
- Do not modify Neon-managed `neon_auth` tables with Alembic.

### API contracts

- `GET /api/v1/me`.
- `PATCH /api/v1/workspace`.
- Common `401`, non-disclosing `404`, `409`, and `422` behavior.

### External integrations

- Neon Managed Better Auth.
- Neon JWKS.
- Google OAuth development app.

### Automated tests

- JWT: valid, expired, wrong issuer/audience, unknown/rotated key, invalid signature, unsupported algorithm.
- Provisioning: first login, repeat login, concurrent first requests, rollback on error.
- Authorization: missing token, User A accessing User B workspace/resource placeholder.
- Account status: disabled/deletion-pending user with otherwise valid token is denied.
- Frontend: signup, signin, OAuth return, signout, reload restoration, protected redirect, error/loading states.
- Live development-branch integration: email/password and Google OAuth where credentials permit.

### Acceptance criteria

- Two test users sign up and receive distinct workspaces.
- Repeated/concurrent requests create no duplicate workspace.
- FastAPI never trusts client-supplied workspace identity.
- Direct unauthenticated FastAPI request is denied independently of Next.js route protection.
- Both auth paths reach the authenticated dashboard.
- User A cannot observe User B's workspace identifier/data through product interfaces.

### Definition of Done

- [ ] Auth and workspace migrations pass on a fresh Neon branch.
- [ ] All auth and negative tenant tests pass.
- [ ] Live email/password and Google OAuth flows are recorded as verified or explicitly blocked.
- [ ] OpenCode reports no unresolved critical/high auth or tenant finding.
- [ ] Human verifies both login paths and two-user separation.

---

## 11. Milestone 3 — Brand profile vertical slice

### Objective

Let an authenticated user create, read, and update one reusable workspace-owned brand profile through the real dashboard.

### Dependencies

- M2 complete.

### Ownership

- Codex: brand module, migration, interfaces, authorization tests.
- Cursor: brand form, validation feedback, logo placeholder/selection seam without implementing uploads yet.
- OpenCode: optional unless tenant or asset ownership issues are found.

### Exact tasks

- [ ] M3-T01 Add `brand_profiles` schema and one-per-workspace constraint.
- [ ] M3-T02 Implement Brand module read/update and resolved-context interface.
- [ ] M3-T03 Implement `GET` and `PUT /api/v1/brand-profile`.
- [ ] M3-T04 Validate bounded name, description, website URL, audience, and voice/tone.
- [ ] M3-T05 Build dashboard brand page with saved/dirty/success/error states.
- [ ] M3-T06 Ensure campaign-only override interface can later consume a snapshot without mutating profile.
- [ ] M3-T07 Add User A/User B brand isolation tests.
- [ ] M3-T08 Leave `logo_asset_id` unavailable or clearly pending until M7 rather than faking upload.

### Relevant modules/files

- `backend/src/social_saas/brands/`.
- Brand models/migration/schemas/routes/tests.
- `frontend/features/brand/`, brand route, typed client.

### Database changes

- `app.brand_profiles` with unique `workspace_id`.
- Nullable logo reference added now only if migration ordering is intentionally handled; otherwise add with M7.

### API contracts

- `GET /api/v1/brand-profile`.
- `PUT /api/v1/brand-profile`.

### External integrations

- None.

### Automated tests

- Create/update/read.
- Unique profile under concurrent create/update.
- URL/text validation.
- Cross-workspace known-ID attempts.
- Frontend form persistence and errors.

### Acceptance criteria

- Each user sees and edits only their own profile.
- Refresh preserves saved data.
- Validation gives corrective feedback.
- One profile exists per workspace.

### Definition of Done

- [ ] Migration and tests pass.
- [ ] Frontend calls the real interface.
- [ ] Tenant negatives pass.
- [ ] Human completes the profile flow for two users.

---

## 12. Milestone 4 — Campaign creation and persistent Celery job shell

### Objective

Create campaigns from hybrid input, persist a recoverable background job, dispatch through Celery/Redis, and show truthful progress without AI generation yet.

### Dependencies

- M3 complete.

### Ownership

- Codex: campaign/job schema, dispatch recovery, Celery queues, interfaces, tests.
- Cursor: campaign form, list/detail, job progress polling.
- OpenCode: mandatory concurrency/idempotency/recovery review.

### Exact tasks

- [ ] M4-T01 Add campaigns, background jobs, and AI-run placeholder schema needed for dispatch.
- [ ] M4-T02 Implement hybrid campaign validation for prompt, structured fields, LinkedIn/Instagram, post count, goal, audience, tone, and date range.
- [ ] M4-T03 Persist resolved brand-context snapshot without changing saved profile.
- [ ] M4-T04 Create campaign + job + dispatch marker transactionally.
- [ ] M4-T05 Configure `ai`, `media`, `integrations`, and `maintenance` Celery routes using architecture defaults.
- [ ] M4-T06 Implement post-commit enqueue and stale `dispatch_pending` recovery.
- [ ] M4-T07 Implement atomic job claim/lease, safe stages, heartbeat, terminal state, and cooperative cancellation.
- [ ] M4-T08 Create a deterministic placeholder task that moves a campaign through pending/running/ready without generating fake content.
- [ ] M4-T09 Implement campaign create/list/read and job read/cancel interfaces.
- [ ] M4-T10 Build campaign form/list/detail and job polling UI.
- [ ] M4-T11 Test duplicate HTTP submission, duplicate Celery delivery, crash between commit/enqueue, stale lease, Redis restart, and account inactivity.

### Relevant modules/files

- `backend/src/social_saas/campaigns/`, `jobs/`, Celery composition/task entry points.
- Campaign/job migrations.
- `frontend/features/campaigns/`, job polling client/UI.

### Database changes

- `app.campaigns`.
- `app.background_jobs`.
- Initial `app.ai_runs` linkage if required.
- Indexes for workspace lists, dispatch, leases, and recovery.

### API contracts

- `POST /api/v1/campaigns`.
- `GET /api/v1/campaigns`.
- `GET /api/v1/campaigns/{campaign_id}`.
- `GET /api/v1/jobs/{job_id}`.
- `POST /api/v1/jobs/{job_id}/cancel`.

### External integrations

- Redis/Celery only.

### Automated tests

- Hybrid input and override resolution.
- Transaction rollback and dispatch recovery.
- Duplicate request/task behavior.
- Job state transition/lease/cancellation.
- Cross-workspace campaign/job access.
- Frontend polling termination and failure states.

### Acceptance criteria

- User creates one campaign and sees real persistent job progress.
- Restarting Redis/worker does not lose campaign intent.
- Duplicate dispatch does not create duplicate campaigns/jobs.
- Cancelled/inactive-account work stops at safe checkpoints.

### Definition of Done

- [ ] Migration, Celery integration, and failure tests pass.
- [ ] OpenCode clears job/idempotency architecture.
- [ ] Human observes create → progress → terminal flow through UI.
- [ ] No fake campaign deliverables are presented.

---

## 13. Milestone 5 — LangGraph text campaign generation

### Objective

Replace the placeholder task with a checkpointed LangGraph workflow that produces a strategy and platform-specific text drafts through AI Credits, without research or images yet.

### Dependencies

- M4 complete.
- AI Credits text-model contract spike complete.

### Ownership

- Codex: AI Credits adapter, LangChain structured outputs, LangGraph graph/checkpoints, content persistence.
- Cursor: render strategy/drafts and generation failure/partial states.
- OpenCode: mandatory workflow recovery and deterministic-boundary review.

### Exact tasks

- [ ] M5-T01 Select and record exact AI Credits model IDs and verify structured-output/tool behavior in a non-production spike.
- [ ] M5-T02 Add posts, post versions, AI runs, and controlled LangGraph checkpoint setup/migrations.
- [ ] M5-T03 Define typed graph state and Pydantic outputs for strategy, LinkedIn drafts, Instagram drafts, hashtags, and timing suggestions.
- [ ] M5-T04 Implement nodes: load authorized context, validate, plan, generate platform posts, review, persist.
- [ ] M5-T05 Keep Master/Content/Review as logical responsibilities, not unconstrained agent chats.
- [ ] M5-T06 Implement bounded schema repair and provider retries.
- [ ] M5-T07 Persist each valid output as immutable version 1 in review-required state.
- [ ] M5-T08 Link AI run/thread/checkpoints to job, campaign, and workspace.
- [ ] M5-T09 Implement checkpoint resume after worker interruption and deny cross-workspace thread IDs.
- [ ] M5-T10 Record bounded usage/latency metadata without logging secrets/full private prompts.
- [ ] M5-T11 Render real strategy and draft cards in campaign detail.

### Relevant modules/files

- `backend/src/social_saas/ai/`, `content/`, AI Credits adapter, LangGraph workflows/nodes/state.
- Post/version/AI-run migrations.
- Campaign detail frontend.

### Database changes

- `app.posts`.
- `app.post_versions`.
- `app.ai_runs` final fields.
- Controlled LangGraph checkpoint tables.

### API contracts

- Existing campaign/job reads expand with strategy and draft summaries.
- `POST /api/v1/campaigns/{campaign_id}/retry-generation` for recoverable failed/partial runs.
- `GET /api/v1/posts/{post_id}` read contract begins.

### External integrations

- AI Credits text model.
- PostgreSQL LangGraph checkpointer.

### Automated tests

- Deterministic fake-model graph success.
- Invalid structured output and bounded repair.
- provider timeout/rate limit/permanent error.
- worker interruption/checkpoint resume.
- duplicate task does not duplicate versions.
- cancellation between nodes.
- cross-workspace graph state/tool access denied.
- frontend partial/failure rendering.

### Acceptance criteria

- A real test campaign produces a strategy and distinct LinkedIn/Instagram drafts.
- Drafts are persisted, refreshable, and review-required.
- Interrupted run resumes or fails visibly without duplicate posts.
- AI cannot approve or publish.

### Definition of Done

- [ ] Real AI Credits text generation is integration-verified.
- [ ] Fake-provider test suite is deterministic.
- [ ] Checkpoint recovery is demonstrated.
- [ ] OpenCode clears workflow and tenant findings.
- [ ] Human reviews output for both platforms.

---

## 14. Milestone 6 — Conditional Tavily research and source traceability

### Objective

Add conditional current-information research with retained sources, prompt-injection defenses, and visible references.

### Dependencies

- M5 complete.
- Tavily credentials and limits verified.

### Ownership

- Codex: Tavily adapter, research decision/node, sources schema, safety and tests.
- Cursor: source/reference review UI.
- OpenCode: mandatory prompt-injection and claim/source review.

### Exact tasks

- [ ] M6-T01 Verify Tavily request/response/error/source metadata and define bounded adapter contract.
- [ ] M6-T02 Add research sources and post-version source association tables.
- [ ] M6-T03 Add explicit `decide_research` graph output with reason and safe criteria.
- [ ] M6-T04 Implement bounded query count, result count, excerpt size, timeouts, and retry policy.
- [ ] M6-T05 Treat retrieved text as untrusted data and isolate it from system/tool instructions.
- [ ] M6-T06 Normalize/store URL, title, publisher, dates, excerpt, retrieval time, and source-quality assessment.
- [ ] M6-T07 Associate sources with exact post versions containing research-dependent claims.
- [ ] M6-T08 Review node removes, qualifies, or flags unsupported claims.
- [ ] M6-T09 Show “research used/skipped” and inspectable sources in campaign/post review.
- [ ] M6-T10 Test ordinary saved-brand campaigns skip Tavily.

### Relevant modules/files

- `backend/src/social_saas/research/` and AI research nodes/tools.
- Source migrations and content associations.
- Frontend source panels.

### Database changes

- `app.research_sources`.
- `app.post_version_sources`.

### API contracts

- Campaign/post reads include safe research decision and source metadata.
- No general-purpose browser/search endpoint is exposed.

### External integrations

- Tavily.

### Automated tests

- Research needed/skipped routing.
- Prompt-injection fixtures.
- source deduplication and workspace scoping.
- unsupported-claim handling.
- Tavily timeout/rate-limit/permanent failure.
- UI reference rendering and unsafe-link handling.

### Acceptance criteria

- Current-events request uses retained sources.
- Ordinary brand request skips unnecessary search.
- Unsupported claim is not presented as verified.
- Retrieved content cannot change authorization/tools/publishing behavior.

### Definition of Done

- [ ] Live Tavily request is verified.
- [ ] Injection and tenant tests pass.
- [ ] OpenCode clears high-risk research findings.
- [ ] Human can inspect sources attached to relevant drafts.

---

## 15. Milestone 7 — S3 media, uploads, web-image rights, and AI image quota

### Objective

Deliver secure workspace-owned media paths and concurrency-safe two-generation enforcement.

### Dependencies

- M5 complete; M6 may proceed immediately before or be merged first.
- AWS development S3 bucket/role and AI Credits image contract available.

### Ownership

- Codex: assets/upload intents, S3 adapter, image reservations, image provider adapter, validation, rights state.
- Cursor: upload UI, previews, image-budget display, source/license confirmation.
- OpenCode: mandatory S3 authorization and image-concurrency review.

### Exact tasks

- [ ] M7-T01 Create private development S3 bucket/access policy through approved infrastructure path; block public access.
- [ ] M7-T02 Add assets, upload intents, post-version asset join, and image-generation event schema.
- [ ] M7-T03 Implement server-generated environment/workspace object keys and short-lived presigned upload/access.
- [ ] M7-T04 Implement upload completion verification and bounded file-type/size/dimension/checksum validation.
- [ ] M7-T05 Implement asset ownership authorization for every preview/download.
- [ ] M7-T06 Verify AI Credits image model and identify evidence that provider-side execution started.
- [ ] M7-T07 Implement atomic reservation: reserved + started <= 2.
- [ ] M7-T08 Implement started/completed/failed-before-start/failed-after-start/uncertain transitions and stale-reservation reconciliation.
- [ ] M7-T09 Ensure duplicate Celery delivery reuses the same logical event.
- [ ] M7-T10 Implement web-discovered image record with source/license evidence; do not add a provider until selected/approved.
- [ ] M7-T11 Implement explicit human rights confirmation and reference-only state when evidence is unclear.
- [ ] M7-T12 Add asset selection/removal and optional text-only behavior to post review.
- [ ] M7-T13 Add logo upload integration to brand profile.

### Relevant modules/files

- `backend/src/social_saas/media/`, S3 and image adapters, media tasks.
- Media/image migrations.
- `frontend/features/media/`, brand logo and post media UI.
- `infra/` S3/IAM definitions/scripts when approved.

### Database changes

- `app.assets`.
- `app.upload_intents`.
- `app.post_version_assets`.
- `app.image_generation_events`.
- Campaign counters/check constraints.
- Brand logo asset foreign key if deferred.

### API contracts

- `POST /api/v1/media/upload-intents`.
- `POST /api/v1/media/upload-intents/{intent_id}/complete`.
- `GET /api/v1/media/{asset_id}/access`.
- `POST /api/v1/campaigns/{campaign_id}/image-generations`.
- `POST /api/v1/media/{asset_id}/rights-confirmation`.

### External integrations

- AWS S3.
- AI Credits image model.
- Web-image provider remains pending selection; implement only approved metadata/confirmation seam.

### Automated tests

- Cross-workspace asset/object-key substitution.
- Expired/reused upload intents.
- invalid type/size/content mismatch.
- concurrent three-request race: at most two reach provider start.
- pre-start failure releases reservation.
- post-start failure consumes slot.
- ambiguous start blocks blind retry.
- duplicate Celery delivery does not allocate/call twice.
- unclear web rights cannot become publishable.
- presigned URLs are bounded and not logged.

### Acceptance criteria

- User uploads and previews an owned image; another user cannot access it.
- Campaign can remain text-only.
- At most two provider-started generations occur under concurrency.
- Rights-unclear web image cannot pass publishability.
- Brand logo uses the same ownership controls.

### Definition of Done

- [ ] S3 and image integrations are live-tested in development.
- [ ] Concurrency/security tests pass.
- [ ] OpenCode clears critical/high media findings.
- [ ] Human verifies upload, optional media, image-limit, and rights UX.

---

## 16. Milestone 8 — Post editing, AI revision, versioning, and approval

### Objective

Deliver the human-control core: independent edits, targeted AI revisions, immutable versions, and approval bound to the exact current publishable version.

### Dependencies

- M5 and M7 complete; M6 source associations integrated.

### Ownership

- Codex: Content/Approval module, version transactions, AI revision flow, tests.
- Cursor: editor, version-aware review, approval confirmation, stale/conflict UX.
- OpenCode: mandatory approval-bypass and concurrency review.

### Exact tasks

- [ ] M8-T01 Finalize canonical publishable representation and content-hash algorithm.
- [ ] M8-T02 Implement manual edits as complete immutable version creation.
- [ ] M8-T03 Implement targeted AI revision job using current base version and bounded instruction.
- [ ] M8-T04 Preserve unrelated posts during one-post revision.
- [ ] M8-T05 Implement explicit approval transaction with current-version/hash/asset/source validation.
- [ ] M8-T06 Invalidate prior approval on publishable content, platform, destination-context, hashtag, media, order, or platform-option changes.
- [ ] M8-T07 Preserve approval for schedule-only time/timezone changes.
- [ ] M8-T08 Add optimistic concurrency/current-version checks returning `409`.
- [ ] M8-T09 Build accessible post editor, targeted-revision action, source/media review, version indicator, and approval confirmation.
- [ ] M8-T10 Prevent frontend from presenting approval as authorization; always refetch backend result.

### Relevant modules/files

- `backend/src/social_saas/content/`, AI revision node/task.
- Approval migration if not already created.
- `frontend/features/content-review/`.

### Database changes

- Final `app.approvals`.
- Constraints/indexes on versions/current version/hash.
- Audit events for version/approval/invalidation.

### API contracts

- `GET /api/v1/posts/{post_id}`.
- `POST /api/v1/posts/{post_id}/versions`.
- `POST /api/v1/posts/{post_id}/ai-revisions`.
- `POST /api/v1/posts/{post_id}/approvals`.

### External integrations

- AI Credits for targeted revision only.

### Automated tests

- edit one post leaves others unchanged.
- stale base version and concurrent editors.
- approval hash/version mismatch.
- every material field invalidates old approval.
- schedule-only change does not invalidate approval.
- invalid/unclear asset blocks approval or later publishability according to finalized rule.
- AI task cannot create approval.
- cross-workspace edit/approve denied.
- UI conflict/refetch and explicit confirmation.

### Acceptance criteria

- User edits one post or requests AI revision without losing other posts.
- New version requires explicit approval.
- Approved version/hash is auditable.
- Stale approval cannot authorize a different version.

### Definition of Done

- [ ] Version/approval migration and tests pass.
- [ ] OpenCode finds no approval bypass.
- [ ] Human demonstrates manual edit, AI revision, stale conflict, and approval.
- [ ] Architecture invariants are traceable in tests.

---

## 17. Milestone 9 — Zernio profile and LinkedIn/Instagram connections

### Objective

Provision one Zernio profile per workspace and connect/list/disconnect workspace-owned LinkedIn and Instagram accounts without publishing yet.

### Dependencies

- M2 complete; M8 preferred before publishing work.
- Zernio non-production account and platform test accounts.

### Ownership

- Codex: Zernio adapter, profile/account schema, connection interfaces, webhook foundation.
- Cursor: connections UI and provider-return states.
- OpenCode: mandatory tenant/profile/account substitution review.

### Exact tasks

- [ ] M9-T01 Verify Zernio profile creation/retry and platform connection contracts against live non-production account.
- [ ] M9-T02 Add Zernio profile and social account tables.
- [ ] M9-T03 Implement idempotent one-profile-per-workspace using opaque workspace ID as `externalId`.
- [ ] M9-T04 Implement LinkedIn/Instagram connection URL generation scoped to stored profile.
- [ ] M9-T05 Implement callback/webhook account-connected/disconnected handling through the signed webhook foundation.
- [ ] M9-T06 Store only necessary provider metadata; no browser/provider secrets.
- [ ] M9-T07 Implement connection list/status and explicit disconnect.
- [ ] M9-T08 Add connection UI with platform, account identity, active/attention/disconnected/unknown states.
- [ ] M9-T09 Test profile/account substitution and reconnect account-ID changes.

### Relevant modules/files

- `backend/src/social_saas/social/` Zernio adapter/profile/account/webhook ingress.
- Zernio migrations.
- `frontend/features/connections/`.

### Database changes

- `app.zernio_profiles`.
- `app.social_accounts`.
- Initial `app.webhook_receipts` if not deferred to M10.

### API contracts

- `POST /api/v1/social/connections`.
- `GET /api/v1/social/accounts`.
- `DELETE /api/v1/social/accounts/{account_id}`.
- `POST /webhooks/zernio` foundation.

### External integrations

- Zernio profiles/connections/webhooks.
- LinkedIn and Instagram OAuth/provider flows through Zernio.

### Automated tests

- profile idempotency and workspace mapping.
- known account/profile ID from another workspace.
- invalid HMAC and duplicate account events.
- reconnect/disconnect transitions.
- frontend callback/error/attention states.

### Acceptance criteria

- Each of two users has a distinct Zernio profile.
- LinkedIn and Instagram test accounts connect to the correct workspace.
- User A cannot list/use/disconnect User B's account.
- Invalid webhook cannot change connection state.

### Definition of Done

- [ ] Live profile and both connection flows verified or a documented provider blocker stops M10.
- [ ] OpenCode clears tenant/webhook issues.
- [ ] Human validates connection UX for both platforms.

---

## 18. Milestone 10 — Zernio scheduling, publishing, webhooks, and manual retry

### Objective

Complete the controlled publishing loop for approved LinkedIn/Instagram content.

### Dependencies

- M7–M9 complete.
- Zernio media/scheduling/cancellation/retry contracts verified.

### Ownership

- Codex: submission state, media handoff, idempotency, scheduling, unscheduling, webhooks, reconciliation, manual retry.
- Cursor: schedule/reschedule/unschedule/manual-retry UI and truthful state/error display.
- OpenCode: mandatory adversarial publishing/webhook/race review.

### Exact tasks

- [ ] M10-T01 Verify live Zernio create/schedule/media/cancel/reschedule/failed-retry/lookup behavior for LinkedIn and Instagram.
- [ ] M10-T02 Add submissions, attempts, platform results, and final webhook-receipt schema.
- [ ] M10-T03 Implement eligibility snapshot: workspace, current version, valid approval/hash, destination, platform, media rights/validation, timezone/time.
- [ ] M10-T04 Persist submission and stable Zernio idempotency key before provider call.
- [ ] M10-T05 Implement private S3-to-Zernio media upload/handoff and provider media reference persistence.
- [ ] M10-T06 Implement schedule/create with timeout/uncertain outcome reconciliation.
- [ ] M10-T07 Implement schedule-only change preserving approval using direct provider reschedule or tested cancel/recreate fallback.
- [ ] M10-T08 Implement unschedule lock: editing remains blocked until cancellation is confirmed.
- [ ] M10-T09 Implement raw-body HMAC-SHA256 verification and constant-time compare.
- [ ] M10-T10 Deduplicate stable event ID in PostgreSQL before asynchronous processing; return timely `2xx` after durable receipt.
- [ ] M10-T11 Translate platform-level scheduled/published/failed/partial events through valid monotonic state transitions.
- [ ] M10-T12 Implement explicit user-initiated retry for confirmed failed eligible outcomes only.
- [ ] M10-T13 Ensure webhook redelivery never triggers publication retry.
- [ ] M10-T14 Build scheduling confirmation, destination/timezone, uncertain, partial, failed, unschedule, and manual-retry UX.
- [ ] M10-T15 Test edit-versus-publish, reschedule, disconnect, duplicate request/event, timeout-after-provider-side-effect, and out-of-order webhook races.

### Relevant modules/files

- Social Publishing module/adapters/tasks/routes.
- Publishing migrations.
- `frontend/features/calendar/`, scheduling and status UI.

### Database changes

- `app.publishing_submissions`.
- `app.publishing_attempts`.
- `app.provider_platform_results`.
- Final `app.webhook_receipts` indexes/state.

### API contracts

- `POST /api/v1/posts/{post_id}/schedule`.
- `PATCH /api/v1/publishing/{submission_id}/schedule`.
- `POST /api/v1/publishing/{submission_id}/unschedule`.
- `POST /api/v1/publishing/{submission_id}/retry`.
- `POST /webhooks/zernio` complete contract.

### External integrations

- Zernio post/media/scheduling/webhook APIs.
- LinkedIn and Instagram test publication.
- AWS S3 media handoff.

### Automated tests

- unapproved/stale/other-workspace submission blocked.
- content edit while scheduled blocked.
- confirmed unschedule unlocks edit; failure keeps lock.
- schedule-only change preserves approval.
- same idempotency key/replayed request creates one provider post.
- invalid/duplicate/out-of-order webhook behavior.
- partial platform result aggregation.
- timeout/uncertain reconciliation.
- manual retry requires user and eligible failed state.
- webhook retry does not republish.
- deletion/disconnection race prevents unsafe new submission.

### Acceptance criteria

- Approved test posts schedule and publish to LinkedIn and Instagram.
- Failed/partial/uncertain states are truthful.
- Editing follows unschedule → edit → reapprove → reschedule.
- Duplicate client/task/webhook activity creates no unintended duplicate post.
- Failed publishing retries only after user action.

### Definition of Done

- [ ] Live end-to-end provider flow works for both platforms and representative media.
- [ ] All race/idempotency tests pass.
- [ ] OpenCode clears critical/high publishing findings.
- [ ] Human verifies schedule, outcome, unschedule/edit cycle, and manual retry behavior.

---

## 19. Milestone 11 — Dashboard, calendar, and end-to-end UX consolidation

### Objective

Turn the accumulated slices into a coherent, accessible, responsive product journey without adding features.

### Dependencies

- M3–M10 complete.

### Ownership

- Cursor: primary implementation.
- Codex: contract/performance fixes and backend list/query support.
- OpenCode: independent functional/accessibility/regression review.

### Exact tasks

- [ ] M11-T01 Finalize authenticated navigation: overview, brand, campaigns, campaign review, calendar, connections, settings.
- [ ] M11-T02 Build truthful dashboard summaries from real interfaces; no fabricated analytics.
- [ ] M11-T03 Complete campaign list/detail and per-post review workflow.
- [ ] M11-T04 Complete calendar/scheduled list with timezone and destination.
- [ ] M11-T05 Standardize loading, empty, partial, failed, uncertain, stale-session, and degraded-provider states.
- [ ] M11-T06 Apply private-data `no-store`/safe cache behavior and mutation refetch rules.
- [ ] M11-T07 Add keyboard navigation, focus, labels, status announcements, contrast, and responsive layouts.
- [ ] M11-T08 Test long text, missing images, multiple errors, LinkedIn/Instagram differences, and mobile overflow.
- [ ] M11-T09 Optimize only evidenced slow list/query/render paths.

### Relevant modules/files

- `frontend/app/(workspace)/`, `features/`, shared components and HTTP client.
- Backend list/query handlers and indexes only where proven needed.

### Database changes

- None expected; add indexes only from observed query evidence with migration/tests.

### API contracts

- Existing list/detail/status interfaces; no new product surface unless required for an approved view.

### External integrations

- Existing Auth, AI, S3, and Zernio behavior through FastAPI.

### Automated tests

- Critical frontend routes and interactions.
- authenticated/unauthenticated routing.
- stale `409` refetch behavior.
- job polling and terminal states.
- schedule/approval/media-rights control visibility.
- responsive and accessibility checks supported by selected tools.

### Acceptance criteria

- A user completes signup → brand → campaign → review → approval → schedule → status without direct URL knowledge.
- No screen implies unavailable analytics or success.
- Desktop/tablet/mobile remain usable.
- Keyboard and status/error flows are accessible.

### Definition of Done

- [ ] Frontend build/test/lint/type checks pass.
- [ ] Integrated browser flow passes with real backend.
- [ ] OpenCode/human review clears blocking UX/accessibility issues.
- [ ] No placeholder or fabricated product state remains.

---

## 20. Milestone 12 — Export, account deletion, and retention

### Objective

Implement the approved simple lifecycle: pre-deletion export, immediate access/session/connection revocation, cancellation, 30-day recovery, primary purge, and 35-day backup-expiry target.

### Dependencies

- M10 complete so schedules/connections can be cancelled.
- M11 settings UX available.

### Ownership

- Codex: export/deletion modules, jobs, S3 packaging/purge, provider cleanup, tests.
- Cursor: export/deletion confirmation/status UX.
- OpenCode: mandatory destructive-flow, security, and retention review.

### Exact tasks

- [ ] M12-T01 Add data exports, account deletions, legal holds, and required audit schema.
- [ ] M12-T02 Implement versioned export manifest with structured workspace data and owned media, excluding secrets.
- [ ] M12-T03 Store export privately with short-lived authorized download and expiry cleanup.
- [ ] M12-T04 Require export to be requested/downloaded before deletion if the user wants it; do not create an inaccessible post-revocation export UX.
- [ ] M12-T05 Implement deletion transaction marking user/workspace inactive and setting 30-day purge timestamp.
- [ ] M12-T06 Immediately deny valid JWT access through application status.
- [ ] M12-T07 Request Neon session revocation using verified mechanism.
- [ ] M12-T08 Mark pending/running jobs cancel requested and stop at safe checkpoints.
- [ ] M12-T09 Cancel all non-terminal Zernio schedules and disconnect accounts; retry external cleanup without restoring access.
- [ ] M12-T10 Implement controlled support/runbook restore within 30 days; require fresh auth and reconnection; do not recreate schedules/jobs.
- [ ] M12-T11 Implement idempotent purge after 30 days for application rows, checkpoints, exports, and owned S3 media.
- [ ] M12-T12 Preserve published social posts and minimal non-content purge evidence.
- [ ] M12-T13 Implement narrowly scoped legal hold record/runbook, not a generalized rules engine.
- [ ] M12-T14 Verify/document Neon and AWS backup expiry capabilities relative to the 35-day target.

### Relevant modules/files

- `backend/src/social_saas/retention/`, cleanup/export tasks.
- Retention migrations.
- Settings/export/delete frontend.
- Operational runbooks in the approved documentation/infra area if later authorized.

### Database changes

- `app.data_exports`.
- `app.account_deletions`.
- `app.legal_holds`.
- Final `app.audit_events`.
- Status/purge fields and indexes.

### API contracts

- `POST /api/v1/exports`.
- `GET /api/v1/exports/{export_id}`.
- `POST /api/v1/account-deletion`.
- Restoration remains controlled operational flow unless separately approved.

### External integrations

- Neon Auth revocation.
- Zernio cancellation/disconnect.
- S3 export and purge.
- Neon/AWS backup policy verification.

### Automated tests

- export includes owned data/media and excludes secrets/other tenants.
- deletion immediately denies a still-valid JWT.
- pending jobs and schedules receive cancellation.
- cleanup retries idempotently.
- 29-day restore versus 30-day purge boundary using controlled clock.
- published posts unaffected.
- legal hold retains only scoped records.
- S3 objects and checkpoints purge with account.

### Acceptance criteria

- User downloads a valid basic export before deletion.
- Deletion immediately blocks application access.
- Schedules/jobs/connections cancel or show operator-visible cleanup failure.
- Controlled restore works inside 30 days.
- Purge removes primary data/media after 30 days.
- Backup expiry capability is verified or transparently recorded as an exception/risk.

### Definition of Done

- [ ] Destructive/recovery tests pass.
- [ ] OpenCode clears critical/high findings.
- [ ] Human performs export and test-account deletion flow.
- [ ] Retention evidence and unresolved provider limitations are documented.

---

## 21. Milestone 13 — Security, reliability, and release-candidate validation

### Objective

Produce a release candidate that satisfies architecture invariants and PRD hard gates before production deployment.

### Dependencies

- M2–M12 complete.

### Ownership

- Codex: fixes, integration/failure suites, operational instrumentation.
- Cursor: frontend regressions/accessibility fixes.
- OpenCode: mandatory independent full review and adversarial test pass.
- Human: product acceptance.

### Exact tasks

- [ ] M13-T01 Run traceability review from PRD requirements/acceptance criteria to tests and implemented interfaces.
- [ ] M13-T02 Execute cross-tenant matrix across HTTP, lists, tasks, LangGraph threads, S3, Zernio mappings, webhooks, exports, and deletion.
- [ ] M13-T03 Execute approval/version/schedule race suite.
- [ ] M13-T04 Execute image-budget concurrent/ambiguous provider suite.
- [ ] M13-T05 Execute Celery duplicate, crash, Redis restart, dispatch-gap, cancellation, and stale-lease recovery.
- [ ] M13-T06 Execute webhook signature, replay, duplicate, out-of-order, partial, and delayed-event cases.
- [ ] M13-T07 Verify rate limits/usage bounds for auth, campaign generation, research, images, uploads, scheduling, webhooks, and exports.
- [ ] M13-T08 Verify structured logging/correlation and secret/private-content redaction.
- [ ] M13-T09 Verify database indexes/query plans for critical lists and worker claims using Neon development diagnostics.
- [ ] M13-T10 Run frontend browser/accessibility/responsive suite.
- [ ] M13-T11 Perform two-user staging end-to-end acceptance with LinkedIn/Instagram test accounts.
- [ ] M13-T12 Produce release candidate evidence and unresolved-risk list.

### Relevant modules/files

- Tests across backend/frontend/infra; only evidence-backed fixes to product code.

### Database changes

- No feature schema changes expected.
- Index/constraint corrections require normal migration review.

### API contracts

- Frozen except for backward-compatible corrections required to satisfy approved architecture.

### External integrations

- Full staging integration set.

### Automated tests

- Full unit, integration, contract, security, worker, frontend, and E2E suites.
- Migration from fresh database and representative prior schema.
- Container build and staging smoke.

### Acceptance criteria

- PRD hard gates pass.
- No unresolved critical/high security or correctness finding.
- Two isolated real users complete full flow.
- Failed/uncertain states are truthful.
- Duplicate/publication/image/tenant invariants hold under concurrency.

### Definition of Done

- [ ] OpenCode independent review is complete.
- [ ] All blocking findings fixed and retested.
- [ ] Human accepts product behavior.
- [ ] Release candidate is tagged or otherwise frozen for M14 deployment.

---

## 22. Milestone 14 — AWS deployment, CI/CD, backup, and production acceptance

### Objective

Deploy the accepted release candidate to the finalized single-EC2 topology with controlled migrations, secrets, HTTPS, monitoring, backups, and rollback/recovery evidence.

### Dependencies

- M13 release candidate accepted.
- AWS/domain/production provider credentials and human deployment approval.

### Ownership

- Codex: infrastructure, Nginx, containers, GitHub Actions, migrations, health, backup/recovery automation and runbooks.
- Cursor: production frontend configuration and post-deploy UI verification.
- OpenCode: mandatory deployment/security/config review.
- Human: production secrets, approvals, OAuth/provider setup, DNS, final acceptance.

### Exact tasks

- [ ] M14-T01 Provision/configure EC2, security group, IAM role, private S3 bucket, and AWS Secrets Manager through approved repeatable process.
- [ ] M14-T02 Configure production Docker Compose networks, health checks, restart policies, resource awareness, and persistent Redis/log storage.
- [ ] M14-T03 Configure Nginx HTTPS, HTTP redirect, route/body/timeout limits, headers, and webhook raw-body compatibility.
- [ ] M14-T04 Configure production Neon pooled application and direct migration connections in protected secrets.
- [ ] M14-T05 Configure production Neon Auth trusted domain, Google OAuth app, email verification/password reset, and required custom SMTP checklist.
- [ ] M14-T06 Configure production AI Credits, Tavily, Zernio, webhook secret/URL, S3, and AWS permissions without exposing values.
- [ ] M14-T07 Create GitHub Actions stages: dependency restore, lint/type/test, security tests, container builds, protected deploy, one Alembic migration step, service start/update, health/smoke, failure report.
- [ ] M14-T08 Ensure production Alembic uses direct URL and runs exactly once under protected environment approval.
- [ ] M14-T09 Implement worker drain/restart and stale-job reconciliation during deployment.
- [ ] M14-T10 Configure structured log retention, disk alerts, process/worker/queue/database/provider health signals, and secret redaction.
- [ ] M14-T11 Verify Neon restore/history capability and S3 backup/version/lifecycle policy against RPO and deletion requirements.
- [ ] M14-T12 Perform restore drill and document reconciliation of jobs, Zernio state, and deletion records.
- [ ] M14-T13 Verify recommended V1 RTO 8 hours and RPO maximum 24 hours or document measured limits.
- [ ] M14-T14 Execute post-deploy two-user smoke including real Auth and controlled Zernio flow.
- [ ] M14-T15 Record single-instance limitations and operator recovery steps.

### Relevant modules/files

- `infra/**`.
- Dockerfiles/Compose/Nginx.
- `.github/workflows/**`.
- Safe environment examples and operational runbooks if authorized.
- No product feature expansion.

### Database changes

- Apply already accepted migrations only.
- No manual production DDL.

### API contracts

- No contract changes expected.

### External integrations

- AWS EC2/S3/Secrets Manager/IAM/DNS/TLS.
- Neon production branch/Auth.
- GitHub Actions.
- AI Credits, Tavily, Zernio production configuration.

### Automated tests

- CI full suite.
- container image/startup/health tests.
- migration dry run on Neon branch before production.
- deployment smoke and rollback/failure behavior.
- backup restore drill.
- production-safe end-to-end smoke.

### Acceptance criteria

- HTTPS application is reachable and healthy.
- Secrets are absent from source, images, logs, and frontend.
- Migrations are controlled and reproducible.
- Worker/job recovery works across deployment.
- Monitoring identifies critical dependency/process failures.
- Backup/restore evidence exists.
- Two users complete the production acceptance flow without leakage or unsafe publishing.

### Definition of Done

- [ ] OpenCode clears deployment/security review.
- [ ] Human approves protected deployment and smoke evidence.
- [ ] Restore drill and recovery targets are recorded.
- [ ] Known single-host limitations are accepted.
- [ ] V1 release is tagged and operational handoff is complete.

---

## 23. Cross-milestone test architecture

### 23.1 Test suites

| Suite | Runs when | Responsibility |
|---|---|---|
| Backend unit/module | Every backend change | Fast domain behavior through module interfaces |
| Database integration | Every schema/repository change | Real Postgres constraints, transactions, concurrency |
| Migration | Every Alembic revision | Fresh upgrade, current-to-head upgrade, reviewed downgrade/roll-forward behavior |
| API integration | Every route/contract change | Auth, validation, errors, ownership, lifecycle |
| Security/tenant | Every private-resource milestone and full CI gate | Known-ID, list/count, nested, task/tool/provider substitution |
| AI workflow | M5 onward | Fake providers, graph routes, checkpoints, cancellation, structured output |
| Celery/Redis | M4 onward | Dispatch, duplicate, retry, lease, cancellation, Redis failure |
| Provider contract | Provider milestones and scheduled checks | Real non-production Neon/AI/Tavily/Zernio/S3 assumptions |
| Frontend component/interaction | Every UI change | Forms, loading/error, keyboard, state behavior |
| Browser E2E | Each vertical slice and M13/M14 | Integrated user journeys |
| Recovery | M4, M10, M12, M14 | Crash, ambiguous side effect, restore, purge |

### 23.2 Critical tests that may never be skipped

- User A cannot access User B data through any known identifier or indirect path.
- Valid JWT for deletion-pending user is denied.
- Concurrent signup provisions one workspace.
- Duplicate task does not duplicate posts, versions, image calls, or provider submissions.
- Third provider-started image generation is impossible.
- Material content change invalidates approval; schedule-only change does not.
- Unapproved/stale content cannot schedule.
- Scheduled content cannot edit before confirmed unschedule.
- Invalid/duplicate webhook causes no duplicate transition.
- Webhook retry does not cause publishing retry.
- Manual retry requires authenticated user action and eligible failed state.
- Cross-workspace S3/Zernio mapping substitution fails.
- Account deletion immediately blocks access and eventually purges primary data/media.

---

## 24. Milestone handoff template

Every agent handoff includes:

```text
Milestone/task:
Objective achieved:
Files changed:
Database migration:
Interfaces changed:
External integration exercised:
Tests run and results:
Security/tenant checks:
Known limitations:
Review findings resolved:
Acceptance evidence:
Recommended next task:
```

Claims such as “auth works,” “publishing works,” or “deletion works” must name the exact live/test flow exercised.

---

## 25. Dependency and risk register

| Risk/dependency | Milestone deadline | Mitigation |
|---|---:|---|
| Managed Auth incompatible with chosen network protection | M0/M2 | Verify AWS-region project and Auth restrictions before setup |
| Next.js/Neon Auth SDK version drift | M1/M2 | Pin tested versions; follow current official quickstart/installed types |
| FastAPI JWT claim/JWKS mismatch | M2 | Live token contract test before dependent private interfaces |
| Unsafe production access by agents | M0/M1 | Non-production branches, project/read-only MCP, protected CI production secrets |
| Migration uses pooled URL | M1 onward | Separate `DATABASE_URL_UNPOOLED`; CI assertion/review |
| DB-to-Redis dispatch gap | M4 | Persistent dispatch marker and recovery test |
| AI Credits structured/image behavior differs | M5/M7 | Adapter spikes and contract fixtures before broad implementation |
| Prompt injection through research | M6 | Untrusted-data isolation, allowlisted tools, adversarial fixtures |
| Image provider start is ambiguous | M7 | Reservation remains occupied until reconciliation |
| Approval/publish race | M8/M10 | Immutable versions, current/hash checks, schedule locks, transaction tests |
| Zernio platform/media/cancel behavior differs | M9/M10 | Live LinkedIn/Instagram contract spike; no invented fallback |
| Duplicate/late webhook | M10 | HMAC, unique event ID, monotonic/idempotent transitions |
| Deletion cleanup external failure | M12 | Access remains blocked; durable retry and operator visibility |
| Backup expiry cannot meet 35 days | M12/M14 | Verify plans/capabilities; document legal/technical exception truthfully |
| Single EC2 outage | M14 | Accepted V1 limitation, backups, reproducible host, restore drill |
| Large AI-generated change set | Every milestone | Small task branches, tests, fixed ownership, independent review |

---

## 26. Plan consistency review

### 26.1 Source-of-truth review

The milestone plan was checked against:

- the V1 scope and exclusions in `PRODUCT_OVERVIEW.md`;
- functional requirements, state behavior, acceptance criteria, and hard gates in `docs/PRODUCT_REQUIREMENTS.md`;
- finalized technologies and provider verification status in `docs/TECH_STACK.md`;
- modules, tables, interfaces, failure states, retention, and deployment topology in `docs/ARCHITECTURE.md`;
- tenant, approval, image-budget, and verification rules in `AGENTS.md`.

### 26.2 Coverage result

| Architecture/product area | Milestone coverage |
|---|---|
| Repository/development environment | M1 |
| Neon branches, pooled/direct connections, migrations | M0–M2 and every schema milestone |
| Neon Auth/workspace/tenant isolation | M2, reinforced M13 |
| Brand profile | M3 |
| Campaign/job foundation | M4 |
| LangGraph/AI Credits | M5 |
| Tavily research | M6 |
| S3/images/rights/two-event cap | M7 |
| Editing/versioning/approval | M8 |
| Zernio profiles/connections | M9 |
| Scheduling/publishing/webhooks/retry | M10 |
| Integrated dashboard/calendar | M11 |
| Export/deletion/retention | M12 |
| Full security/reliability acceptance | M13 |
| AWS deployment/CI/CD/recovery | M14 |

No approved V1 area is intentionally omitted, and no excluded product feature is introduced.

### 26.3 Ordering review

The order is deliberate:

- authentication and workspace isolation precede all private resources;
- persistent jobs/recovery precede real AI work;
- AI text behavior precedes research and image cost/risk;
- media eligibility and versioning precede publishing;
- Zernio account mapping precedes scheduled submissions;
- publishing behavior exists before deletion must cancel it;
- full hardening precedes production deployment.

Frontend work is included in each vertical slice, with M11 reserved for consolidation rather than first integration.

### 26.4 Missing dependencies and unresolved verification

The plan cannot pre-confirm:

- exact installed package/runtime versions;
- the user's Neon project/network configuration;
- AI Credits model contracts;
- Tavily plan limits;
- Zernio plan/platform/media/cancellation/retry details beyond documented capabilities;
- AWS region, domain, EC2 size, and backup implementation;
- whether Neon/AWS backup expiry can meet the 35-day target.

M0 assigns these dependencies, and the relevant milestone refuses to claim completion without evidence.

### 26.5 Plan readiness

The plan is ready for approval and implementation sequencing. It does not authorize implementation by itself. The next action after approval is Milestone 0 readiness confirmation followed by the first development milestone below.

---

## 27. Recommended first development milestone

The exact first development milestone is **Milestone 1 — Executable repository and development foundation**, after the brief human/provider readiness checks in Milestone 0.

Why this first:

- the repository currently contains documentation only;
- every later slice depends on compatible runtime/tool versions and a reproducible local stack;
- it proves pooled application versus direct migration connections before schema work;
- it proves FastAPI, Next.js, Redis/Celery, Nginx, tests, and Docker Compose without mixing in product complexity;
- it establishes file ownership and verification commands for Codex, Cursor, and OpenCode.

### First milestone Definition of Done

- [ ] Approved monorepo directories exist with no product over-scaffolding.
- [ ] Python/Node/package-manager and core dependency versions are pinned and locked.
- [ ] FastAPI liveness/readiness interfaces pass tests.
- [ ] Next.js public shell builds and reaches FastAPI through local Nginx.
- [ ] SQLAlchemy connects to a non-production Neon branch using pooled URL.
- [ ] Alembic uses the direct URL and applies successfully to a fresh branch.
- [ ] Redis and Celery execute a smoke task.
- [ ] Docker Compose starts all selected V1 processes with health checks.
- [ ] Backend and frontend lint/type/test/build checks pass.
- [ ] `.env.example` documents required names without secrets.
- [ ] No real credential is committed or emitted to client/logs.
- [ ] Human reproduces the documented startup and approves moving to M2.


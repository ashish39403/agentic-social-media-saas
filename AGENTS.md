# Project Instructions

## Product source of truth

- Read `PRODUCT_OVERVIEW.md` before proposing or changing product behavior.
- Read `docs/PRODUCT_REQUIREMENTS.md` before implementation planning or coding.
- Read `docs/TECH_STACK.md` for finalized technology ownership, `docs/ARCHITECTURE.md` for system boundaries, and `docs/IMPLEMENTATION_PLAN.md` for milestone order and Definition of Done.
- Treat confirmed decisions in those documents as constraints. Do not silently replace them.
- When the documents differ, `PRODUCT_OVERVIEW.md` controls confirmed product intent; record and resolve the inconsistency before implementation.

## Scope discipline

- V1 is a private, single-user workspace product. Do not add teams, invitations, shared roles, multiple workspaces, or multiple saved brand profiles.
- Every post requires explicit approval of its current content before scheduling or publishing.
- A material post change invalidates approval and requires reapproval.
- Enforce the maximum of two AI image-generation events per campaign in application logic; regenerations count.
- Treat web-discovered images as references unless usage rights are sufficiently established and the user approves their use.
- Do not invent unconfirmed providers, supported social channels, quotas, pricing, analytics, infrastructure, or implementation frameworks.
- Preserve the boundary between probabilistic AI work and deterministic application controls. AI may recommend; application code must enforce authorization, budgets, approvals, scheduling eligibility, and publishing idempotency.

## Security and tenancy

- Scope every workspace-owned read and write on the server/data-access boundary.
- Apply the same ownership checks to user requests, agent tools, background work, media, social credentials, and publishing callbacks.
- Never use a client-side filter as the security boundary.
- Never expose provider credentials, social tokens, private research context, or another workspace's identifiers or content.

## Change process

- Keep confirmed decisions, proposed defaults, and open questions visibly separate in product documentation.
- Update requirement IDs and the traceability matrix when changing V1 behavior.
- Add or revise acceptance criteria for every behavioral requirement change.
- Surface conflicts and unresolved product choices instead of guessing.
- Preserve unrelated user work.

## Verification expectations

- Verify implementation changes with proportionate automated tests and relevant runtime checks.
- Include negative tenant-isolation tests, approval-gate tests, image-budget tests, and duplicate-publishing tests for affected flows.
- Do not claim end-to-end completion from unit tests or mocks alone; verify the deployed integration path before launch.

## Architecture and ownership

- Keep the system a Next.js frontend plus FastAPI modular monolith and separate Celery worker. Do not introduce microservices or substitute finalized providers.
- Codex owns `backend/**`, database migrations, AI workflows, provider adapters, and `infra/**`. Cursor owns `frontend/**`. OpenCode reviews completed changes read-only.
- Shared files require one named owner. Never let two agents edit the same file simultaneously.
- Freeze an API contract before frontend integration. Backend behavior, OpenAPI output, and frontend types must agree; the browser never becomes an authorization boundary.

## Database and integrations

- Manage application schema only through reviewed Alembic revisions. Never alter Neon's managed `neon_auth` schema.
- Use pooled `DATABASE_URL` for FastAPI and Celery; use direct `DATABASE_URL_UNPOOLED` for Alembic and administrative operations.
- Use Neon branches for development and migration rehearsal. Neon MCP is limited to explicitly authorized development resources; never use it against production or permit unrestricted agent mutations.
- Keep external providers behind adapters. Validate timeouts, signatures, idempotency keys, duplicate events, and failure states without inventing undocumented capabilities.

## Delivery workflow

- Execute one approved milestone at a time: Select Milestone → Define API Contracts → Implement → Integrate → Test → Review → Fix → Verify → Commit.
- Give every task one owner and bounded files. Parallel implementation requires separate Git worktrees created from the same reviewed base.
- Use `milestone/<id>-<slug>` for integration branches and `feat/<id>-<slug>` or `fix/<id>-<slug>` for task branches. Do not merge until the milestone's acceptance criteria and Definition of Done pass.
- The original implementation owner fixes valid review findings. OpenCode reports findings with severity, file, line, impact, and recommended fix; it does not modify files.
- Never commit credentials, tokens, `.env` files, provider payloads containing secrets, or production connection strings.


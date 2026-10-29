# AI Social Media SaaS — Technical Stack and Architecture Specification

| Field | Value |
|---|---|
| Document status | Architecture baseline for detailed design and implementation planning |
| Version | 1.0 |
| Prepared | 29 October 2026 |
| Product authority | `PRODUCT_OVERVIEW.md` and `docs/PRODUCT_REQUIREMENTS.md` |
| Technology authority | `TECH_VERVIEW.md` and the confirmed clarifications recorded in this document |
| Implementation status | Pre-implementation; no production integration has been validated end to end |

> This document defines the selected V1 technology stack, component responsibilities, system boundaries, integration flows, and architecture constraints. It is not application code, an API contract, a database schema, or a deployment runbook. Product behavior remains governed by the PRD.

---

## 1. Purpose and decision language

The product is a production-oriented, multi-tenant AI social media SaaS for individual users. It must combine a secure personal workspace, reusable brand context, AI-assisted campaign creation, conditional web research, optional visual content, per-post human approval, Zernio-managed scheduling and publishing, and truthful publishing status.

This specification has four decision labels:

| Label | Meaning |
|---|---|
| **Confirmed** | The technology or architecture direction is finalized for V1. |
| **Documentation-verified** | The capability is supported by cited official provider documentation, but the application has not yet proven it in a live integration. |
| **Recommendation** | A concrete implementation direction consistent with the finalized stack; it may be refined during detailed design without replacing the stack. |
| **Pending verification** | A provider, operational, or implementation detail that must be tested or decided before the affected capability is considered complete. |

The document does not treat a provider's documented behavior as proof that credentials, account configuration, plan entitlements, platform-specific constraints, or our integration are working correctly.

---

## 2. Architecture goals and constraints

### 2.1 Goals

1. Preserve strict workspace isolation across HTTP requests, database queries, AI tools, Celery tasks, Redis messages, S3 objects, Zernio profiles, and webhooks.
2. Keep human approval as a deterministic gate before any post is submitted for immediate or scheduled publishing.
3. Run long AI and media operations outside request-response lifetimes.
4. Make PostgreSQL the durable source of truth for product, workflow, and job state.
5. Use explicit, retry-safe workflows for operations that may execute more than once.
6. Support a complete V1 on one EC2 host without prematurely introducing microservices or managed orchestration platforms.
7. Keep provider-specific behavior behind application-owned interfaces so future changes do not leak across the domain model.
8. Make failures, partial outcomes, and uncertain publishing outcomes observable and recoverable.

### 2.2 Constraints

- V1 is a modular monolith, not a microservice system.
- One authenticated user owns one application workspace.
- One workspace owns one saved brand profile.
- Zernio owns scheduled publishing execution; Celery does not wake up at publish time.
- Celery and Redis handle application background work such as AI generation and asynchronous webhook processing.
- The application may submit only a currently approved post revision to Zernio.
- AI image generation is capped at two accepted generation events per campaign, including regenerations.
- Web-discovered images are not publishable merely because they were found online.
- The initial deployment is a single EC2 server and is not highly available.
- Exact social platforms, AI model identifiers, provider plan limits, instance sizing, and several detailed policies remain pending verification.

---

## 3. Finalized technology stack

| Layer | Technology | Status | Primary responsibility |
|---|---|---|---|
| Web application | Next.js + TypeScript | Confirmed | Public site and authenticated product experience |
| UI | Tailwind CSS + shadcn/ui | Confirmed | Styling, accessible primitives, and reusable interface composition |
| API/backend | FastAPI + Python | Confirmed | Authenticated APIs, authorization, domain logic, integrations, and webhook ingress |
| Backend structure | Modular monolith | Confirmed | Cohesive deployable with internal domain-module boundaries |
| Validation | Pydantic | Confirmed by FastAPI stack | Request, response, configuration, and structured boundary validation |
| Relational database | Neon PostgreSQL | Confirmed | Durable application source of truth |
| Authentication | Neon Managed Better Auth | Confirmed | Signup, login, Google OAuth, verification, reset, sessions, and logout |
| ORM | SQLAlchemy 2.x | Confirmed | Explicit transactional relational persistence |
| Migrations | Alembic | Confirmed | Versioned application-schema evolution |
| AI integration | LangChain | Confirmed | Model adapters, tools, prompts, and structured output integration |
| AI orchestration | LangGraph | Confirmed | Stateful, explicit campaign workflow graph |
| Model gateway | AI Credits | Confirmed | Access to selected text and image models |
| Web research | Tavily | Confirmed provider selection | Current-information search and source retrieval |
| Image model | AI Credits-supported model | Model pending | AI image generation within campaign budget |
| Task processing | Celery | Confirmed | Durable-at-application-level background execution and retries |
| Broker | Redis | Confirmed | Celery task transport |
| Celery result backend | Redis | Confirmed | Short-lived task execution results and Celery coordination |
| Persistent job state | PostgreSQL | Confirmed | User-visible and recoverable background-job record |
| Social integration | Zernio | Confirmed | Account connections, provider profiles, post submission, scheduling, and publishing outcomes |
| Media storage | AWS S3 | Confirmed | Private storage for logos, uploads, and generated assets |
| Compute | AWS EC2 | Confirmed | Initial application host |
| Containerization | Docker + Docker Compose | Confirmed | Reproducible service packaging and single-host orchestration |
| Edge proxy | Nginx | Confirmed | TLS termination/reverse proxying and request routing |
| HTTPS | TLS certificate | Confirmed | Encrypted public transport |
| CI/CD | GitHub Actions | Confirmed | Automated checks, builds, and controlled EC2 deployment |
| Version control | Git + GitHub | Confirmed | Source history and delivery trigger |

No additional framework, queue, database, object store, cloud orchestration platform, or observability vendor is selected by this document.

---

## 4. System context and trust boundaries

```text
┌──────────────────────────────── User device ────────────────────────────────┐
│ Browser: Next.js UI, authenticated session context, no provider secrets      │
└───────────────────────────────────┬───────────────────────────────────────────┘
                                    │ HTTPS
                                    v
┌──────────────────────────── AWS EC2 trust zone ─────────────────────────────┐
│ Nginx                                                                     │
│   ├── Next.js frontend                                                    │
│   └── FastAPI backend                                                     │
│         ├── modular domain services                                       │
│         ├── Zernio webhook ingress                                        │
│         ├── Celery task producer                                          │
│         └── provider adapters                                             │
│                                                                            │
│ Redis (private Docker network) <──────> Celery worker                       │
│                                            ├── LangGraph workflows          │
│                                            ├── LangChain tools              │
│                                            └── media/background processing  │
└───────────────┬─────────────────────┬──────────────────┬────────────────────┘
                │ TLS                 │ TLS              │ TLS
                v                     v                  v
       Neon PostgreSQL             AWS S3         External providers
       + Neon Auth                                ├── AI Credits
                                                  ├── Tavily
                                                  └── Zernio → social platforms
```

### 4.1 Trust-boundary rules

- The browser is untrusted. Workspace IDs, resource IDs, approval flags, image counts, and provider identifiers supplied by the client are claims to validate, not authorization facts.
- FastAPI is the application authorization boundary. It derives the authenticated identity and workspace from trusted session verification and application-owned mappings.
- PostgreSQL is the durable product-state authority. Redis and Celery metadata do not replace it.
- Celery tasks are untrusted inputs at execution time because messages may be stale, duplicated, or tampered with if infrastructure is compromised. Workers must reload and reauthorize durable records.
- Provider webhooks are untrusted until cryptographically verified and deduplicated.
- Retrieved web pages and model output are untrusted data. They must never be interpreted as system instructions or authorization decisions.
- S3 possession does not imply workspace authorization. Object keys and presigned URLs must be issued only after application authorization.

---

## 5. Request, job, and publishing data flows

### 5.1 Interactive request flow

```text
Browser
  → Nginx
  → Next.js or FastAPI
  → authenticate session
  → resolve application identity and workspace
  → authorize requested resource/action
  → execute domain service transaction
  → return workspace-scoped response
```

FastAPI must not accept a `workspace_id` from the client as proof of scope. If a workspace identifier is present for routing or consistency checking, it must match the server-derived workspace.

### 5.2 Campaign generation flow

```text
User submits campaign
  → FastAPI validates input and workspace ownership
  → PostgreSQL transaction creates campaign + persistent job
  → after commit, enqueue Celery task with opaque job/campaign IDs
  → Celery worker reloads job, campaign, and workspace
  → worker claims idempotent execution
  → LangGraph runs campaign workflow
       ├── optional Tavily research
       ├── AI Credits text-model calls
       ├── optional image generation through AI Credits
       └── deterministic validation/review checkpoints
  → PostgreSQL stores strategy, sources, post revisions, assets, progress, errors
  → frontend reads user-visible status from FastAPI/PostgreSQL
```

The enqueue operation occurs only after the database transaction commits. Detailed design must select a reliable database-to-broker handoff pattern; an application-level dispatch marker or equivalent recovery mechanism is recommended so a process crash between commit and enqueue does not strand a job.

### 5.3 Scheduling and publishing flow

```text
User approves current post revision
  → user selects destination and schedule
  → FastAPI reloads authoritative state
  → validate workspace, revision, approval, media, account, and time
  → create local publishing submission and stable idempotency key
  → call Zernio create-post/schedule API
  → persist Zernio post reference and accepted provider state
  → Zernio owns future scheduled execution
  → Zernio sends signed webhook outcome(s)
  → FastAPI verifies and durably records webhook receipt
  → Celery processes event asynchronously when work exceeds acknowledgement path
  → PostgreSQL updates provider/platform outcome
  → dashboard shows reconciled state
```

Because Zernio owns the scheduled execution, the application's final approval and authorization gate occurs before the schedule is handed to Zernio. The submitted payload must represent an immutable approved revision snapshot. Editing the application post later creates or selects a different revision; it must not mutate the already scheduled payload silently. Cancellation/replacement behavior for an already submitted schedule remains a detailed workflow decision and must be tested against Zernio.

### 5.4 Webhook ingestion flow

```text
Zernio webhook
  → Nginx
  → FastAPI webhook endpoint
  → read raw request bytes
  → verify HMAC-SHA256 signature
  → validate envelope and event type
  → insert stable event ID into unique-indexed receipt table
       ├── duplicate: return 2xx without reapplying effect
       └── new: persist receipt/payload or required normalized fields
  → return 2xx within provider deadline
  → enqueue/trigger Celery processing if non-trivial
  → resolve Zernio profile/account/post mapping
  → verify workspace association
  → apply idempotent state transition
```

If the application cannot durably accept a new event, it should not acknowledge success merely to suppress a retry. Payload retention must follow the final privacy and retention policy.

---

## 6. Frontend architecture

### 6.1 Responsibilities

Next.js and TypeScript implement:

- public landing and authentication entry points;
- signup/login, email verification, password reset, Google OAuth return, logout, and session-aware routing;
- authenticated dashboard and first-use onboarding;
- brand-profile management;
- Zernio account-connection initiation and status display;
- hybrid campaign creation with prompt and structured fields;
- generation progress and recoverable failure states;
- campaign strategy and independent post review;
- manual editing, targeted AI revision requests, image selection, and approval;
- calendar/scheduled-post presentation;
- publishing and connection state presentation;
- workspace settings relevant to the individual workspace model.

Tailwind CSS supplies styling utilities. shadcn/ui supplies composable UI source components and accessible primitives; it does not define domain behavior.

### 6.2 Frontend boundaries

The frontend must not:

- connect directly to PostgreSQL, Redis, Celery, AI Credits, Tavily, or privileged S3 APIs;
- hold service API keys, Zernio API keys, webhook secrets, database credentials, or AWS credentials;
- authorize workspace access based on hidden fields or client-side filtering;
- decide whether a post is approved or publishable;
- enforce the two-image campaign limit as the only control;
- trust task-result data directly from Redis;
- interpret provider callbacks as authoritative without FastAPI processing.

### 6.3 Data-fetching and progress strategy

The exact Next.js rendering mode, client-state library, caching policy, and progress transport are not finalized. V1 may use authenticated HTTP reads with polling for long-running jobs; real-time WebSockets or another event service are not selected and must not be introduced without a decision. Whatever mechanism is chosen, PostgreSQL-backed application status remains authoritative.

### 6.4 Browser security

- Use the secure session mechanism supported by Neon Auth and the selected FastAPI verification pattern.
- Protect cookie-based state-changing requests against cross-site request forgery where applicable.
- Avoid placing session credentials or sensitive provider data in browser storage when secure HTTP-only cookie/session patterns are available.
- Enforce a restrictive content security policy during deployment design.
- Render model and research output as data; never inject unsanitized HTML.
- Do not expose private S3 object URLs permanently.

The exact Next.js version, Node.js version, package manager, route layout, rendering strategy, and frontend test tools remain pending implementation decisions.

---

## 7. Backend architecture

### 7.1 Modular monolith

FastAPI is one deployable backend with explicit internal modules. This avoids distributed transactions and service-to-service operational complexity while preserving seams that can be extracted only if real scale or team boundaries justify it.

Recommended logical modules:

```text
backend
├── identity              session verification and application identity mapping
├── workspaces            provisioning and tenant resolution
├── brands                reusable brand profile and campaign overrides
├── campaigns             campaign request and lifecycle
├── content               posts, revisions, approval, and review
├── research              Tavily adapter and source records
├── ai                    LangChain integrations and LangGraph workflows
├── media                 S3, uploads, provenance, and image budget
├── social                Zernio profiles, accounts, submissions, and webhooks
├── jobs                  persistent jobs, dispatch, progress, and recovery
└── platform              configuration, database, logging, errors, and health
```

These are Python module boundaries, not network services.

### 7.2 Layering recommendation

Each module should separate:

1. **API boundary:** FastAPI routes, authentication dependency, request/response schemas.
2. **Application service:** use-case coordination and transaction boundaries.
3. **Domain rules:** approval validity, budgets, state transitions, and invariants.
4. **Persistence:** SQLAlchemy repositories/queries scoped by workspace.
5. **Provider adapter:** AI Credits, Tavily, S3, or Zernio-specific transport and translation.

Routes should not contain provider orchestration or direct ad hoc queries. Provider response shapes should not become the application's domain model.

### 7.3 API behavior

- Use versioned HTTP API routes; the exact URL convention is pending.
- Validate inputs and outputs with Pydantic.
- Use opaque application identifiers and never reveal cross-tenant existence through different authorization errors.
- Make mutation endpoints retry-aware where duplicate client submissions are plausible.
- Return a persistent application job identifier for long-running generation requests.
- Treat partial campaign success and uncertain provider outcomes as explicit states, not generic success/failure booleans.
- Keep provider error bodies out of public responses unless normalized and safe.

The exact REST resource contract, pagination, error envelope, correlation header, rate-limit policy, and API versioning convention remain pending detailed design.

---

## 8. Authentication and application identity

### 8.1 Final provider and V1 methods

Neon Managed Better Auth is the selected identity provider. V1 includes:

- email/password signup and login;
- Google OAuth;
- email verification;
- password reset;
- secure session lifecycle;
- logout.

Exact SDK/API usage and FastAPI verification must follow current official Neon Auth guidance at implementation time.

### 8.2 Identity boundary

Authentication proves who the user is. The application database determines what that identity owns.

Recommended mapping:

```text
Neon Auth stable subject/identity
        │
        v
application user identity row
        │ one-to-one in V1
        v
application workspace
```

Do not use email address as the authorization key. Email can change and may have normalization or provider-linking semantics. Store the stable external identity reference required by Neon Auth and enforce uniqueness in application data.

### 8.3 Workspace provisioning

Workspace provisioning must be idempotent:

1. verify the authenticated Neon Auth identity;
2. look up or create the application identity mapping;
3. look up or create exactly one personal workspace under a uniqueness constraint;
4. create required baseline records in the same transaction where practical;
5. return the existing workspace on repeated callbacks or requests.

An OAuth callback, browser retry, or concurrent first request must not create multiple workspaces.

### 8.4 Pending authentication verification

- session verification mechanism available to FastAPI;
- signing key/JWKS or managed-session validation behavior;
- cookie domains and same-site policy across deployment hostnames;
- session expiry, renewal, revocation, and logout propagation;
- account linking between password and Google identities;
- email-verification enforcement behavior;
- password-reset callback and redirect rules;
- local and automated integration-test strategy.

Authentication is incomplete until both browser flows and protected FastAPI routes are tested end to end.

---

## 9. Multi-tenant isolation model

### 9.1 Tenant authority

The application workspace is the canonical tenant boundary. Zernio profiles, S3 prefixes, campaign/job context, and agent execution are subordinate mappings; none may independently authorize access.

### 9.2 Database isolation

Every workspace-owned record must contain or resolve an unambiguous `workspace_id`. All reads and mutations must scope by both resource identifier and authorized workspace.

Required patterns:

- load resources through workspace-scoped repository methods;
- use composite uniqueness constraints where uniqueness is tenant-local;
- include workspace ownership in nested-resource joins;
- prevent changing a record's workspace association through ordinary updates;
- protect bulk operations, exports, callbacks, and administrative scripts with the same boundary;
- test known-ID attacks, list leakage, count leakage, indirect joins, and job substitution.

Database row-level security is not a finalized stack decision. Application-level authorization in FastAPI remains mandatory whether or not database policies are later added.

### 9.3 Celery isolation

Celery messages should carry only the minimum identifiers needed to reload work, such as `job_id`, not complete credentials or trusted serialized domain objects. On execution, a worker must:

1. load the persistent job;
2. resolve its workspace and target resource;
3. verify their relationship;
4. acquire the task's idempotency/claim control;
5. load current allowed credentials and inputs server-side;
6. execute and persist scoped results.

A task must never accept a workspace identifier and an unrelated resource identifier without verifying the relationship.

### 9.4 Zernio tenant mapping

Zernio's multi-tenant model is documentation-verified: one profile can represent each customer, connected accounts are placed in that profile, and webhook payloads can carry the configured profile `externalId`. The recommended V1 mapping is one Zernio profile per application workspace, with the application workspace's stable opaque identifier used as the Zernio `externalId`.

FastAPI still enforces authorization. A matching `externalId`, `profileId`, or `accountId` from the browser or webhook is routing data, not sufficient authorization. Before submitting a post, FastAPI must verify that the stored Zernio account belongs to the current workspace's stored Zernio profile.

Actual profile creation, reconnect behavior, plan entitlements, and profile/account isolation must be proven in integration tests.

### 9.5 S3 isolation

- Use a private bucket with public access blocked.
- Namespace object keys by environment and workspace using server-generated paths.
- Treat the prefix as organization, not authorization.
- Persist asset ownership and object key in PostgreSQL.
- Authorize the asset record before issuing a short-lived presigned operation.
- Validate uploads before marking an asset eligible for use.
- Ensure task roles/credentials grant only necessary bucket actions.
- Never accept an arbitrary object key from a user and sign it without ownership validation.

---

## 10. Database and persistence architecture

### 10.1 Neon PostgreSQL responsibilities

PostgreSQL stores durable application state, including:

- application identity and workspace mappings;
- brand profiles and campaign-specific overrides;
- campaigns, generation requests, and strategy output;
- research sources and claim/source associations;
- posts and immutable or versioned post revisions;
- approval records bound to exact revisions;
- image-generation budget events;
- media metadata, provenance, and publishability state;
- Zernio profile/account mappings;
- publishing submissions, idempotency keys, provider post references, and outcomes;
- persistent jobs, attempts, progress, and errors;
- webhook receipts and deduplication records;
- security-relevant audit facts required by the PRD.

Neon Auth-managed identity data remains provider-managed. Application-owned tenancy and domain data remain in application tables.

### 10.2 SQLAlchemy 2.x

Use SQLAlchemy 2.x explicit session and transaction patterns. Avoid hidden global sessions. HTTP requests and Celery tasks need separate, bounded session lifecycles.

Recommended transaction principles:

- keep external API calls outside long database transactions;
- persist intent before invoking a non-transactional external side effect;
- store the stable idempotency key before the Zernio request;
- use database constraints as the final guard for uniqueness and counters;
- use row locking, compare-and-swap, or an equivalent atomic database mechanism for concurrency-sensitive state;
- record enough state to reconcile after a process crashes between provider response and local update.

### 10.3 Alembic

- All application-schema changes use versioned Alembic migrations.
- Production deployment must not run uncontrolled auto-create behavior.
- Migrations need forward/rollback or roll-forward recovery planning appropriate to data risk.
- Destructive migrations require explicit backup and compatibility planning.
- Application rollout and migration ordering must support the single-host deployment without silently losing data.

### 10.4 Core invariants

The detailed schema is pending, but it must enforce:

- at most one V1 workspace per application identity;
- at most one saved brand profile per workspace;
- every campaign, post, asset, social mapping, job, and publishing record belongs to one workspace;
- approval references one exact post revision;
- only the current approved revision is eligible for a new publishing submission;
- at most two accepted AI image-generation events per campaign;
- a stable local idempotency identity exists per logical Zernio post creation;
- each Zernio webhook event ID is processed no more than once per receiving integration/environment;
- provider identifiers needed for reconciliation are unique in their correct scope.

### 10.5 Connection behavior pending design

The pooled versus direct Neon connection configuration, pool sizes for FastAPI and Celery, transaction isolation choices, statement timeouts, backup/restore process, and branching/migration workflow must be selected and load-tested. Worker concurrency must not exceed practical database connection capacity.

---

## 11. AI orchestration architecture

### 11.1 Division of responsibility

| Concern | Owner |
|---|---|
| Workflow routing and resumable logical state | LangGraph |
| Model/tool adapters and structured model interactions | LangChain |
| Text and image model access | AI Credits |
| Current-information retrieval | Tavily |
| Task execution and retries around workflow runs | Celery |
| Durable campaign, post, job, and audit state | PostgreSQL |
| Authorization, approval, budgets, and publishing eligibility | Deterministic FastAPI/domain services |

LangGraph state is workflow context, not the tenant authorization source. LangGraph checkpoints, if used, must not replace domain records or introduce another unselected persistence service.

### 11.2 Recommended campaign graph

```text
load_authorized_context
        ↓
validate_campaign_request
        ↓
plan_campaign
        ↓
decide_research ── no ───────────────────┐
        │ yes                            │
        v                                │
research_with_tavily                     │
        ↓                                │
validate_and_store_sources               │
        └────────────────────────────────┤
                                         v
                              generate_platform_posts
                                         ↓
                              review_structured_output
                                         ↓
                               decide_visuals_per_post
                                  ├── none/upload/web suggestion
                                  └── AI generation through budget gate
                                         ↓
                              persist_reviewable_revisions
                                         ↓
                                      complete
```

Logical “Master,” “Research,” “Content,” and “Review” agents describe responsibilities. They do not require independent chat loops or separate model processes. Prefer explicit graph nodes and typed state over unconstrained agent-to-agent conversation.

### 11.3 Structured outputs

Model outputs that feed application state should use validated structured schemas for:

- strategy summary;
- research decision and reason;
- source-linked claims where applicable;
- post text, hashtags, target platform, and timing recommendation;
- review findings and revision instructions;
- visual recommendation and rationale.

Schema validation failure must not create an approved or publishable record. Repair/retry limits must be bounded to prevent runaway model cost.

### 11.4 Research safety

Tavily is invoked only when the graph's research decision determines current or external facts are needed. Research tools must have bounded calls and input lengths. Retrieved text is untrusted content and must not override system instructions, request credentials, call arbitrary tools, or change authorization scope.

Store source URL and useful attribution metadata with the research finding. The exact source-quality rubric, recency rules, excerpt retention, request budget, and Tavily plan limits remain pending verification.

### 11.5 Human-in-the-loop boundary

LangGraph may pause after producing reviewable drafts, but approval is an application domain action performed by the authenticated user through FastAPI. A model cannot approve content. A post revision's approval is invalidated by a material change according to the product policy.

### 11.6 AI Credits boundary

AI Credits is the finalized gateway. The application should isolate it behind text-model and image-model adapters rather than spreading provider-specific request formats through graph nodes.

Pending verification:

- exact model IDs;
- structured-output and tool-calling compatibility;
- streaming availability if desired;
- timeout and rate-limit semantics;
- usage reporting and cost metadata;
- image-generation endpoint and supported parameters;
- content-safety behavior;
- data retention and provider terms.

No model capability should be assumed from generic OpenAI-compatible text semantics.

---

## 12. Image and media architecture

### 12.1 Supported paths

1. AI-generated image through an AI Credits-supported model.
2. User upload stored privately in S3.
3. Web-discovered suggestion with source and rights metadata.
4. Text-only post.

### 12.2 Two-event budget

The maximum of two AI image-generation events is a campaign-wide business invariant. It must be enforced before invoking the paid provider, across users' clicks, graph nodes, task retries, and concurrent requests.

Recommended enforcement:

1. start a short PostgreSQL transaction;
2. lock or atomically update the campaign budget state;
3. verify the campaign has fewer than two consumed events;
4. create a unique generation-event record with request identity;
5. commit the accepted event;
6. invoke the image provider outside the transaction;
7. update that event with outcome and asset metadata.

Celery redelivery must reuse the same generation-event identity and must not consume another slot for the same logical attempt. The product must still decide whether a provider-rejected request that never begins generation consumes a slot; this policy is explicitly pending.

### 12.3 S3 object lifecycle

Recommended flow:

```text
authorized upload/generation
  → server allocates workspace-scoped object key
  → upload object privately
  → validate declared and detected type, size, dimensions, and integrity
  → persist asset metadata and provenance in PostgreSQL
  → mark review/publishability state
  → issue short-lived access only when authorized or required by integration
```

Exact bucket layout, regions, maximum sizes, allowed formats, malware/image-safety scanning, lifecycle expiration, deletion, and backup policy are pending decisions.

### 12.4 Zernio media handoff

The application must use the media-upload/access pattern supported by Zernio rather than assuming a private S3 URL is directly usable. If a presigned URL is used, its lifetime must cover provider retrieval without creating long-lived public access. Actual behavior must be verified with each initial platform's constraints.

### 12.5 Web-image rights

Web discovery does not grant publishing rights. Store source and available license/usage information. Assets with insufficient rights evidence remain suggestions and cannot pass the deterministic publishability gate. The exact discovery provider and rights-confirmation UX are unresolved.

---

## 13. Background processing with Celery and Redis

### 13.1 Responsibilities

Celery executes:

- campaign-generation workflows;
- Tavily research as part of the workflow;
- AI image generation;
- targeted post revision jobs;
- upload/media processing when necessary;
- non-trivial webhook processing after durable receipt;
- reconciliation or recovery jobs explicitly initiated by application logic.

Celery does not own scheduled social publication. Zernio does.

### 13.2 Redis roles

Redis is both the Celery broker and Celery result backend in V1. It is not the durable product database and must not be the only location for user-visible job state, approvals, image counts, webhook deduplication, or publishing outcomes.

Redis runs on the private Docker network and must not expose its port publicly.

### 13.3 Persistent job model

Before enqueueing work, FastAPI creates a PostgreSQL job record containing at least:

- job identifier and type;
- workspace and target resource relationship;
- requested-by identity;
- lifecycle state;
- logical request/idempotency identity;
- attempt/progress information suitable for users and operators;
- safe error category and timestamps.

Celery task IDs may be recorded for diagnostics but must not become the product job identifier.

### 13.4 Retry and idempotency rules

- Retry only errors classified as transient.
- Bound maximum attempts and execution time.
- Use backoff appropriate to provider limits.
- Recheck durable state before each side effect.
- Ensure repeated execution either returns the existing result or safely resumes.
- Never repeat a paid image-generation call merely because a worker lost its acknowledgement; reconcile the existing logical event first.
- Never create a second Zernio post for the same logical submission; reuse its stored idempotency key within the documented provider window and reconcile thereafter.
- Record permanent failure and expose a safe user recovery path.

### 13.5 Celery Beat

Celery Beat is not required for initial post scheduling because Zernio owns scheduled publishing. This does not prohibit future operational reconciliation tasks, but adding Beat or another scheduler requires a specific need and decision.

### 13.6 Pending worker decisions

- Celery and Redis versions;
- queue names and routing;
- worker concurrency and process model;
- acknowledgement mode and prefetch settings;
- soft/hard time limits;
- Redis persistence configuration;
- dead-letter/failed-job operational process;
- graceful deployment shutdown and in-flight task handling;
- dispatch recovery after database commit;
- retention of Redis result data.

These must be load- and failure-tested on the selected EC2 size.

---

## 14. Zernio integration

### 14.1 Final responsibility boundary

Zernio is the selected unified social integration and owns:

- multi-tenant provider profiles;
- social account connection under those profiles;
- receiving approved post submissions;
- provider-managed scheduling;
- scheduled publishing to supported social accounts;
- publishing lifecycle events delivered by webhook.

FastAPI owns:

- workspace authorization;
- the mapping between workspace and Zernio profile/account records;
- post revision and approval validity;
- media publishability;
- schedule-request validation before handoff;
- creation and persistence of the logical submission/idempotency key;
- webhook verification, deduplication, workspace routing, and local state transitions;
- truthful dashboard state and user recovery actions.

Celery owns asynchronous application work around the integration, but not Zernio's scheduled execution.

### 14.2 Documentation-verified capabilities

The following are verified against official Zernio documentation as of 29 October 2026:

- `scheduledFor` supports provider-managed scheduled publishing; `publishNow` supports immediate publication.
- One Zernio profile per customer is the documented multi-tenant pattern; `externalId` can map the profile to an application customer/workspace.
- Post creation accepts an `Idempotency-Key`; reusing a key for the same logical post within the documented 24-hour window returns the original post rather than creating another.
- Webhook deliveries can be signed with lowercase hexadecimal HMAC-SHA256 of the raw request body using the configured endpoint secret.
- Each event carries a stable event ID in the payload and `X-Zernio-Event-Id`; it is the deduplication key across retries/redelivery.
- Webhook delivery is at least once and can make up to seven attempts, counting the first, when an endpoint does not return `2xx` within five seconds.

References:

- [Zernio webhooks](https://docs.zernio.com/webhooks)
- [Zernio multi-tenant architecture](https://docs.zernio.com/multi-tenant)
- [Zernio create-post API](https://docs.zernio.com/posts/create-post)

These capabilities remain pending live integration testing with the application's Zernio account and initial platforms.

### 14.3 Idempotent post submission

For each logical scheduled/immediate post submission:

1. create the local publishing-submission record;
2. bind it to the exact approved post revision and workspace-owned destination;
3. generate and persist one stable idempotency key before the provider call;
4. send the same key on retries of that logical submission;
5. store the returned Zernio post identifier and normalized state;
6. reconcile timeout/connection-loss cases before creating a different logical submission.

An idempotency key must never be reused for a different post revision or destination. Because the documented key window is 24 hours, recovery outside that window requires explicit reconciliation rather than blind resubmission.

### 14.4 Webhook security and processing

- Configure a high-entropy webhook secret through secure deployment configuration.
- Read raw bytes before parsing JSON.
- Compute HMAC-SHA256 over those exact raw bytes and compare the lowercase hexadecimal signature using a constant-time comparison.
- Reject missing or invalid signatures without processing.
- Validate expected event envelope and type.
- Deduplicate using the stable event ID with a PostgreSQL unique constraint.
- Do not use the event ID as an account, post, or workspace identifier.
- Resolve profile/account/post references through stored mappings and verify workspace consistency.
- Persist enough information to audit and reconcile the transition.
- Return `2xx` within five seconds only after the event is durably accepted; defer non-trivial processing to Celery.

### 14.5 Webhook delivery retry versus failed-post retry

These are different mechanisms:

- **Webhook delivery retry:** Zernio retries delivering the same event notification to our endpoint, up to seven attempts. The stable event ID allows deduplication.
- **Failed-post publishing retry:** A social platform publication failed and someone or some system chooses whether to attempt publication again. This is not automatically authorized by webhook redelivery.

V1 must not interpret a repeated `post.failed` webhook as an instruction to republish. The failed-post retry policy, user confirmation requirements, provider endpoint behavior, and reuse/new-idempotency-key behavior remain pending implementation decisions.

### 14.6 Pending Zernio integration verification

- API credentials and plan entitlements;
- exact initial platforms and account limits;
- real profile creation/retry behavior;
- OAuth/connect redirect flow and account reconnection;
- platform-specific text, hashtag, media, and scheduling constraints;
- timezone and past-time behavior adopted by the product;
- actual signature verification with raw FastAPI request bytes;
- seven-attempt webhook behavior in a controlled failure test where feasible;
- event ordering and platform-level partial outcomes;
- cancellation, rescheduling, and editing of scheduled posts;
- media upload/retrieval behavior with private S3 assets;
- reconciliation APIs and behavior after ambiguous create-post outcomes;
- failed-post retry workflow;
- rate limits, timeouts, and production error shapes.

---

## 15. AWS S3

### 15.1 Responsibilities

S3 stores binary media:

- brand logos;
- user-uploaded images;
- AI-generated images;
- other approved V1 image assets.

PostgreSQL stores the metadata, ownership, provenance, rights state, status, and S3 object key.

### 15.2 Security baseline

- Block public access at bucket/account level as appropriate.
- Use TLS for all access.
- Use least-privilege AWS credentials available only to required backend/worker services.
- Do not embed permanent AWS credentials in images, containers, GitHub, or source files.
- Authorize before issuing presigned URLs.
- Keep presigned expirations short and purpose-specific.
- Validate content type independently of the browser-provided value.
- Prevent object-key traversal/substitution.
- Separate deployment environments by bucket or rigorously isolated prefix and credentials; final choice pending.

S3 server-side encryption configuration, versioning, lifecycle rules, retention, deletion, CORS, and backup requirements remain pending detailed deployment design.

---

## 16. AWS EC2 and deployment architecture

### 16.1 Initial topology

One EC2 instance runs Docker Compose services:

```text
nginx
frontend
backend
celery-worker
redis
```

External managed dependencies are Neon PostgreSQL/Neon Auth, AWS S3, AI Credits, Tavily, Zernio, and connected social platforms.

### 16.2 Nginx and TLS

Nginx is the public ingress and reverse proxy. It should:

- expose only HTTPS publicly, with HTTP redirected to HTTPS;
- route frontend, API, and webhook paths deliberately;
- enforce appropriate body-size and timeout limits by route;
- preserve required forwarding headers safely;
- avoid buffering/transforming webhook bodies in a way that breaks raw-body signature verification;
- apply security headers selected during deployment hardening;
- keep backend, worker, and Redis ports private.

Certificate issuer and renewal mechanism are pending. “TLS certificate” is finalized; a specific certificate service is not.

### 16.3 Docker Compose

- Build immutable application images.
- Separate frontend, backend, worker, Redis, and Nginx processes.
- Use health checks and restart policies appropriate to each service.
- Keep configuration outside images.
- Use private networks for internal services.
- Persist Redis data only according to the finalized queue-recovery strategy.
- Do not rely on container filesystem for durable uploads or database state.
- Ensure worker and backend run the same compatible application release during deployment transitions.

### 16.4 Single-server trade-off

Benefits:

- low operational complexity;
- low initial cost;
- simple deployment and debugging;
- appropriate for a V1 demonstration and early users.

Limitations:

- EC2 host failure affects web, API, worker, and Redis simultaneously;
- deployments can interrupt in-flight requests/tasks without careful draining;
- CPU/memory contention between Next.js, FastAPI, Redis, and AI workers;
- no horizontal scaling or high availability;
- Redis availability is coupled to the host;
- maintenance creates a larger blast radius.

ECS, managed Redis, load balancers, auto-scaling, Kubernetes, and multi-node designs are not selected. They should be considered only after measured demand or reliability requirements justify them.

### 16.5 Pending deployment decisions

- AWS region and EC2 instance family/size;
- operating system/base image and patching process;
- domain/DNS and TLS issuance/renewal;
- inbound firewall/security-group rules;
- AWS identity/credentials delivery to containers;
- secrets injection and rotation procedure;
- persistent volumes and Redis recovery settings;
- zero/minimal-downtime deployment and worker draining;
- rollback procedure;
- host backup and disaster-recovery objectives;
- staging environment strategy;
- log retention and disk-usage controls.

---

## 17. CI/CD with GitHub Actions

### 17.1 Pipeline responsibilities

```text
push / approved merge
  → dependency installation from locked manifests
  → frontend lint/type/build checks
  → backend lint/type/test checks
  → security and tenant-boundary tests
  → container builds
  → publish or transfer immutable artifacts
  → controlled EC2 deployment
  → controlled Alembic migration
  → service health checks
  → report success/failure
```

Exact linters, type checkers, test frameworks, container registry, and deployment transport are not finalized by the source report and must be selected without adding unnecessary infrastructure.

### 17.2 Deployment safety

- Protect production deployment with branch/environment controls.
- Store deployment credentials in protected GitHub environment secrets, not repository files.
- Pin action versions and dependency lockfiles.
- Build once and deploy the same artifact.
- Run database migrations in one controlled step, not concurrently in every container.
- Fail visibly when migration or health verification fails.
- Define rollback compatibility between application and database changes.
- Do not expose provider keys in CI logs.

---

## 18. Security architecture

### 18.1 Required controls

| Area | Required control |
|---|---|
| Identity | Verify Neon Auth session through documented server-side mechanism |
| Authorization | Derive workspace in FastAPI; scope every private operation |
| Database | Parameterized SQLAlchemy access, constraints, least-privilege credentials |
| Background work | Reload and reauthorize resources; idempotent task execution |
| Webhooks | Raw-body HMAC verification, stable-event-ID deduplication, safe routing |
| Social publishing | Revision-bound approval and workspace-owned Zernio account mapping |
| S3 | Private bucket, authorized short-lived access, validated uploads |
| AI tools | Explicit allowlist, validated inputs/outputs, no secrets, no authorization decisions |
| Research | Treat retrieved content as hostile/untrusted data |
| Secrets | Environment/deployment-managed, rotated, never committed or logged |
| Logging | Structured but redacted; no tokens, passwords, secrets, or unnecessary private content |
| Abuse | Rate limits and bounded model/search/image/task usage; exact limits pending |

### 18.2 Approval safety

- Store approval against the exact current revision or content fingerprint.
- Public text, hashtags, media, or factual-claim changes invalidate approval according to the product policy.
- FastAPI rechecks approval immediately before submitting the immutable revision snapshot to Zernio.
- A client-supplied `approved=true` field never authorizes publishing.
- AI agents and Celery tasks cannot create an approval record on behalf of the user.
- Scheduled content already handed to Zernio must be cancelled/replaced through a defined workflow if the user wants different public content.

### 18.3 Threats requiring explicit tests

- insecure direct object reference across workspaces;
- workspace ID substitution in nested routes and task payloads;
- S3 object-key or presigned-URL substitution;
- Zernio profile/account substitution;
- forged, replayed, duplicated, or cross-environment webhook;
- signature verification performed on reserialized rather than raw bytes;
- stale post revision published after edit;
- concurrent third image generation;
- duplicate Celery delivery causing duplicate paid/provider side effects;
- prompt injection through campaign input or Tavily content;
- secret/private-data leakage into model prompts, logs, or analytics;
- OAuth callback/provisioning races.

### 18.4 Pending security decisions

- rate-limit thresholds and implementation location;
- CSRF pattern for the final session topology;
- content security policy;
- upload scanning and image moderation;
- data retention/deletion/export policy;
- formal secret store and rotation workflow;
- dependency/container vulnerability scanning choices;
- incident response and audit retention;
- privacy, terms, and media-rights review.

---

## 19. Reliability and consistency

### 19.1 Sources of truth

| State | Authority |
|---|---|
| Authentication session | Neon Auth, verified by application |
| Workspace/resource ownership | Application PostgreSQL |
| Campaign/post/revision/approval | Application PostgreSQL |
| Image-generation budget | Application PostgreSQL |
| Background job user-visible state | Application PostgreSQL |
| Celery transport/execution metadata | Redis/Celery, non-authoritative for product state |
| Media bytes | S3; ownership/provenance metadata in PostgreSQL |
| Scheduled execution after accepted handoff | Zernio |
| Application-visible publishing state | Reconciled PostgreSQL record informed by Zernio API/webhooks |

### 19.2 Failure handling

| Failure | Required behavior |
|---|---|
| FastAPI crashes after job commit before enqueue | Recover undispatched persistent job without creating a second logical job |
| Celery task redelivered | Resume/return existing result; do not duplicate side effects |
| AI/Tavily transient failure | Bounded retry; preserve partial durable progress where useful |
| Model produces invalid structure | Validate, bounded repair/retry, then visible failure/partial state |
| S3 upload fails | Do not mark asset usable; allow safe retry |
| Zernio create request times out | Reuse idempotency key/reconcile; do not create a blind duplicate |
| Webhook delivered twice | Unique event ID causes one applied transition |
| Webhook processing fails after receipt | Celery retry against persisted receipt without asking Zernio to republish |
| Social publication fails | Show failed/partial state; no automatic republish until policy is finalized |
| Provider outcome ambiguous | Show uncertain/reconciling state rather than published or failed without evidence |
| Redis is lost | Recover durable application jobs from PostgreSQL according to the finalized recovery design |

### 19.3 Time and timezone

Store canonical timestamps in UTC and preserve the timezone context the user saw when scheduling. The product must decide the source of workspace timezone, daylight-saving behavior, and rules for past/near-future schedules. Zernio schedule interpretation must be integration-tested.

### 19.4 Health checks

Recommended distinct checks:

- process liveness;
- application readiness;
- database connectivity;
- Redis/broker connectivity for worker readiness;
- worker heartbeat/last successful job as an operational signal;
- deployment smoke check of public frontend and protected API path.

External provider degradation should not necessarily mark the entire web service unready; surface dependency-specific operational state.

---

## 20. Scalability

### 20.1 V1 capacity model

The single EC2 deployment scales vertically. Concurrency is controlled through:

- FastAPI worker/process configuration;
- Celery worker concurrency and queue routing;
- Redis capacity;
- Neon connection pool capacity;
- provider rate limits;
- bounded research and model calls;
- upload and request-size limits.

No numerical capacity target is currently finalized. Load testing must determine safe settings for the selected instance and Neon/provider plans.

### 20.2 Scale-out path without premature commitment

The modular boundaries allow future separation of web/API and worker capacity. Potential future infrastructure is intentionally not selected. Before scaling out, measure:

- request latency and CPU/memory;
- queue depth and oldest-job age;
- job duration by type;
- database connections and query latency;
- Redis memory and delivery behavior;
- S3 throughput/errors;
- AI Credits and Tavily latency/rate limits;
- Zernio request and webhook volume.

The next architecture should be driven by an observed bottleneck, not by speculative enterprise scale.

---

## 21. Observability and operations

No monitoring vendor is finalized. At minimum, emit structured logs and application metrics sufficient to operate the system.

### 21.1 Correlation

Use non-secret identifiers to correlate:

- request/correlation ID;
- workspace ID;
- application job ID;
- campaign/post/revision ID;
- Celery task ID for diagnostics;
- AI workflow run ID;
- image-generation event ID;
- publishing-submission ID and safe Zernio post reference;
- webhook event ID.

Do not log raw access tokens, auth cookies, webhook secrets, AWS credentials, complete private prompts by default, or presigned URLs.

### 21.2 Minimum operational signals

- HTTP error and latency counts by safe route pattern;
- authentication and authorization failures without cross-tenant resource disclosure;
- job queue depth, oldest pending job, duration, retries, and failures;
- LangGraph node duration/failure and bounded model usage;
- Tavily calls, failures, and budget blocks;
- image-generation count and blocked third attempts;
- database pool pressure and slow queries;
- Redis availability and worker heartbeat;
- S3 upload/download errors;
- Zernio request outcomes, ambiguous submissions, webhook signature failures, duplicate events, processing lag, and terminal post outcomes;
- EC2 CPU, memory, disk, and service restarts.

Alert thresholds, retention, dashboards, on-call ownership, and incident procedures remain pending.

---

## 22. Testing strategy and architecture verification

### 22.1 Test layers

| Layer | Focus |
|---|---|
| Unit | Domain rules, state transitions, approval invalidation, budget logic, provider translation |
| Integration | PostgreSQL constraints/transactions, S3 authorization, Redis/Celery behavior, auth verification |
| Contract | AI Credits, Tavily, Zernio, and Neon Auth request/response assumptions |
| Security | Cross-tenant access, task substitution, object access, webhook forgery/replay, secret leakage |
| End to end | Browser signup through isolated workspace, campaign generation, approval, Zernio schedule/publish, webhook outcome |
| Failure/recovery | Worker crash, duplicate delivery, timeout after side effect, Redis restart, provider partial/ambiguous outcome |

### 22.2 Required critical scenarios

- two real users cannot read, mutate, enqueue, approve, schedule, publish, or access assets across workspaces;
- repeated signup/callback creates one workspace;
- concurrent image requests cannot consume a third campaign event;
- a material edit invalidates approval and blocks Zernio submission;
- a duplicated Celery task does not duplicate model/image/Zernio side effects;
- the same Zernio idempotency key returns/reconciles one logical provider post;
- invalid webhook signature has no effect;
- repeated stable webhook event ID applies one state transition;
- webhook delivery retry does not trigger publication retry;
- failed and partial platform outcomes remain truthful;
- private S3 media cannot be fetched or signed by another workspace;
- research prompt injection cannot change tools, tenant, approval, or publishing behavior.

### 22.3 Documentation-verified versus integration-verified

Zernio documentation verification is complete for the capabilities listed in Section 14.2. The application may label them integration-verified only after automated or recorded tests exercise the real configured account, credentials, endpoints, signatures, profile routing, idempotency, scheduling, and relevant initial platforms.

---

## 23. Architectural decisions and trade-offs

### ADR-01 — Modular monolith over microservices

**Decision:** One FastAPI backend and separate Celery worker using shared application modules.

**Why:** V1 needs coherent transactions, simple tenant enforcement, and low operational overhead. Microservices would add network contracts, distributed tracing, independent deployment, and eventual-consistency problems without demonstrated need.

**Trade-off:** Web and worker code remain coupled at release boundaries, and independent scaling is limited initially.

### ADR-02 — Celery + Redis for long-running work

**Decision:** HTTP requests initiate durable jobs; Celery executes background AI/media work via Redis.

**Why:** AI workflows and media processing exceed reliable HTTP lifetimes and require retries/progress.

**Trade-off:** At-least-once task behavior requires idempotent handlers, durable job records, and recovery design. Redis is another operational dependency on EC2.

### ADR-03 — PostgreSQL as durable workflow authority

**Decision:** Persistent job, approval, budget, webhook, and publishing state live in PostgreSQL.

**Why:** Redis task metadata is not sufficient for user-visible correctness or recovery.

**Trade-off:** More explicit state modeling and transaction design are required.

### ADR-04 — LangGraph explicit orchestration

**Decision:** Model the AI team as a controlled graph rather than unconstrained multi-agent conversation.

**Why:** Explicit steps, routing, state, budgets, and failure boundaries are easier to test and operate.

**Trade-off:** Workflow changes require deliberate graph/schema evolution.

### ADR-05 — AI Credits gateway

**Decision:** Access selected text and image models through AI Credits.

**Why:** Centralizes model access and permits role-appropriate model choices.

**Trade-off:** Gateway-specific capability, model availability, observability, and image support must be verified; the gateway is an external dependency.

### ADR-06 — Zernio-managed scheduling

**Decision:** Submit approved immutable post revisions to Zernio, which owns scheduled execution.

**Why:** Avoids implementing a separate social scheduling engine and leverages the selected unified provider.

**Trade-off:** The application depends on Zernio's platform support and state semantics. Changes after handoff need explicit cancel/replace behavior, and actual provider execution is outside our transaction boundary.

### ADR-07 — Private S3 media

**Decision:** Store binary media in private S3; store ownership and provenance in PostgreSQL.

**Why:** Object storage is appropriate for media and avoids EC2-local durability problems.

**Trade-off:** Presigned access, provider media retrieval, lifecycle, and rights eligibility require careful coordination.

### ADR-08 — Single EC2 V1

**Decision:** Run application containers and Redis on one EC2 instance initially.

**Why:** Matches V1 scope and minimizes infrastructure complexity.

**Trade-off:** No high availability and a shared failure/resource domain. This limitation must be communicated honestly.

---

## 24. External dependencies and technical risks

| Dependency/risk | Impact | Mitigation or required verification |
|---|---|---|
| Neon Auth/FastAPI session mismatch | Broken or insecure authentication | Verify official integration, expiry, revocation, OAuth, and protected routes end to end |
| Cross-tenant query/task/provider mapping error | Severe privacy and account-control breach | Server-derived workspace, scoped repositories, relationship constraints, negative tests |
| Neon capacity/connection exhaustion | API and worker failures | Pool/concurrency design and load tests |
| AI Credits model/gateway incompatibility | Generation or structured-output failure | Adapter layer and model contract tests |
| Tavily quality/limits | Missing or weak current-information support | Bounded usage, source validation, plan/limit verification |
| Prompt injection | Tool misuse or content corruption | Treat content as data, strict tools/schemas, deterministic permissions |
| Concurrent image requests | Budget bypass and cost | Atomic PostgreSQL budget record |
| Redis/worker interruption | Delayed or redelivered jobs | Persistent PostgreSQL job state and idempotent recovery |
| Zernio ambiguous create response | Duplicate public post | Persisted idempotency key and reconciliation |
| Webhook replay/duplication | Repeated state effects | HMAC verification and unique stable event ID |
| Confusing delivery retry with publish retry | Unintended republishing | Separate state/policy; repeated webhook never authorizes a new post |
| Zernio platform-specific limits | Rejected or altered posts | Validate initial platforms and content/media constraints |
| Private S3 media inaccessible to Zernio | Failed publication | Verify supported media handoff and URL lifetime |
| Web-image licensing | Legal/reputation risk | Block publishability without adequate rights evidence |
| Single EC2 outage | Full application/worker/broker downtime | Backups, restart/recovery plan, transparent V1 limitation |
| Uncontrolled logs | Secret or private-content exposure | Structured redaction and retention policy |

---

## 25. Pending decisions and verification register

These items do not reopen the finalized stack. They must be resolved during detailed design or integration work.

### 25.1 Application design

- exact API contracts, URL versioning, error envelope, pagination, and rate limits;
- database schema, indexes, deletion/retention strategy, and detailed state transitions;
- campaign input precedence and minimum required fields;
- material-change/approval invalidation matrix;
- schedule cancellation/replacement behavior after Zernio handoff;
- failed-post retry policy and required user action;
- timezone/DST behavior;
- progress delivery mechanism;
- exact web-image discovery and rights-verification workflow.

### 25.2 Provider integration

- Neon Auth server verification and complete browser/session behavior;
- AI Credits model IDs, structured output, tools, image endpoint, usage metadata, and limits;
- Tavily API behavior, limits, budgets, and source metadata;
- Zernio credentials, plan, initial platforms, connect flow, content/media constraints, callbacks, reconciliation, cancellations, and live verification of documented capabilities;
- S3-to-Zernio media transfer behavior.

### 25.3 Runtime and operations

- language/runtime and dependency versions;
- EC2 region, size, OS, volumes, and capacity;
- database/Redis/Celery connection, persistence, concurrency, timeout, and recovery settings;
- DNS, TLS certificate issuer/renewal, security groups, and secret delivery;
- CI tool details, artifact registry/transfer, migration and rollback mechanics;
- staging strategy, monitoring implementation, alerts, retention, backup, RTO, and RPO;
- accessibility/browser support and performance targets.

---

## 26. Implementation sequencing

This is an architecture-oriented dependency order, not a delivery estimate.

1. **Foundational contracts:** finalize identity mapping, workspace ownership, resource scoping, state terminology, and schema/migration conventions.
2. **Provider spikes:** prove Neon Auth to FastAPI, Zernio profile/account/schedule/webhook/idempotency, AI Credits structured output/image availability, Tavily sources, and S3 media handoff.
3. **Core application foundation:** create FastAPI modular boundaries, PostgreSQL persistence, workspace provisioning, authorization, persistent jobs, and private media metadata.
4. **Background foundation:** configure Redis/Celery and prove retry-safe job dispatch, execution, progress, and recovery.
5. **AI workflow:** implement typed LangGraph flow with LangChain adapters, conditional Tavily research, bounded model calls, and durable results.
6. **Human control:** implement versioned posts, deterministic material-change handling, approval records, and image-budget enforcement.
7. **Zernio publishing:** implement workspace/profile/account mapping, immutable approved submissions, idempotency, signed webhook receipt, deduplication, and reconciled states.
8. **Frontend completion:** connect onboarding, campaign creation/progress, post review, media, approval, calendar, and truthful errors/status.
9. **Deployment and hardening:** Docker Compose, Nginx/TLS, EC2, S3 controls, GitHub Actions, migrations, backups, logs, and security tests.
10. **Real-user verification:** execute the PRD's two-user isolated end-to-end acceptance flow with supported live accounts.

Do not build the broad UI on unverified identity, tenancy, and provider assumptions. Provider spikes must produce recorded contracts and update the pending-verification register.

---

## 27. Definition of architecture readiness

The technical design is ready for implementation planning when:

- finalized technologies and module boundaries are accepted;
- the application identity/workspace mapping is defined;
- tenant-scoped data access and task patterns are agreed;
- core schema/state designs cover revisions, approvals, image budget, jobs, Zernio submissions, and webhook receipts;
- Neon Auth, AI Credits, Tavily, Zernio, and S3 integration spikes resolve blocking unknowns;
- scheduling handoff and post-change behavior are explicit;
- failed-post retry and uncertain-outcome policies are explicit;
- runtime versions, EC2 sizing assumptions, and connection/concurrency budgets are recorded;
- security and failure-mode test plans cover the PRD's hard gates;
- no pending item is being represented as a confirmed capability in implementation prompts.

The system is not production-ready merely because containers start or mocked workflows pass. Production readiness requires deployed end-to-end verification of authentication, tenant isolation, AI workflows, media, approval enforcement, Zernio submission, signed webhook processing, failure visibility, duplicate prevention, recovery, and operational controls.

---

## 28. Final architecture summary

The V1 uses a Next.js/TypeScript interface styled with Tailwind CSS and shadcn/ui. It communicates through authenticated HTTP APIs with a FastAPI/Python modular monolith. Neon Managed Better Auth authenticates users; application-owned PostgreSQL records map the stable authenticated identity to one private workspace. Neon PostgreSQL, accessed through SQLAlchemy 2.x and migrated with Alembic, is the durable authority for domain and workflow state.

FastAPI executes deterministic authorization and business rules. It records long-running work before sending it through Celery using Redis as broker and result backend. Celery workers run explicit LangGraph workflows built with LangChain, call text/image models through AI Credits, and invoke Tavily only when research is needed. PostgreSQL—not Redis—stores user-visible job progress and final results. S3 privately stores uploaded and generated media while PostgreSQL stores ownership, provenance, rights, and publishability metadata.

After explicit approval of the current post revision, FastAPI validates the workspace, destination, media, schedule, and immutable content snapshot, then submits it to Zernio with a stable idempotency key. Zernio owns scheduled publishing. FastAPI receives HMAC-SHA256 signed, at-least-once webhooks, deduplicates them using the stable event ID, and uses Celery for non-trivial asynchronous handling. Webhook delivery retries do not authorize failed-post publishing retries.

Docker Compose runs Nginx, Next.js, FastAPI, the Celery worker, and private Redis on one AWS EC2 instance. Nginx provides HTTPS ingress; GitHub Actions provides controlled checks, container builds, migrations, deployment, and health verification. This topology deliberately accepts a single-server availability limitation in exchange for V1 simplicity while preserving clean boundaries for future scale based on measured need.


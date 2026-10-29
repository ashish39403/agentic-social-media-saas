# AI Social Media SaaS
## Technology Stack & System Architecture Report

**Version:** 1.0  
**Date:** October 29, 2026  
**Status:** Technology stack selected; detailed system design pending.

---

# 1. Project Overview

We are building a multi-tenant, AI-powered social media management SaaS.

The platform allows individual users to create private workspaces, configure brand profiles, connect social media accounts, and generate complete marketing campaigns using an autonomous AI agent team.

Our AI system will support:

- Campaign planning and content strategy
- Intelligent web research
- Platform-specific content generation
- AI image generation
- Web-discovered image suggestions
- Human-in-the-loop content editing
- Approval and scheduling
- Automated social media publishing

Every user will have an isolated workspace.

Our primary engineering goal is to build a secure, reliable, end-to-end SaaS application using modern backend, AI and cloud engineering practices.

---

# 2. Final Technology Stack

| Layer | Technology | Status |
|---|---|---|
| Frontend | Next.js + TypeScript | ✅ Final |
| UI Framework | Tailwind CSS + shadcn/ui | ✅ Final |
| Backend | FastAPI + Python | ✅ Final |
| Backend Architecture | Modular Monolith | ✅ Final |
| Database | Neon PostgreSQL | ✅ Final |
| Authentication | Neon Managed Better Auth | ✅ Final |
| ORM | SQLAlchemy 2.x | ✅ Final |
| Database Migrations | Alembic | ✅ Final |
| AI Framework | LangChain | ✅ Final |
| AI Orchestration | LangGraph | ✅ Final |
| LLM Gateway | AI Credits | ✅ Final |
| Web Research | Tavily | ✅ Selected, name to confirm |
| Image Generation | AI Credits-supported image model | ⏳ Exact model pending |
| Background Processing | Celery | ✅ Final |
| Message Broker | Redis | ✅ Final |
| Task Result Backend | Redis | ✅ Final |
| Persistent Job Records | PostgreSQL | ✅ Final |
| Social Media Integration | Zernio API | ✅ Final |
| Social Media Scheduling | Zernio | ✅ Final |
| Media Storage | AWS S3 | ✅ Final |
| Cloud Hosting | AWS EC2 | ✅ Final |
| Containerization | Docker + Docker Compose | ✅ Final |
| Reverse Proxy | Nginx | ✅ Final |
| HTTPS | TLS certificate | ✅ Final |
| CI/CD | GitHub Actions | ✅ Final |
| Version Control | Git + GitHub | ✅ Final |

---

# 3. High-Level System Architecture

```text
                   USER / BROWSER
                         |
                         v
                    AWS EC2
                         |
                    NGINX + HTTPS
                         |
             +-----------+-----------+
             |                       |
             v                       v
        NEXT.JS                 FASTAPI
        FRONTEND                 BACKEND
             |                       |
             |                 Business Logic
             |                       |
             |          +------------+------------+
             |          |            |            |
             |          v            v            v
             |       NEON DB      AWS S3       REDIS
             |                                    |
             |                                    v
             |                              CELERY WORKER
             |                                    |
             |                                    v
             |                              LANGGRAPH
             |                                    |
             |                    +---------------+--------------+
             |                    |               |              |
             |                    v               v              v
             |                AI CREDITS        TAVILY       IMAGE MODEL
             |                    |
             +--------------------+
                                  |
                            FASTAPI APIs
                                  |
                              ZERNIO API
                                  |
                         SOCIAL PLATFORMS
```

**Architecture principle:** One modular backend application with a separate background worker.

We will not introduce microservices unnecessarily.

---

# 4. Frontend Architecture

### Technologies
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui

### Responsibilities

The frontend will handle:

1. Landing page and authentication UI
2. User dashboard
3. Brand profile management
4. Social account connection interface
5. Campaign creation
6. AI generation progress
7. Post editing and approval
8. Content calendar
9. Publishing status monitoring
10. Workspace settings

The frontend communicates with FastAPI through authenticated HTTP APIs.

**Important:** Sensitive business logic, API keys, database authorization and AI execution must remain on the server.

---

# 5. Backend Architecture

### Technology: FastAPI

FastAPI will serve as the application's primary backend.

### Logical Modules

```text
Backend
│
├── Authentication Integration
├── Workspace Management
├── Brand Management
├── Campaign Management
├── AI Agent Orchestration
├── Content Management
├── Media Management
├── Social Account Integration
├── Publishing Management
└── Background Task Management
```

These are logical modules inside one backend application.

### Responsibilities

FastAPI will handle:

- API request validation
- Authentication verification
- Workspace-level authorization
- Business rules
- Database operations
- AI task initiation
- Image-generation limits
- Content approvals
- Zernio API requests
- Webhook processing

We will use Pydantic for request and response validation.

SQLAlchemy will manage application database access, while Alembic will handle schema migrations.

---

# 6. Authentication & Multi-Tenancy

### Provider: Neon Managed Better Auth

Authentication requirements:

- Email/password signup
- Google OAuth
- Email verification
- Password reset
- Secure sessions
- Logout

### Workspace Creation

```text
User Signs Up
      |
      v
Neon Authentication
      |
      v
User Identity Created
      |
      v
Provision Personal Workspace
      |
      v
Redirect to Dashboard
```

Workspace provisioning must be idempotent to prevent duplicate workspaces during repeated requests or OAuth callbacks.

### Multi-Tenant Security

Every workspace will own its associated:

- Campaigns
- Posts
- Media
- Brand settings
- Social accounts
- AI runs
- Publishing records

FastAPI will derive the authenticated user's workspace from trusted server-side identity information.

A user must never be allowed to supply another user's workspace identifier and access its resources.

Neon authentication credentials will be validated by FastAPI using a documented, secure verification mechanism. Session expiration and revocation behavior must be tested before implementation is considered complete.

**Security requirement:** Isolation applies to API requests, database access, Celery workers, agent tools and stored media.

---

# 7. AI Agent Architecture

### Technologies
- LangChain
- LangGraph
- AI Credits LLM Gateway

### Agent Responsibilities

| Component | Responsibility |
|---|---|
| Master Agent | Understand campaign goals and coordinate work |
| Research Agent | Collect fresh information when necessary |
| Content Agent | Generate platform-specific posts |
| Review Agent | Check content quality and consistency |
| Image Tool | Generate images when useful |

The image component can be a tool rather than another fully autonomous agent.

### Execution Flow

```text
User Creates Campaign
          |
          v
     Master Agent
          |
          v
   Research Required?
       /      \
      Yes      No
       |        |
       v        |
 Research Agent |
       |        |
       +----+---+
            |
            v
      Content Agent
            |
            v
       Review Agent
            |
            v
      Image Workflow
            |
            v
   Save Generated Drafts
            |
            v
       User Review
```

### Why LangGraph?

LangGraph will help coordinate execution steps, maintain workflow state, and route tasks based on decisions.

LangChain will provide model integrations, tools, structured outputs and agent functionality.

The workflow should use explicit state transitions rather than unnecessary agent-to-agent conversations.

### AI Model Integration

AI Credits provides our model gateway.

We can choose different models for:

- Campaign planning
- Content generation
- Content reviewing
- Image generation

Exact model IDs, structured-output behavior, tool-calling compatibility and image endpoints must be verified against the gateway.

---

# 8. Web Research

### Selected Provider: Tavily

The Research Agent will use Tavily for internet searches and relevant source extraction.

### Research Behavior

The system will invoke research only when required.

For example:

**Campaign:** Promote my personal SaaS product.

Research may be unnecessary because the saved brand profile already provides the required information.

**Campaign:** Explain the latest developments in AI agents.

Research is useful because current information is necessary.

### Research Rules

- Prefer credible sources.
- Retain source references.
- Avoid unsupported statistics.
- Limit unnecessary search calls.
- Treat retrieved web content as untrusted data, not instructions for the agent.

This helps control cost and reduce incorrect content generation.

---

# 9. Image Management

### Image Sources

1. AI-generated images
2. Web-discovered image suggestions
3. User-uploaded images

Text-only posts are also supported.

### AI Generation Limit

**Maximum: 2 AI-generated images per campaign.**

Image regeneration counts toward the same limit.

The backend must enforce this limit using persistent records and concurrency-safe checks.

### Image Generation Provider

We will select a compatible image model through AI Credits.

Potential examples include DALL·E or another image-capable model, depending on gateway availability.

We must verify actual image-generation API support rather than assuming an OpenAI-compatible text endpoint supports images.

### Web-Discovered Images

External images require source attribution and appropriate publishing rights.

Unverified web images can be displayed as suggestions but must not automatically become publishable media.

---

# 10. Background Processing — Celery + Redis

This is an important engineering component.

### Why Celery?

AI workflows can take considerable time.

Running them entirely inside an HTTP request can cause timeouts and negatively affect the user experience.

Celery allows these operations to execute independently.

### Responsibilities

**FastAPI:** Receives requests and creates tasks.

**Redis:** Acts as the message broker.

**Celery Worker:** Executes background tasks.

**PostgreSQL:** Stores persistent application state and job records.

### Workflow

```text
User Clicks Generate
         |
         v
       FastAPI
         |
         v
Create Persistent Job Record
         |
         v
     Redis Queue
         |
         v
    Celery Worker
         |
         v
     LangGraph
         |
         v
   Generate Campaign
         |
         v
Save Results in PostgreSQL
         |
         v
   Job = Completed
         |
         v
Dashboard Displays Results
```

### Background Tasks in V1

| Task | Celery |
|---|---|
| Generate campaigns | Yes |
| Run web research | Yes, as part of agent workflow |
| Generate AI images | Yes |
| Process uploaded media | When necessary |
| Process publishing webhooks | Yes, when processing requires additional work |
| Publish posts at scheduled times | No — Zernio handles this |

### Reliability Rules

- Task retries for transient failures
- Execution timeouts
- Failed-job recording
- Idempotent task processing
- Duplicate execution protection
- Persistent progress tracking

Redis will serve as the broker and task-result backend. PostgreSQL remains the source of truth for campaign and job status.

A Redis-backed task queue can redeliver work under certain failure conditions, so tasks must be safe to retry.

**Celery Beat is not initially required** because Zernio handles scheduled post publishing.

---

# 11. Social Media Integration

### Provider: Zernio

Zernio provides the unified API layer for supported social platforms.

### Responsibilities

- Connect social media accounts
- Manage provider-side account relationships
- Publish approved posts
- Schedule approved posts
- Report publishing outcomes

### Multi-Tenant Integration

Each workspace will map to its own Zernio customer profile.

Associated social accounts must remain scoped to that workspace.

### Publishing Workflow

```text
User Approves Post
          |
          v
Select Schedule
          |
          v
FastAPI Validates Post
          |
          v
Submit to Zernio
          |
          v
Zernio Schedules Post
          |
          v
Zernio Publishes
          |
          v
Webhook to FastAPI
          |
          v
Update PostgreSQL
          |
          v
Update User Dashboard
```

### Publishing Safety

- Unapproved posts cannot be published.
- Editing approved content invalidates approval when the publishable content changes.
- Duplicate submissions must be prevented.
- Failed publishing attempts must be visible.
- Webhooks must be authenticated and deduplicated.

Zernio supports event IDs, signed webhook deliveries and retry behavior, which our backend must handle correctly.

The exact initial social platforms and account limits still require confirmation against the selected Zernio plan.

---

# 12. Database & Media Storage

### Neon PostgreSQL

PostgreSQL will store:

- Users' application records and workspace mappings
- Brand profiles
- Campaigns
- Posts and revisions
- Approval states
- AI execution records
- Media metadata
- Social account mappings
- Publishing records
- Background job states

Authentication-managed tables are maintained through Neon Auth.

### AWS S3

S3 will store:

- Brand logos
- User-uploaded images
- Generated images
- Other approved media assets

### Security Requirements

- Private S3 bucket
- Workspace-scoped media authorization
- Presigned URLs for controlled access
- File size and content-type validation
- Secure credentials
- No unrestricted public object access

Assets submitted to Zernio must remain accessible for publishing through its supported media-upload workflow.

---

# 13. AWS Deployment Architecture

### Cloud Provider: AWS

### Infrastructure

```text
                 INTERNET
                     |
                     v
                 AWS EC2
                     |
                NGINX + HTTPS
                     |
       +-------------+-------------+
       |             |             |
       v             v             v
     Next.js       FastAPI        Redis
                     |
                     v
                Celery Queue
                     |
                     v
                Celery Worker
                     |
                     v
                AI Workflows

External Managed Services:
- Neon PostgreSQL
- AWS S3
- AI Credits
- Tavily
- Zernio
```

### Docker Compose Services

```text
docker-compose
│
├── nginx
├── frontend
├── backend
├── celery-worker
└── redis
```

This architecture allows us to deploy everything on one EC2 instance initially.

Redis will run on a private Docker network, without exposing its port publicly.

We will configure Redis persistence appropriate to the job queue and ensure application-level job recovery mechanisms exist.

### Deployment Limitations

This is a single-server deployment.

It is suitable for an initial working SaaS and internship demonstration, but it does not provide high availability.

We can consider ECS, managed Redis and additional infrastructure later if actual demand requires them.

---

# 14. CI/CD Pipeline

### Tool: GitHub Actions

Our delivery workflow:

```text
Developer Pushes Code
         |
         v
      GitHub
         |
         v
    GitHub Actions
         |
         v
    Lint + Type Check
         |
         v
     Automated Tests
         |
         v
     Build Containers
         |
         v
   Deploy to AWS EC2
         |
         v
   Application Health Check
```

### Requirements

- Automated backend tests
- Frontend build and type checks
- Container builds
- Controlled database migrations
- Secure deployment credentials
- Health checks
- Deployment failure reporting

Production credentials must never be committed to Git.

---

# 15. Essential Engineering Standards

The following requirements apply across the application.

### Security

- Authenticated API access
- Strict workspace isolation
- Secure handling of social account credentials
- Rate limiting
- Input validation
- Private object storage
- Verified webhooks
- Protected secrets

### Reliability

- Background job retries
- Task timeouts
- Duplicate prevention
- Publishing-state consistency
- Failure reporting
- Recovery from interrupted workflows

### AI Engineering

- Structured outputs
- Tool input validation
- Research source references
- Token and generation cost controls
- Image-generation limit enforcement
- Human approval before publication
- Agent execution logging

### Monitoring

At minimum, we need structured logs for:

- API requests and failures
- Background jobs
- Agent runs
- External API failures
- Publishing submissions
- Webhook processing

Sensitive tokens and private user information must not appear in logs.

---

# 16. End-to-End Application Workflow

This is how the complete product will operate.

### Phase 1 — User Onboarding

User visits the landing page, signs up through Neon Auth and receives a private workspace.

### Phase 2 — Brand Configuration

User saves brand information and connects supported social media accounts through Zernio.

### Phase 3 — Campaign Creation

User enters a campaign prompt and optional structured information.

FastAPI saves the campaign request and starts a Celery task.

### Phase 4 — AI Execution

Celery executes the LangGraph workflow.

The Master Agent coordinates research, content generation, review and image tools.

AI-generated content is saved in PostgreSQL.

Generated image assets are stored in S3.

### Phase 5 — Human Review

User reviews individual posts.

The user can edit, request AI revisions, approve or reject posts.

Every publishable version requires explicit approval.

### Phase 6 — Scheduling

User selects publishing dates and times.

FastAPI validates the approved content and sends scheduling instructions to Zernio.

### Phase 7 — Publishing

Zernio executes publishing at the scheduled time.

Its webhooks notify our backend about publishing outcomes.

### Phase 8 — Status Tracking

FastAPI updates publishing records.

Users can view scheduled, published and failed posts in their dashboard.

---

# 17. Remaining Technical Details

The major technologies are selected. The following details must still be verified or finalized during detailed architecture design:

1. Exact AI Credits model IDs, endpoint compatibility and image-generation support.
2. Exact initial social platforms and Zernio plan limitations.
3. Neon Auth verification, session expiration and revocation behavior with FastAPI.
4. Specific Tavily usage limits and research-call budgets.
5. Web image licensing and selection workflow.
6. Redis persistence, Celery concurrency and failed-job recovery.
7. AWS instance sizing, operational costs and deployment configuration.
8. API contracts, database schema and detailed agent state transitions.

These are implementation-level decisions, not reasons to reopen the entire technology stack.

---

# 18. Final Architecture Principles

Our engineering approach will follow these principles:

**1. Build a modular monolith first.**  
Avoid unnecessary microservices.

**2. Separate HTTP requests from long-running work.**  
Use Celery and Redis for background processing.

**3. Keep application data persistent.**  
Use PostgreSQL as the source of truth.

**4. Separate intelligent decisions from deterministic operations.**  
Use AI for planning, research and writing; use backend services for authorization, approvals and publishing.

**5. Maintain strict tenant isolation.**  
Every user must have an independent, secure workspace.

**6. Keep humans in control.**  
AI-generated content cannot be published without approval.

**7. Build for reliable operation, not artificial complexity.**  
Use established tools and introduce additional infrastructure only when justified.

---

## Final Summary

The AI Social Media SaaS will use **Next.js, TypeScript and shadcn/ui for the frontend; FastAPI and Neon PostgreSQL for the backend; LangChain and LangGraph for AI orchestration; AI Credits for model access; Tavily for web research; Celery and Redis for background processing; Zernio for publishing; and AWS EC2, S3, Docker, Nginx and GitHub Actions for infrastructure and deployment.**

This architecture is designed to support a secure, demonstrable, end-to-end multi-user SaaS without introducing unnecessary distributed-system complexity.
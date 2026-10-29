# AI Social Media SaaS — Product Overview

> **Document type:** Product definition and V1 scope baseline  
> **Status:** Working product specification — confirmed decisions consolidated  
> **Last updated:** 29 October 2026  
> **Purpose:** Explain what the product is, who it serves, how users interact with it, and what the first version must do. This is **not** the final technical architecture or implementation plan.

---

## 1. Product at a Glance

### What are we building?

We are building a **multi-user, AI-powered social media management SaaS** that helps individuals plan, create, review, schedule, and publish social media campaigns through an **autonomous AI agent team**.

A user signs up, receives a **private personal workspace**, saves their brand context, connects supported social media accounts, and asks the AI team to create a campaign. The AI team can research current information when necessary, prepare a short campaign strategy, draft platform-specific posts, recommend hashtags and posting times, and propose visual content. The user remains in control: **every post must receive explicit human approval before it can be scheduled or published**.

Approved posts are published through **Zernio**, our selected unified social media publishing integration.

### One-sentence positioning

> An AI-powered social media workspace that turns a campaign goal into researched, brand-aware, ready-to-review posts, with human-controlled publishing.

### What this product is *not*

It is **not** merely a caption generator, a generic chatbot, or an unreviewed auto-posting bot. Its value is the **end-to-end workflow**: campaign planning → agent-assisted content production → individual review → approval → scheduling → publishing → status tracking.

---

## 2. Problem and Value Proposition

### User problems

Individuals managing social media often need to:

- Decide what to post and build a coherent campaign rather than isolated captions.
- Research trends or current developments when a post depends on fresh information.
- Adapt wording, hashtags, and timing for different platforms.
- Find or create appropriate visuals without generating unnecessary AI-image costs.
- Review drafts, request revisions, and keep track of what has been approved.
- Schedule posts and manage publishing without switching between many tools.

### Product value

The SaaS combines **brand context, agentic content creation, human review, and cross-platform publishing** in one personal workspace. It aims to reduce repetitive work while keeping final decisions and account access under the user's control.

### Core product principles

1. **Human control:** AI prepares content; the user approves what goes public.
2. **Private by design:** One user's content, credentials, and AI context must never leak into another user's workspace.
3. **Useful autonomy:** Agents can plan and delegate tasks, but deterministic software handles operations such as authorization and reliable publishing.
4. **Cost awareness:** Use web research only when needed; strictly cap AI image generation.
5. **Practical V1:** Build a usable, secure end-to-end product before adding broad enterprise features.

---

## 3. Target Users

### Primary audience

**Individual creators, startup founders, solo marketers, and small-business owners** who manage their own brand or product's social media presence and want assistance with regular campaign creation and publishing.

### Example personas

| User | Need | Value from the product |
|---|---|---|
| Solo startup founder | Promote a product without a dedicated marketing team | Turn product context and goals into a campaign with reviewable posts |
| Individual creator | Publish consistently across supported platforms | Create platform-specific drafts and schedule approved content |
| Freelance/solo marketer | Draft and revise content efficiently for a brand they manage | Reuse a saved brand profile and edit individual campaign posts |
| Small-business owner | Save time on content ideas and scheduling | Get a simple guided flow from campaign idea to publication |

**V1 boundary:** Each user operates **one personal workspace with one saved brand profile**. A person managing multiple clients through separate shared teams is **not** the primary V1 scenario.

### The user model

- **Visitor:** Can view the public landing page and start signup/login.
- **Authenticated user:** Owns and manages one private workspace and its campaigns, assets, social connections, and posts.
- **No collaborative roles in V1:** No invitations, shared workspaces, owners/admins/members hierarchy, or workspace switching.

---

## 4. Workspace and Multi-Tenant SaaS Model

### Signup and onboarding

1. A visitor opens the landing page.
2. The visitor signs up or signs in.
3. On first signup, the system **automatically creates a personal workspace** associated with that user.
4. The user is taken to their dashboard; they do not need to manually create or choose a workspace.
5. The user may configure their brand profile and connect social accounts before starting a campaign.

### Isolation requirements

All workspace-owned information must be securely isolated, including:

- Brand profile and branding assets.
- Campaign inputs, generated strategies, and posts.
- Drafts, revisions, approvals, and schedules.
- Uploaded, AI-generated, and selected visual assets.
- Connected social accounts, tokens/credentials, and publishing results.
- Agent runs, research context, tool results, and job execution context.

A logged-in user must not be able to view, guess an identifier to access, edit, delete, publish, or use another user's resources. **Enforcement belongs on the server/data-access boundary**, not merely in frontend filtering. Agent tools and background jobs must follow the same isolation rules.

**Important distinction:** A personal workspace does **not** require a separate physical database or separate API keyspace for every user. The final storage/isolation implementation will be decided during architecture design.

---

## 5. End-to-End User Journey

```text
Landing page
    |
Signup / Login
    |
Private workspace auto-created (on first signup)
    |
Dashboard
    |-- Save / update brand profile
    |-- Connect supported social accounts
    |
Create campaign (natural-language prompt + optional structured fields)
    |
Master Agent plans campaign
    |-- Research Agent searches the web only if needed
    |-- Content Agent writes platform-specific drafts
    |-- Image workflow adds visuals only where useful
    |-- Review Agent checks/refines proposed content
    |
Campaign strategy + individual draft posts
    |
User reviews / edits / asks AI for targeted revisions
    |
User approves posts individually
    |
User selects/confirms schedule
    |
Approved posts are published via Zernio
    |
Dashboard shows publishing outcomes / errors
```

**Example:** A founder asks, “Create a five-day campaign to introduce my AI note-taking app to startup founders.” The AI can reuse the saved brand profile, propose five tailored posts, suggest hashtags and dates, and add images only where valuable. At most **two AI-image generations** are allowed for that campaign; remaining posts can be text-only or use other permitted image sources. The founder revises and approves each post separately before scheduling.

---

## 6. V1 Product Capabilities

### 6.1 Landing page and user accounts

- Public landing page introducing the product and its capabilities.
- User signup, login, and access to a personal dashboard.
- Automatic personal-workspace creation on first signup.
- Authenticated, workspace-scoped access to private features.

**Not yet chosen:** Specific identity/authentication provider and exact login methods beyond the baseline signup/login experience.

### 6.2 Saved brand profile

Each workspace supports **one reusable brand profile** in V1. The user can save:

- Brand/product name.
- Brand/product description.
- Website URL.
- Target audience.
- Brand voice and tone.
- Optional brand logo.

The AI team uses this context when creating campaigns. A campaign can **override relevant brand details** without necessarily changing the saved profile. Brand information must never be drawn from another workspace.

### 6.3 Hybrid campaign creation

The user can create a campaign by:

1. Writing a natural-language request; and/or
2. Providing structured details in a campaign form.

The structured details can include brand/product context, target audience, tone, selected platform(s), campaign goal, number of posts, and date range. Both inputs should inform the same campaign rather than behave like unrelated features.

**Example request:** “Create seven LinkedIn posts explaining how our AI tool helps developers organize research.”

### 6.4 Autonomous AI agent team

The product presents an **agentic, task-coordinated content workflow** rather than one unstructured generation prompt. The following are **logical responsibilities**, not a final commitment to any particular agent framework or number of LLM processes.

| Logical role | Responsibility |
|---|---|
| **Master/Orchestrator Agent** | Understand the goal, use brand context, plan the work, decide when research is needed, and coordinate content preparation. |
| **Research Agent** | When necessary, search/read relevant web sources, extract useful current facts, and preserve references. |
| **Content Writer Agent** | Prepare platform-appropriate captions/posts, suitable hashtags, and suggested posting times. |
| **Visual Content Capability** | Determine where an image adds value; generate within budget or suggest an allowable alternative. |
| **Content Review Agent** | Check drafts for relevance, coherence, brand voice, and unsupported claims before showing them to the user. |

**Agent boundary:** LLMs should not be used for tasks that deterministic backend services can do more safely, such as enforcing permissions or executing scheduled API calls.

### 6.5 Intelligent web research

Web research is **available but conditional**:

- Use it for recent news, changing trends, external facts, or claims that require verification.
- Skip it when the user's saved brand context or established knowledge is enough.
- Favor credible/relevant sources and keep references associated with research findings.
- Avoid invented statistics, fabricated citations, and unsupported factual claims.
- Apply search/request limits to avoid unnecessary cost and latency.

The web research capability for **facts and trends** is separate from the web-image discovery option described below.

### 6.6 Generated campaign deliverables

A generated campaign should provide:

1. **Short campaign strategy summary** — intended message, audience, and content direction.
2. **Platform-specific draft posts** — adapted to selected social channels.
3. **Relevant hashtags** — tailored per post where appropriate.
4. **Suggested posting dates/times** — recommendations the user can confirm or change.
5. **Images where useful** — no requirement to attach an image to every post.

Timing suggestions are recommendations, **not guarantees** of higher engagement.

### 6.7 Image sourcing and generation

Supported image options for V1:

- **AI-generated images** when they improve the post.
- **Web-discovered images** suggested by the system, subject to source/rights checks.
- **User-uploaded images** provided directly by the user.
- **Text-only posts** with no image.

#### Strict AI-generation budget

- **Maximum: 2 AI image-generation events per campaign.**
- **Regeneration counts** toward the same limit; it does not provide an extra free allowance.
- The limit applies to the **whole campaign**, not individually to each agent or post.
- No mandatory image for each post; the agent should choose deliberately where visuals add value.
- The budget must be enforced by backend/business logic, not merely by prompting the model.

#### Rules for web-discovered images

- Discovery does **not** automatically grant the right to republish an image.
- Keep the source and available license/usage information.
- Do not automatically publish a random image found online or assume every online image is royalty-free.
- Only use an externally sourced image for publishing when applicable usage rights/conditions are satisfied, and the user has approved the post.
- If rights are unclear, treat it as a reference/suggestion rather than a publishable asset.

The exact image search provider and asset licensing/verification UX are **not yet selected**.

### 6.8 Post-level review, editing, and approval

Every generated post is reviewable **independently**. The user can:

- Inspect its text, hashtags, selected image, and suggested schedule.
- Manually edit the caption or other editable content.
- Ask AI for a targeted revision, e.g. “Make post 3 shorter and more professional.”
- Regenerate a specific post's text or request an image change (within the image-generation budget).
- Approve the individual post once satisfied.
- Leave other posts in draft/review while approving selected posts.

**Non-negotiable approval rule:** A post cannot be published without explicit user approval of its **current** content. If approved content is materially modified afterward, it must be reviewed and approved again.

### 6.9 Scheduling and publishing

- Users can schedule approved posts for a chosen date/time, using the AI's suggestions or their own selections.
- The product uses **Zernio** as its selected unified social-media publishing API provider.
- Connected accounts must be associated with the correct workspace.
- Only approved content may be sent for publication.
- The application must track whether a post is awaiting review, approved, scheduled, published, or failed; the exact internal state-machine design will be settled later.
- Failures must be visible and must not silently present failed posts as published.
- Retry behavior must avoid unintended duplicate posts.

**Architecture still open:** Which scheduling responsibilities live in our application versus Zernio, what channels are supported in the chosen plan, and exact API behavior require verification before implementation.

### 6.10 Dashboard and basic management experience

The product should give an authenticated user access to their own:

- Overview/dashboard.
- Brand profile.
- Campaign list and campaign details.
- Drafts and post-level review/editing.
- Calendar or scheduled-post view.
- Connected social accounts.
- Publishing states, failures, and relevant settings.

These are **functional areas**, not a finalized page/navigation design. Detailed engagement analytics are not yet defined as a V1 requirement.

---

## 7. Product Rules and Safety Boundaries

| Area | V1 rule |
|---|---|
| Workspace ownership | One user → one automatically created personal workspace. |
| Collaboration | No team invitations, shared roles, or multiple workspaces in V1. |
| Brand profile | One saved profile per workspace; campaign-level overrides allowed. |
| Campaign input | Hybrid: prompt and/or structured form. |
| Web research | Conditional, with references and controlled usage. |
| Campaign output | Strategy, posts, hashtags, suggested timing, and images where useful. |
| AI image budget | Max **2 generation events per campaign**, including regenerations. |
| Other media | Web-discovered images (rights permitting), user uploads, or no image. |
| Review | Per-post manual edits and AI-assisted revisions supported. |
| Approval | Explicit human approval required before scheduling/publishing each post. |
| Post-change behavior | Material changes after approval require reapproval. |
| Publishing | Zernio integration; ensure correct workspace/account and track outcomes. |
| Tenant security | No cross-workspace reads, modifications, tokens, AI context, or job execution. |
| AI execution | No uncontrolled publishing or unnecessary image/research requests. |

---

## 8. Illustrative User Stories

### Account and privacy

- **As a new user**, I want signup to provision my workspace automatically so I can start without manual setup.
- **As an authenticated user**, I want all content and connected accounts to remain private to me.

### Brand and campaign creation

- **As a founder**, I want to save my brand voice once so I do not repeat it for every campaign.
- **As a creator**, I want to describe a goal in plain language and optionally add form details.
- **As a marketer**, I want a brief strategy and channel-specific posts rather than generic captions.

### AI assistance

- **As a user posting about current events**, I want the AI to research recent facts and retain source references.
- **As a user posting about my own product**, I do not want unnecessary web research to slow down creation.
- **As a budget-conscious user**, I want image generation limited and images added only when appropriate.

### Control and publishing

- **As a user**, I want to rewrite only post 3 without regenerating the entire campaign.
- **As a user**, I want to approve posts individually and prevent unapproved drafts from being published.
- **As a user**, I want to schedule approved posts and see when publishing fails.

---

## 9. Example Acceptance Scenarios for V1

These scenarios describe **observable product behavior**, not a finalized test implementation.

1. **Automatic onboarding:** When a new user signs up successfully, they enter a private workspace with no manual workspace-creation step.
2. **Cross-user isolation:** User A cannot retrieve, edit, or publish User B's campaign/post even by requesting a known resource identifier.
3. **Brand reuse:** A newly created campaign can draw on the user's saved brand details and honor valid campaign-specific overrides.
4. **Hybrid input:** Campaign creation works using a short prompt, and optional structured fields refine the generated output.
5. **Conditional research:** A request about recent events can trigger sourced web research; an ordinary brand-awareness campaign need not.
6. **Meaningful output:** A generated campaign contains strategy, individual draft posts, relevant hashtags, and suggested dates/times.
7. **Image budget:** Once two AI image-generation events have been used for a campaign, additional AI image generations/regenerations are blocked by application logic.
8. **Optional images:** A campaign can contain text-only posts even when image functionality is available.
9. **Safe external media:** A web-discovered image with unclear publishing rights cannot flow straight into automated publication.
10. **Targeted editing:** Revising one post does not automatically overwrite unrelated posts.
11. **Approval gate:** A draft/unapproved post cannot be scheduled or published. A materially edited approved post requires new approval.
12. **Publishing result:** A scheduled post has a visible status; a failed API call is surfaced instead of being treated as successful publication.
13. **Publishing isolation:** A background publishing operation cannot substitute another user's connected social account or credentials.

---

## 10. Scope Boundaries: V1 vs. Future Enhancements

### In scope for the agreed V1 product

- Public landing page and user authentication.
- Auto-created, isolated personal workspace for each user.
- One reusable brand profile per workspace.
- Social account connectivity through the Zernio integration.
- Hybrid campaign creation.
- Coordinated AI agent responsibilities with conditional web research.
- Campaign strategy, platform-specific posts, hashtags, and time suggestions.
- Optional images: at most two AI generations per campaign, plus suitable web suggestions and user uploads.
- Individual post editing, AI-assisted targeted revisions, and mandatory human approval.
- Scheduling/publishing of approved posts and basic outcome/error visibility.

### Explicitly outside the selected V1 scope

- Team workspaces, team invitations, role hierarchies, and collaboration.
- Multi-workspace switching or multiple saved brand profiles per user.
- AI-generated video content.
- Unlimited AI image generation.
- Fully autonomous publishing that bypasses human approval.
- Enterprise-scale workflow features not necessary for a working personal-workspace SaaS.

### Not yet decided; do **not** assume these are included

- Paid subscriptions, billing, pricing tiers, or usage-based billing.
- Advanced social analytics, engagement reporting, or competitor monitoring.
- A fixed list of social media channels; availability depends on Zernio capabilities and plan.
- A specific UI design system, implementation framework, database, job queue, cloud host, or agent framework.

---

## 11. External Dependencies, Costs, and Risks

### Zernio

Zernio is the **chosen publishing provider**, not a guarantee of unlimited free usage or support for every platform. Before implementation, validate:

- Supported channel connections and publishing operations.
- Free-tier/paid-tier account, profile, and request limits.
- Whether the intended multi-user SaaS connection model is supported.
- Authentication and token lifecycle requirements.
- Scheduling, media, error, webhook, and retry capabilities.

### AI and research providers

LLM, web-search, and image-generation providers are **not chosen yet**. API usage, latency, quality, terms, and pricing must be evaluated. Enforce the agreed image cap independently of any provider's prompt instructions.

### Media rights

Web images introduce licensing/copyright risk. Search results are not evidence of reuse permission. Keep sources visible and require authorization/appropriate rights before published use.

### Reliability and security

Publishing jobs must handle time zones, provider errors, delays, retries, and duplicate prevention; credentials and workspace boundaries require careful handling. These are engineering requirements, **not** permission to introduce complex infrastructure prematurely.

---

## 12. Open Questions for the Next Phase

These choices were **not finalized** during product discovery and should be resolved during scope/architecture planning, not silently assumed here:

1. Which exact social platforms will be supported initially through Zernio?
2. Which authentication provider and supported login methods will be used?
3. Which LLM, image model/provider, and web-search/image-discovery provider(s) will be used?
4. Which technology stack, storage system, deployment platform, and background-job mechanism will be used?
5. Will our system or Zernio own the actual scheduled execution, and what happens when publishing fails?
6. How will we implement media storage, source attribution, and rights checks in the user experience?
7. How many posts/campaigns/agent runs should be allowed per workspace or over time? (**The only finalized numeric generation limit is 2 AI images per campaign.**)
8. What authentication, rate-limiting, observability, and operational controls are needed for a secure public deployment?
9. Will billing, usage quotas, or advanced analytics be included in a later release?

---

## 13. Definition of a Successful V1

V1 is successful when **two separate real users** can independently sign up, have isolated private workspaces, configure their brands, create AI-assisted campaigns, review/edit individual posts, approve selected content, and publish/schedule it through supported connected accounts **without data leakage, unapproved publishing, silent failures, or image-cap bypasses**.

The end-to-end flow should be demonstrable in a deployed application with enough testing and operational visibility to explain key backend, AI, SaaS security, and integration decisions in an internship interview.

---

## 14. Summary of Confirmed Decisions

| # | Decision | Selected approach |
|---:|---|---|
| 1 | Product category | Multi-user **AI Social Media SaaS** |
| 2 | Tenant model | Private **individual workspace** created automatically per user |
| 3 | AI interaction | **Autonomous agent team**, with mandatory human approval |
| 4 | Publishing integration | **Zernio** unified social media API |
| 5 | Content modalities | **Text + images**, no AI video in V1 |
| 6 | Campaign input | **Hybrid** prompt + optional structured form |
| 7 | Content review | **Individual post review + AI-assisted editing** |
| 8 | Image strategy | AI generation (**max 2 per campaign**, regenerations included), web discovery, user uploads, and text-only |
| 9 | Campaign deliverables | Strategy summary, posts, hashtags, posting-time suggestions, images where valuable |
| 10 | Brand context | **Saved brand profile** with campaign-level overrides |
| 11 | Research capability | **Web Research Agent** with source references |
| 12 | Research invocation | **Intelligent/conditional**, only when helpful |

**Next step:** Review this product definition as the agreed baseline, then separately design the V1 architecture and implementation plan. This document intentionally avoids prematurely deciding frameworks, providers beyond Zernio, database layout, and infrastructure.

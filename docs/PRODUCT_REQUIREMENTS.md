# AI Social Media SaaS — V1 Product Requirements Document

| Field | Value |
|---|---|
| Document status | Draft for product, design, and engineering review |
| Product phase | V1 definition; pre-architecture and pre-implementation |
| Product baseline | `PRODUCT_OVERVIEW.md`, last updated 29 October 2026 |
| PRD version | 0.1 |
| Prepared | 29 October 2026 |
| Decision authority | Product owner; named owner not yet recorded |

> This PRD translates the confirmed product overview into testable product requirements. It does not select a technology stack or silently settle open product questions. Labels are used deliberately: **Confirmed** comes directly from the overview; **Derived requirement** is necessary to make a confirmed behavior safe or observable; **Open** requires a product, design, integration, or architecture decision.

---

## 1. Executive summary

The product is a multi-user SaaS for individuals who manage their own social presence. Each authenticated user receives one private personal workspace, saves one reusable brand profile, connects supported social accounts, and asks a coordinated AI system to develop a social campaign. The system can conditionally research current information, create a short strategy, produce platform-specific posts, recommend hashtags and timing, and propose visuals. The user reviews each post independently and must explicitly approve its current content before it becomes eligible for scheduling or publishing through Zernio.

The product's differentiator is not raw text generation. It is a controlled workflow from campaign intent to publishable output: brand context → campaign planning → conditional research → content and visual preparation → automated review → human revision and approval → scheduling → publishing outcome. Deterministic software, not an LLM, enforces workspace isolation, resource ownership, usage limits, approval validity, scheduling eligibility, and safe publishing.

V1 is successful only when two separate real users can complete this flow in independently isolated workspaces without cross-user leakage, unapproved publishing, silent publishing failures, duplicate publication caused by unsafe retry behavior, or bypass of the two-image-generation campaign cap.

---

## 2. Problem definition

### 2.1 Core user problem

Individuals responsible for social media without a dedicated marketing team must coordinate campaign thinking, current-information research, channel-specific writing, visual selection, review, scheduling, and publishing across disconnected tools. This creates repeated work, inconsistent output, extra context switching, and a risk that low-confidence or unreviewed content reaches the public.

This is a workflow problem rather than a caption-generation problem. A useful solution must help the user move coherently from a campaign goal to controlled publication while preserving brand context and human judgment.

### 2.2 Problem evidence available today

The product overview identifies recurring user tasks and pain points, but it does not include customer-interview evidence, behavioral data, willingness-to-pay evidence, or a quantified baseline. Those evidence gaps do not invalidate the proposed V1, but they limit claims about market demand and measurable time savings.

Before external launch positioning is finalized, product discovery should validate:

- whether the primary users experience the full workflow problem frequently enough to adopt a dedicated product;
- which part of the workflow is most painful today;
- which initial social channels are essential;
- what level of campaign quality users consider publishable after review;
- whether users trust sourced research and human-gated publishing;
- whether users can correctly evaluate web-image usage rights in the proposed experience.

### 2.3 Business problem

The business needs a credible V1 that demonstrates differentiated end-to-end value rather than an interchangeable AI writing interface. It also needs enough safety, reliability, and isolation to support real users and provide defensible evidence of product and engineering quality.

Revenue, pricing, subscription conversion, and paid acquisition are not defined V1 outcomes because billing and commercial packaging have not been selected.

### 2.4 Problems V1 intentionally does not solve

- Collaborative agency or marketing-team workflows.
- Managing multiple client workspaces or multiple reusable brands per user.
- Full social listening, competitor intelligence, or advanced performance analytics.
- AI video creation.
- Fully autonomous public posting without human approval.
- A guarantee that suggested posting times improve engagement.
- Automatic clearance of arbitrary online images for commercial reuse.

---

## 3. Product vision, positioning, and principles

### 3.1 Vision

Give an individual the leverage of a small social-content team while keeping public communication, account access, and final decisions under that individual's control.

### 3.2 Positioning

> An AI-powered social media workspace that turns a campaign goal into researched, brand-aware, ready-to-review posts, with human-controlled publishing.

### 3.3 Product principles

| Principle | Product implication |
|---|---|
| Human control | AI-produced content remains a proposal until the user approves each post's current revision. |
| Private by design | Workspace ownership is enforced at every server, data-access, agent-tool, job, media, credential, and callback boundary. |
| Useful autonomy | AI coordinates judgment-heavy content work; deterministic services perform permissions, counters, state transitions, and external side effects. |
| Cost awareness | Research runs only when useful; AI image generation is optional and capped at two events per campaign. |
| Practical V1 | The first release proves a secure end-to-end personal workflow before collaboration or enterprise breadth. |
| Truthful output | Current or external claims are sourced when needed; invented facts, fabricated citations, and misleading publishing status are unacceptable. |
| Recoverable failure | Errors remain visible and actionable; retries must not create unintended duplicate public posts. |

---

## 4. Goals, non-goals, and success definition

### 4.1 V1 goals

1. Let a new user move from signup to an automatically created private workspace without a workspace-selection step.
2. Let the user save reusable brand context and create a campaign using a prompt, structured inputs, or both.
3. Generate a coherent campaign strategy and independently reviewable, platform-adapted draft posts.
4. Use current-information research selectively and retain source references when research informs content.
5. Support text-only, user-uploaded, rights-eligible web-discovered, and budgeted AI-generated visual paths.
6. Give the user targeted post-level editing and revision controls without overwriting unrelated posts.
7. Ensure only explicitly approved current revisions can be scheduled or published.
8. Publish through the correct user's supported connected account via Zernio and show truthful outcomes.
9. Demonstrate isolation, budget enforcement, approval integrity, and reliable failure handling with two real users.

### 4.2 V1 non-goals

- Teams, invitations, roles, approvals by multiple people, or shared workspaces.
- Multiple personal workspaces or multiple saved brand profiles.
- AI-generated video.
- Unlimited AI-generated images.
- Autonomous approval or approval-free publishing.
- Billing, subscriptions, pricing tiers, or usage-based charging unless separately approved.
- Advanced analytics, engagement reporting, social listening, or competitor monitoring unless separately approved.
- Support for every social network.
- Final technical architecture or detailed visual design in this document.

### 4.3 Hard success gates

The following are confirmed release-level outcomes rather than aspirational metrics:

| Gate | Pass condition |
|---|---|
| End-to-end usability | Two separate real users can each sign up, configure a brand, create a campaign, review and edit posts, approve selected posts, and schedule or publish through a supported connected account. |
| Tenant isolation | Neither user can access, alter, publish, or cause jobs to operate on the other user's workspace-owned resources or credentials. |
| Approval integrity | No unapproved or approval-invalidated post can be scheduled or published. |
| Image-budget integrity | A third AI image-generation attempt for the same campaign is rejected by deterministic application logic, including concurrent attempts. |
| Publishing truthfulness | Failed or uncertain provider outcomes are never displayed as successfully published. |
| Duplicate prevention | A retry or repeated callback does not unintentionally create a duplicate social post. |
| Operational explainability | The deployed flow exposes enough logs/status information to explain important AI, security, publishing, and failure decisions. |

### 4.4 Measurement plan requiring targets

The overview does not provide baselines or numerical product targets beyond two users and two AI image generations per campaign. The team must not invent targets to make the PRD appear complete. Before a broader launch, owners should define baselines, time windows, exclusions, and targets for:

- signup-to-workspace provisioning success rate;
- onboarding completion rate;
- campaign-generation completion and failure rates;
- time from campaign submission to reviewable output;
- percentage of generated posts approved, edited, regenerated, or abandoned;
- scheduling and publishing success rates by channel;
- median time to surface provider failure;
- rate of research use and source-reference availability;
- AI image-generation utilization and blocked over-budget attempts;
- tenant-isolation, approval-bypass, and duplicate-publication incidents (target must be zero);
- user-reported usefulness and trust after the first completed campaign.

---

## 5. Users, jobs, and access model

### 5.1 Primary users

| Segment | Situation | Primary job |
|---|---|---|
| Solo startup founder | Promotes a product without a marketing team | Turn product context and a launch goal into a credible multi-post campaign. |
| Individual creator | Needs a consistent cross-channel presence | Produce and schedule platform-appropriate posts without repeating context. |
| Freelance or solo marketer | Manages a brand independently | Create, revise, and approve content efficiently using saved brand context. |
| Small-business owner | Has limited time for content operations | Move through a guided idea-to-publication workflow with clear control. |

### 5.2 Jobs to be done

- When I have a campaign goal, help me turn it into a coherent set of channel-appropriate posts so I do not plan each post from scratch.
- When a post depends on current facts, help me use credible, traceable information so I can review claims before publication.
- When visual content would help, give me cost-aware and rights-aware options so I am not forced into unnecessary image generation or unsafe reuse.
- When a draft is imperfect, let me change that post without losing good work elsewhere in the campaign.
- When content is ready, let me approve and schedule it with confidence that nothing else will be posted.
- When publishing fails, tell me what happened and what I can safely do next.

### 5.3 Actors

| Actor | Allowed V1 capabilities |
|---|---|
| Visitor | View public product information; start signup or login. |
| Authenticated user | Access the single workspace they own; manage its brand, campaigns, posts, assets, connections, schedules, and settings. |
| AI workflow | Operate only within an explicitly scoped workspace and campaign using permitted tools; propose content and recommendations. |
| Background publisher | Execute an authorized scheduled operation for one eligible post and one workspace-owned connection. |
| External provider | Return connection, scheduling, publishing, media, error, or callback information subject to verified integration behavior. |

There is no V1 invitation, collaborator, admin/member, approver, or workspace-switching role.

---

## 6. Scope and release boundary

### 6.1 Included capabilities

- Public landing page, signup, login, logout, and authenticated access.
- Automatic creation of one private personal workspace on first signup.
- One editable reusable brand profile and optional logo per workspace.
- Workspace-owned social account connections through Zernio.
- Campaign creation from natural language, structured inputs, or both.
- Coordinated AI planning, conditional research, writing, visual selection, and review responsibilities.
- Strategy summary; platform-specific drafts; relevant hashtags; suggested dates and times; optional images.
- Per-post manual editing, targeted AI revision, regeneration, and individual approval.
- Scheduling and publishing of eligible approved posts.
- Campaign, post, schedule, connection, publishing-status, and failure visibility.
- Minimum operational and security controls required by the hard launch gates.

### 6.2 Excluded capabilities

- Collaborative and enterprise workflows.
- Multi-brand or multi-workspace account management.
- AI-generated video.
- Unlimited AI image generation.
- Approval-free publishing.
- Features listed as undecided in Section 16 unless explicitly resolved and added to scope.

### 6.3 Scope interpretation rule

If a feature is not included above, is not required by a numbered requirement, and is not needed to satisfy an acceptance criterion or safety gate, it is not part of V1 without a documented scope decision.

---

## 7. End-to-end experience

### 7.1 Happy path

1. A visitor understands the product's value and starts authentication.
2. On first successful signup, the application provisions exactly one personal workspace and routes the user to the authenticated experience.
3. The user completes or updates the brand profile and connects at least one supported social account.
4. The user starts a campaign with a prompt, optional structured details, or both.
5. The system validates the request and resolves saved brand context plus campaign-specific overrides.
6. The orchestrated AI flow creates a plan, decides whether current-information research is needed, prepares content, chooses appropriate visual paths, and reviews its own proposed deliverables.
7. The campaign becomes reviewable with a short strategy and independent draft posts. Research-derived claims retain references; image provenance and rights state remain visible where relevant.
8. The user edits or requests targeted revisions for individual posts. Unrelated posts remain unchanged.
9. The user explicitly approves each acceptable post revision.
10. The user selects or confirms a schedule for approved posts against the intended connected account and its timezone context.
11. The system revalidates ownership, connection, approval revision, schedule, and publishing eligibility before creating the external side effect.
12. The product shows a truthful scheduled, publishing, published, failed, or uncertain outcome and gives safe recovery guidance when needed.

### 7.2 Required alternate paths

- The user creates a campaign before completing the optional brand fields; the product identifies which minimum inputs are missing rather than borrowing context from elsewhere.
- The system determines research is unnecessary and proceeds without a web-search call.
- Research is required but fails or yields insufficient evidence; the product avoids unsupported factual claims and communicates the limitation.
- The campaign contains no images because visuals do not add enough value.
- The user uploads an image instead of generating one.
- A discovered image has unclear rights; it remains a reference and cannot silently enter the publishable path.
- One post is regenerated while all other posts preserve their current revisions.
- An approved post is materially changed and returns to a review-required state.
- The user tries to schedule an unapproved post and is blocked with corrective guidance.
- A social connection is expired or revoked before execution; publication is blocked or fails visibly without using a different connection.
- The provider times out or returns an ambiguous result; the product shows an uncertain/pending-reconciliation state rather than assuming success or immediately duplicating the request.

---

## 8. Functional requirements

All requirements in this section are V1 requirements unless explicitly labeled Open. “System” includes the product's deterministic application services, not only its user interface.

### 8.1 Public experience and authentication

| ID | Requirement | Source |
|---|---|---|
| AUTH-01 | The product shall provide a public landing page that accurately explains the core workflow and human-approval boundary. | Confirmed |
| AUTH-02 | A visitor shall be able to begin signup and login from the public experience. | Confirmed |
| AUTH-03 | After a first successful signup, the system shall create one personal workspace associated with that authenticated identity without requiring manual workspace creation or selection. | Confirmed |
| AUTH-04 | Returning authenticated users shall enter their own workspace experience rather than receive a second workspace. | Derived requirement |
| AUTH-05 | Private routes and operations shall require a valid authenticated session and server-side workspace authorization. | Confirmed |
| AUTH-06 | Authentication failure, expired session, and provisioning failure shall not expose private data and shall provide a recoverable user-facing outcome. | Derived requirement |
| AUTH-07 | The specific authentication provider and supported login methods remain Open and shall not be implied in product copy or implementation planning until selected. | Open |

### 8.2 Workspace provisioning and isolation

| ID | Requirement | Source |
|---|---|---|
| TEN-01 | V1 shall maintain a one-user-to-one-personal-workspace product model. | Confirmed |
| TEN-02 | Every workspace-owned entity shall carry or resolve an authoritative workspace ownership relationship. | Derived requirement |
| TEN-03 | Every read, list, create, update, delete, approval, schedule, publish, asset, and connection operation shall enforce workspace ownership on the server/data-access boundary. | Confirmed |
| TEN-04 | User-supplied resource identifiers shall never be sufficient authorization. | Derived requirement |
| TEN-05 | AI tools, agent runs, queues/jobs, provider callbacks, logs, caches, and file access shall use the same workspace boundary as synchronous application requests. | Confirmed |
| TEN-06 | The system shall never substitute another workspace's brand data, campaign context, asset, social connection, token, or publishing destination. | Confirmed |
| TEN-07 | V1 shall not expose invitations, roles, shared access, workspace creation, workspace switching, or membership management. | Confirmed |

### 8.3 Brand profile

| ID | Requirement | Source |
|---|---|---|
| BRD-01 | Each workspace shall support one reusable brand profile. | Confirmed |
| BRD-02 | The profile shall support brand/product name, description, website URL, target audience, voice/tone, and an optional logo. | Confirmed |
| BRD-03 | The user shall be able to create, view, and update their profile. | Confirmed |
| BRD-04 | Campaign generation shall use the current workspace's saved profile when applicable. | Confirmed |
| BRD-05 | A campaign may override relevant brand details for that campaign without silently changing the saved profile. | Confirmed |
| BRD-06 | The experience shall make saved values and campaign-only overrides distinguishable before generation. | Derived requirement |
| BRD-07 | Profile and logo validation rules, minimum required fields, and website ingestion behavior remain Open. | Open |

### 8.4 Social account connections

| ID | Requirement | Source |
|---|---|---|
| CON-01 | An authenticated user shall be able to initiate, inspect, and remove supported social account connections made available through Zernio. | Confirmed/derived |
| CON-02 | Each connection and credential reference shall be bound to the current workspace and identifiable destination account/channel. | Confirmed |
| CON-03 | Secrets and tokens shall not be exposed in client-visible payloads, logs, prompts, or error messages. | Derived requirement |
| CON-04 | Connection status shall distinguish at minimum usable from unavailable/attention-required; exact provider-specific states remain subject to validation. | Derived requirement |
| CON-05 | Revoking or expiring a connection shall prevent new publication through that connection until it is restored. | Derived requirement |
| CON-06 | Initial supported channels, connection limits, token lifecycle, and Zernio's multi-user SaaS model remain Open pending provider validation. | Open |

### 8.5 Campaign creation

| ID | Requirement | Source |
|---|---|---|
| CMP-01 | A user shall be able to create a campaign with a natural-language request, structured details, or both. | Confirmed |
| CMP-02 | Structured details shall be capable of expressing applicable brand/product context, target audience, tone, platform selection, campaign goal, requested post count, and date range. | Confirmed |
| CMP-03 | Prompt and structured fields shall form one campaign request; they shall not create unrelated generation flows. | Confirmed |
| CMP-04 | The system shall identify contradictory inputs or apply an explicit, user-visible precedence rule before relying on them. | Derived requirement |
| CMP-05 | Campaign data shall be stored within the current workspace and remain available for later review and status tracking. | Confirmed |
| CMP-06 | The system shall reject unsupported platform selections or impossible input combinations with corrective guidance. | Derived requirement |
| CMP-07 | Post-count limits, campaign limits, prompt length, required fields, and precedence between prompt and form remain Open. | Open |

### 8.6 AI orchestration and generation

| ID | Requirement | Source |
|---|---|---|
| AI-01 | The generation workflow shall cover the logical responsibilities of orchestration, conditional research, platform-specific writing, visual decision-making, and content review. | Confirmed |
| AI-02 | Logical roles shall not require one model process per role; architecture shall preserve responsibilities without treating the role names as a framework mandate. | Confirmed |
| AI-03 | The orchestrator shall use only the current campaign's resolved brand and user inputs and explicitly permitted tool outputs. | Confirmed |
| AI-04 | Generated deliverables shall include a short strategy, independent post drafts, relevant hashtags where appropriate, suggested dates/times, and optional image proposals. | Confirmed |
| AI-05 | Drafts shall be adapted to the selected platform rather than emitted as an undifferentiated caption set. | Confirmed |
| AI-06 | The review responsibility shall check relevance, coherence, brand voice, and unsupported claims before content becomes user-reviewable. | Confirmed |
| AI-07 | AI output shall remain draft/recommendation content and shall not itself authorize a schedule or publish operation. | Confirmed |
| AI-08 | Generation failures shall preserve the campaign and expose a retry or recovery path that does not duplicate successful outputs without user awareness. | Derived requirement |
| AI-09 | Model providers, agent framework, model routing, retry limits, latency targets, and content-policy rules remain Open. | Open |

### 8.7 Conditional web research

| ID | Requirement | Source |
|---|---|---|
| RES-01 | The system shall be able to use web research for recent news, changing trends, external facts, and claims requiring verification. | Confirmed |
| RES-02 | The workflow shall be able to skip web research when saved/user-provided context and established knowledge are sufficient. | Confirmed |
| RES-03 | Research findings that influence content shall retain source references associated with the campaign or relevant post. | Confirmed |
| RES-04 | The workflow shall favor credible, relevant sources and shall not invent statistics, citations, or unsupported factual claims. | Confirmed |
| RES-05 | Research request volume shall be bounded by deterministic limits; exact limits are Open. | Confirmed/Open |
| RES-06 | If adequate support cannot be obtained, the workflow shall remove, qualify, or flag the claim rather than present it as verified. | Derived requirement |
| RES-07 | The review experience shall allow the user to inspect references for research-dependent content. | Derived requirement |
| RES-08 | Search provider, recency rules, source-quality policy, citation presentation, and retention period remain Open. | Open |

### 8.8 Visual assets

| ID | Requirement | Source |
|---|---|---|
| MED-01 | A post may use an AI-generated image, a rights-eligible web-discovered image, a user-uploaded image, or no image. | Confirmed |
| MED-02 | The system shall not require an image for every post and shall select visuals only where they add value. | Confirmed |
| MED-03 | The system shall permit at most two AI image-generation events per campaign. | Confirmed |
| MED-04 | Every generation and regeneration attempt that is accepted for execution shall consume the campaign budget; a regeneration shall not create a new allowance. | Confirmed |
| MED-05 | Budget enforcement shall be deterministic, concurrency-safe, and shared across all agents, posts, and entry points for the campaign. | Confirmed/derived |
| MED-06 | Once the budget is exhausted, the system shall block another AI generation before provider execution and explain the remaining alternatives. | Confirmed/derived |
| MED-07 | Web-discovered image records shall retain source and available license/usage information. | Confirmed |
| MED-08 | A web-discovered image with unclear rights shall remain a reference/suggestion and shall not be treated as publishable media. | Confirmed |
| MED-09 | The user shall be able to upload an image to their own workspace and associate it with an eligible post. | Confirmed |
| MED-10 | The product shall make image provenance and publishability status visible during review. | Derived requirement |
| MED-11 | Image providers, search provider, file types/sizes, storage, moderation, license-verification workflow, and meaning of provider-rejected/failed generation attempts for budget accounting remain Open. | Open |

### 8.9 Post review, editing, revision, and approval

| ID | Requirement | Source |
|---|---|---|
| PST-01 | Each generated post shall be independently reviewable. | Confirmed |
| PST-02 | Review shall expose the post text, hashtags, selected or proposed image, target platform/account, suggested schedule, and applicable sources/provenance. | Confirmed/derived |
| PST-03 | The user shall be able to manually edit editable post content. | Confirmed |
| PST-04 | The user shall be able to request a targeted AI revision or text regeneration for one post without overwriting unrelated posts. | Confirmed |
| PST-05 | The user shall be able to request an image change subject to rights rules and the remaining AI-image budget. | Confirmed |
| PST-06 | Approval shall be an explicit user action applied to a specific current post revision. | Confirmed/derived |
| PST-07 | A material change after approval shall invalidate the approval and return the post to a review-required state. | Confirmed |
| PST-08 | A non-material system metadata update shall not silently invalidate or transfer approval; the material-change boundary must be explicitly defined before implementation. | Derived/Open |
| PST-09 | Approval history shall be attributable to the authenticated user, post revision, and time for operational traceability. | Derived requirement |
| PST-10 | Bulk approval is not a confirmed V1 capability and shall not be assumed. | Open/not included |

### 8.10 Scheduling and publishing

| ID | Requirement | Source |
|---|---|---|
| PUB-01 | A user shall be able to choose or confirm a date/time for an approved post. | Confirmed |
| PUB-02 | The product shall treat AI timing suggestions as editable recommendations, not guaranteed performance predictions. | Confirmed |
| PUB-03 | Before accepting a schedule and again before external execution, the system shall verify workspace ownership, the exact approved revision, a usable workspace-owned connection, a supported destination, media eligibility, and required schedule data. | Confirmed/derived |
| PUB-04 | An unapproved, approval-invalidated, or otherwise ineligible post shall not be scheduled or published. | Confirmed |
| PUB-05 | Publishing shall use Zernio as the selected unified provider, subject to validated capability and contract behavior. | Confirmed |
| PUB-06 | Each external publishing attempt shall use an idempotency or reconciliation strategy that prevents unintended duplicates across retries, worker restarts, repeated requests, and callbacks. | Confirmed/derived |
| PUB-07 | The product shall expose truthful user-visible statuses for review, approval, scheduling, execution, publication, and failure; the detailed model appears in Section 9. | Confirmed/derived |
| PUB-08 | Provider failures shall be visible and shall not be represented as successful publication. | Confirmed |
| PUB-09 | Ambiguous outcomes shall be reconciled before a retry that could create a duplicate. | Derived requirement |
| PUB-10 | A schedule change that alters post content shall require reapproval; the treatment of time-only or destination-only changes must be settled in the material-change policy. | Confirmed/Open |
| PUB-11 | The user shall be able to identify the intended destination account and timezone context before confirming a schedule. | Derived requirement |
| PUB-12 | Scheduler ownership, Zernio-supported channels, media constraints, callback behavior, cancellation/rescheduling behavior, and retry policy remain Open pending validation. | Open |

### 8.11 Dashboard and management

| ID | Requirement | Source |
|---|---|---|
| UI-01 | The authenticated experience shall provide access to an overview, brand profile, campaigns, campaign detail, post review, scheduled-post/calendar view, social connections, publishing outcomes, and relevant settings. | Confirmed |
| UI-02 | Lists and detail views shall show only resources authorized for the current workspace. | Confirmed |
| UI-03 | The campaign view shall make each post's review, approval, schedule, and publishing condition understandable without implying that all campaign posts share one state. | Derived requirement |
| UI-04 | Failures and blocked actions shall explain the cause and the next corrective action without exposing secrets or blaming the user. | Derived requirement |
| UI-05 | Empty, loading, partial-success, stale-connection, and provider-degraded states shall be designed as first-class product states. | Derived requirement |
| UI-06 | Exact information architecture, navigation, component library, and visual design remain Open. | Open |

---

## 9. Lifecycle and state requirements

The following are product-level state semantics. Engineering may implement them differently if all transitions, guards, and observable behavior remain intact.

### 9.1 Campaign lifecycle

| State | Meaning | Allowed next outcomes |
|---|---|---|
| Draft input | Campaign request is being composed and has not begun generation. | Generating, abandoned/deleted subject to future deletion policy |
| Generating | The system is planning, researching if needed, and preparing deliverables. | Ready for review, partially ready, generation failed |
| Ready for review | Strategy and at least the expected reviewable post set are available. | In review |
| Partially ready | Some output exists but one or more components failed or require attention. | Generating/retry, in review for usable posts |
| In review | The user is editing, revising, and approving posts independently. | Remains in review; campaign-level summary may derive progress |
| Completed | All intended posts have reached a terminal or intentionally excluded outcome according to a policy still to be defined. | No implicit archival/deletion behavior assumed |
| Generation failed | No sufficiently reviewable result is available. | Safe retry or edit request |

A campaign-level label shall never override individual post eligibility.

### 9.2 Post content and approval lifecycle

```text
Draft/review required
        |
        | explicit approval of revision N
        v
Approved revision N
        |
        | material edit or applicable targeted regeneration
        v
Draft/review required (revision N+1)
```

Rules:

- Approval references an immutable content revision or equivalent content fingerprint.
- Scheduling and publishing re-check that the approved revision is still current.
- An AI-generated change and a manual change follow the same approval-invalidating rule when material.
- A failed publication does not grant approval to a newer revision.
- “Material change” must include changes to public text, hashtags when published as content, media, and any factual claim. Destination and time-change treatment remains an explicit open decision.

### 9.3 Publishing lifecycle

| State | Meaning | Required behavior |
|---|---|---|
| Review required | Current revision is not approved. | Cannot schedule or publish. |
| Approved | Current revision is approved but not scheduled. | Eligible for scheduling after validation. |
| Scheduled | An eligible post has a future execution plan. | Show time, timezone, destination, and ability/limits to change it once defined. |
| Publishing | External execution has begun and final outcome is not known. | Prevent unsafe duplicate initiation. |
| Published | Provider outcome is confirmed successful with available external reference metadata. | Show truthful completion. |
| Failed | Provider outcome is confirmed unsuccessful. | Show reason category and safe recovery action. |
| Outcome uncertain | The request may have succeeded but confirmation is absent or ambiguous. | Reconcile before retrying. Never label published without evidence. |
| Cancelled | A previously scheduled operation will not execute, if cancellation is supported. | Provider and application state must agree or show reconciliation need. |

Exact internal names may differ. The product must preserve the difference between confirmed failure and uncertain outcome.

### 9.4 Social connection lifecycle

At minimum, the user experience must distinguish:

- connected and usable;
- action required/expired/revoked;
- disconnected;
- connection status unknown due to provider availability.

The product must not silently route a post through a different connection when the selected connection is unavailable.

---

## 10. Information and ownership model

This is a conceptual product model, not a database schema.

| Concept | Ownership and important relationships |
|---|---|
| Authenticated identity | Resolves to exactly one V1 personal workspace. Provider representation is Open. |
| Workspace | Security and data-ownership boundary for all private product resources. |
| Brand profile | One per workspace; supplies reusable context. |
| Campaign | Belongs to one workspace; records input, resolved context, strategy, generation/research summary, and image budget. |
| Research finding/source | Belongs to one workspace and campaign; may support one or more post claims. |
| Post | Belongs to one campaign and workspace; targets a platform/destination and has independent lifecycle state. |
| Post revision | Represents reviewable public content and media selection; approval binds to a specific revision. |
| Approval record | Identifies user, post revision, and approval time; cannot authorize later material content. |
| Asset | Belongs to one workspace; retains type, provenance, rights/publishability state, and associations. |
| Image-generation event | Belongs to one campaign and contributes to its shared maximum of two. |
| Social connection | Belongs to one workspace; references a provider connection and destination without exposing secrets. |
| Schedule | Belongs to one post revision and selected connection; records time and timezone context. |
| Publishing attempt | Belongs to one schedule/post revision; records idempotency/reconciliation identity and provider outcome. |
| Agent run/tool result | Belongs to one workspace and campaign/post context; must not cross tenant boundaries. |

### 10.1 Data-classification expectations

| Class | Examples | Minimum handling expectation |
|---|---|---|
| Public | Landing-page copy | May be publicly accessible. |
| Private workspace content | Brand profile, campaign prompts, drafts, research, assets | Authorized workspace access only. |
| Sensitive integration data | Social connection identifiers, tokens, callback secrets | Server-side only where possible; encrypted/protected; never inserted into AI prompts or client logs. |
| Operational/audit data | Approvals, publishing attempts, job context, security events | Workspace-scoped access, limited internal access, and retention policy to be defined. |

Retention, export, deletion, account closure, and privacy-policy requirements are Open and must be decided before a public production launch.

---

## 11. Logical events and auditability

These events describe business facts the product must be able to observe or reconstruct. They do not mandate event sourcing, a vendor, or a particular analytics pipeline.

### 11.1 Required business events

| Event | Minimum useful context |
|---|---|
| WorkspaceProvisioned | workspace, authenticated identity reference, timestamp, outcome |
| BrandProfileUpdated | workspace, changed-field categories, actor, timestamp |
| SocialConnectionChanged | workspace, provider connection reference, destination/channel, previous/new condition, timestamp |
| CampaignSubmitted | workspace, campaign, selected platforms, requested post count if supplied, timestamp |
| CampaignGenerationStarted/Completed/Failed | workspace, campaign, run, outcome, duration, safe error category |
| ResearchDecisionRecorded | workspace, campaign, research used/skipped, reason category |
| ResearchSourceAttached | workspace, campaign/post, source reference, timestamp |
| ImageGenerationConsumed | workspace, campaign, resulting count, request/result category, timestamp |
| ImageGenerationBlocked | workspace, campaign, reason, current count, timestamp |
| PostRevisionCreated | workspace, campaign, post, revision, actor type, timestamp |
| PostApproved | workspace, campaign, post, revision, user, timestamp |
| PostApprovalInvalidated | workspace, campaign, post, old revision, new revision, reason category, timestamp |
| PostScheduled/Rescheduled/Cancelled | workspace, post revision, destination reference, scheduled time/timezone, actor, timestamp |
| PublishAttemptStarted | workspace, post revision, connection reference, attempt/reconciliation identity, timestamp |
| PublishOutcomeRecorded | workspace, post revision, attempt, confirmed state, safe provider/error category, timestamp |
| AuthorizationDenied | actor/session reference, requested resource type, safe reason, timestamp; avoid leaking another tenant's resource data |

### 11.2 Product analytics events

Analytics instrumentation may reuse business events but must not copy secrets, complete prompts, social tokens, or unnecessary private content into an analytics provider. Event names, vendors, consent, retention, and targets remain Open.

### 11.3 Audit requirements

- The team must be able to determine which post revision was approved and which revision was sent to the provider.
- The team must be able to determine why a third image-generation request was allowed or blocked.
- The team must be able to correlate a user-visible publishing state with a provider request/outcome without exposing a token.
- Security logs must avoid revealing whether a resource identifier belongs to another user.

---

## 12. Non-functional product requirements

### 12.1 Security and privacy

- Default-deny authorization for workspace-owned resources.
- Server-side checks at every data and side-effect boundary.
- Secure handling and rotation/revocation capability for credentials as supported by the chosen providers.
- Protection against cross-tenant access through direct requests, agent tools, background jobs, media URLs, callbacks, caches, and logs.
- User-facing errors that do not expose secret values, provider payloads containing secrets, or another tenant's resource existence.
- Threat modeling and negative isolation tests before real-user deployment.

### 12.2 Reliability and consistency

- Workspace provisioning must be idempotent so signup retries do not create multiple V1 workspaces.
- Image-budget accounting must remain correct under concurrent requests and worker retries.
- Approval checks must be performed against the current revision at schedule time and execution time.
- Publishing must use idempotent execution or provider reconciliation to prevent duplicates.
- Partial AI or provider failures must not corrupt previously valid user work.
- Timezone handling must preserve the user's intended wall-clock schedule and display the effective timezone.

### 12.3 Performance

No numerical latency or availability targets are confirmed. Before engineering sign-off, the team must set targets for interactive page operations, campaign-generation feedback, background progress visibility, and publishing-status freshness. The experience must not present a long-running operation as frozen; it needs visible progress or a background/pending state.

### 12.4 Accessibility and responsive use

The product should support keyboard operation, visible focus, semantic labels, readable contrast, accessible status/error announcements, and responsive review/scheduling workflows. The governing accessibility standard and browser/device support matrix remain Open and must be selected before design acceptance.

### 12.5 Observability and supportability

- Correlate authenticated request, workspace, campaign/post, agent run, job, and provider attempt using non-secret identifiers.
- Track generation, research, image-budget, scheduling, provider, callback, and authorization failures.
- Make operational state sufficient to reconcile uncertain publishing outcomes.
- Define alerts and service objectives only after architecture and traffic expectations are known.

### 12.6 Cost controls

- Enforce image-generation caps outside model prompts.
- Bound web research calls and agent retry behavior outside model prompts.
- Prevent duplicate paid calls caused by uncontrolled job retry.
- Make model, search, image, storage, and publishing costs observable by safe internal dimensions before scale.

---

## 13. Acceptance criteria by capability

### AC-01 — First-user provisioning

**Given** a visitor completes signup successfully for the first time, **when** the authenticated experience loads, **then** exactly one personal workspace exists for that identity and the user reaches its dashboard without creating or selecting a workspace.

**And given** the same provisioning operation is retried, **then** it resolves to the same V1 workspace rather than creating another.

### AC-02 — Cross-user isolation

**Given** User A and User B own separate workspaces, **when** User A supplies an identifier for User B's campaign, post, asset, connection, schedule, or job through any supported endpoint or tool, **then** the operation reveals no private data and performs no read, mutation, publication, or background action against User B's resource.

### AC-03 — Brand reuse and overrides

**Given** a user has a saved brand profile, **when** they create a campaign with a campaign-only tone or audience override, **then** generation uses the resolved campaign context and the saved profile remains unchanged unless the user separately updates it.

### AC-04 — Hybrid campaign input

**Given** a valid short prompt with no optional structured values, **when** the user submits it, **then** one campaign-generation flow begins.

**And given** structured values are supplied, **then** those values refine the same campaign request according to a visible precedence/validation rule.

### AC-05 — Conditional research

**Given** a request relies on recent external facts, **when** generation succeeds, **then** relevant research references are retained and inspectable.

**Given** ordinary user-owned brand context is sufficient, **when** generation runs, **then** it can complete without a web-research request.

**Given** adequate evidence cannot be found, **then** unsupported claims are removed, qualified, or visibly flagged.

### AC-06 — Reviewable campaign output

**Given** campaign generation completes successfully, **then** the user receives a short strategy and independent platform-appropriate posts with relevant hashtags and suggested scheduling information, while images remain optional.

### AC-07 — AI image budget

**Given** a campaign has consumed two accepted AI image-generation events, **when** a user, agent, repeated request, or concurrent request attempts another, **then** application logic blocks provider execution and offers permitted alternatives.

**And** text regeneration, user upload, or rights-eligible web-image selection does not incorrectly reset or increase the AI image budget.

### AC-08 — External-image safety

**Given** a discovered image lacks sufficient usage-rights information, **when** the user reviews the post, **then** the image is identified as a reference/suggestion and cannot flow directly into publication as an eligible asset.

### AC-09 — Targeted revision

**Given** a campaign contains multiple posts, **when** the user manually edits or requests an AI revision for one post, **then** a new revision is created for that post and unrelated posts are not overwritten.

### AC-10 — Approval binding

**Given** the user explicitly approves revision N, **when** public content is materially changed to revision N+1, **then** the prior approval is invalid and the new revision cannot be scheduled or published until explicitly approved.

### AC-11 — Scheduling eligibility

**Given** a post is not approved, its approval is stale, its destination connection is unusable, or its media is ineligible, **when** scheduling is attempted, **then** the system blocks the operation and explains the corrective action.

### AC-12 — Execution-time revalidation

**Given** a valid post was scheduled, **when** its execution time arrives, **then** the background operation revalidates the current approved revision, workspace-owned connection, destination, and media eligibility before calling the provider.

### AC-13 — Publishing outcome

**Given** Zernio confirms success, **then** the post becomes published with available safe reference metadata.

**Given** Zernio confirms failure, **then** the post becomes failed and the error is visible.

**Given** the result is ambiguous, **then** the product records an uncertain outcome and reconciles it before any retry that could duplicate publication.

### AC-14 — Publishing isolation

**Given** a queued job or provider callback contains stale, tampered, or mismatched workspace/connection context, **when** it is processed, **then** no post is sent using another workspace's social connection and the event is safely rejected and observable.

### AC-15 — Truthful dashboard

**Given** a campaign contains posts in different states, **when** the user views it, **then** each post's current review, approval, scheduling, and publishing state is clear and a campaign summary does not falsely imply every post has the same outcome.

---

## 14. Dependencies and validation work

### 14.1 Zernio dependency

Zernio is a confirmed product choice but its relevant behavior is not yet validated in this PRD. Before implementation commitments, verify directly against current provider documentation, account terms, and a test integration:

- supported social channels and account types;
- whether the intended multi-user SaaS connection model is permitted and supported;
- connection authorization, refresh, expiry, revocation, and secure token model;
- text, hashtag, media, per-channel length, file, and format constraints;
- immediate publishing versus provider-owned scheduling;
- timezone interpretation;
- idempotency support;
- status lookup, callbacks/webhooks, signature verification, ordering, and replay behavior;
- failure, rate-limit, timeout, and ambiguous-outcome semantics;
- cancellation, edits, rescheduling, and deletion behavior;
- plan limits, pricing, and production approval requirements.

No supported-channel promise should appear in launch scope until this validation is recorded.

### 14.2 AI, research, and image dependencies

Providers are not selected. Evaluation must compare output quality, structured-output/tool support, latency, cost, rate limits, safety behavior, data handling, retention/training terms, regional availability, and failure behavior. The product's authorization, approval, and budget controls must remain provider-independent.

### 14.3 Media and rights

Before enabling external-image publication, legal/product review must define what evidence makes an asset publishable, what attribution must be shown or included, how a user confirms rights, and how takedown or disputed rights are handled. Search-result presence alone is insufficient.

---

## 15. Risks and mitigations

| Risk | Product impact | Required mitigation direction |
|---|---|---|
| Cross-tenant data or credential leakage | Severe privacy/security failure | Server-side tenant scoping, negative tests, scoped jobs/tools, protected media, safe logs. |
| Unapproved or stale content published | Loss of trust and public harm | Revision-bound approval; schedule- and execution-time guards. |
| Duplicate provider publication | Public duplication and user cleanup | Idempotency, attempt ledger, callback deduplication, uncertain-outcome reconciliation. |
| Hallucinated facts or sources | Reputation and misinformation risk | Conditional research, retained references, review checks, qualify/remove unsupported claims. |
| Unsafe web-image reuse | Copyright/licensing exposure | Provenance and rights state; block unclear assets from publishable path. |
| Image cap bypass or runaway AI calls | Unexpected cost | Atomic shared campaign counter and bounded retries outside prompts. |
| Provider limits differ from proposed UX | Broken schedules or unsupported content | Complete Zernio validation before platform commitments and design finalization. |
| Long generation latency | Abandonment and duplicate submissions | Progress/pending experience, idempotent requests, recoverable retries; set target after provider tests. |
| Social token expiry | Missed scheduled posts | Connection-health visibility, execution-time check, actionable reauthorization path. |
| Ambiguous material-change policy | Approval errors and user confusion | Decide and document field-by-field invalidation rules before implementation. |
| Weak market evidence | Build may not address the most urgent need | Run focused primary-user discovery and usability tests alongside shaping. |
| Over-scoped V1 | Delayed end-to-end proof | Preserve personal-workspace boundary; defer collaboration, billing, and advanced analytics. |

---

## 16. Open decisions and decision owners

The named role is the recommended accountable function, not an assumption about current staffing.

| ID | Decision needed | Why it matters | Recommended owner | Required before |
|---|---|---|---|---|
| O-01 | Initial Zernio-supported social platforms | Determines content constraints, connection UX, and launch claims. | Product + Engineering | Final V1 scope/design |
| O-02 | Authentication provider and login methods | Determines onboarding, identity mapping, recovery, and security. | Engineering + Product | Architecture sign-off |
| O-03 | LLM, research, image-generation, and image-discovery providers | Determines quality, cost, latency, privacy, and tool behavior. | Product + Engineering | Architecture/prototype |
| O-04 | Application stack, storage, deployment, job mechanism, and secrets strategy | Determines implementation and operations. | Engineering | Implementation plan |
| O-05 | Application-owned versus Zernio-owned schedule execution | Determines lifecycle, retry, cancellation, and observability. | Engineering + Product | Scheduling design |
| O-06 | Media storage, moderation, provenance, attribution, and rights-confirmation UX | Determines legal safety and publishability. | Product + Design + Legal/appropriate reviewer | Media workflow acceptance |
| O-07 | Campaign, post, research, agent-run, upload, and time-based quotas | Determines cost and abuse controls. | Product + Engineering | Public beta |
| O-08 | Material-change and approval-invalidation matrix | Determines the core human-control guarantee. | Product + Design + Engineering | Post-review implementation |
| O-09 | Timezone source, display, travel/change behavior, and DST policy | Prevents incorrect publication time. | Product + Engineering | Scheduling implementation |
| O-10 | Provider retry, reconciliation, and user-initiated retry policy | Prevents duplicates and misleading outcomes. | Engineering + Product | Publishing implementation |
| O-11 | Minimum required brand/campaign inputs and prompt/form precedence | Determines validation and first-use friction. | Product + Design | Campaign prototype |
| O-12 | Deletion, retention, export, account closure, and privacy policy | Determines user rights and operational data lifecycle. | Product + Engineering + appropriate legal reviewer | Production launch |
| O-13 | Accessibility standard, browser/device matrix, and localization/time format | Determines design/test acceptance. | Product + Design + Engineering | UI acceptance |
| O-14 | Numerical success, reliability, performance, and cost targets | Enables launch and iteration decisions. | Product + Engineering | Beta plan |
| O-15 | Billing, subscriptions, pricing, or later usage-based packaging | Changes entitlement and quota requirements if added. | Product | Separate future scope decision |
| O-16 | Advanced analytics and engagement reporting | Requires additional provider/data permissions and product surface. | Product | Separate future scope decision |

No open decision should be resolved implicitly through an implementation shortcut.

---

## 17. Delivery approach and launch gates

No delivery dates or fixed appetite were provided, so this PRD does not invent a schedule. A delivery plan should preserve an end-to-end thin slice and validate high-risk dependencies early.

### 17.1 Recommended shaping sequence

1. **Provider feasibility:** Validate Zernio's SaaS, channel, scheduling, media, status, webhook, and idempotency behavior.
2. **Core contract prototype:** Shape workspace ownership, campaign/post revisions, approval binding, and publishing eligibility without selecting unnecessary product breadth.
3. **Functional experience prototype:** Test onboarding, hybrid campaign creation, post review, approval invalidation, schedule confirmation, and failure states with target users.
4. **AI quality prototype:** Compare provider options on representative brand/campaign cases, current-fact research, platform adaptation, citations, and targeted revision.
5. **Media safety prototype:** Test optional visual selection, two-event enforcement, uploads, provenance, rights state, and blocked paths.
6. **End-to-end implementation:** Deliver the smallest supported-channel flow that satisfies the hard success gates.

### 17.2 Product readiness gate

- Primary user and core problem have been tested with representative users.
- Initial platforms and launch claims are confirmed.
- Open decisions affecting visible behavior are resolved and recorded.
- The post material-change matrix and image-rights UX are approved.
- Error states and recovery paths are included in the design.

### 17.3 Engineering/security readiness gate

- Architecture review covers identity mapping, tenancy, secret handling, jobs, provider callbacks, idempotency, and reconciliation.
- Automated tests cover direct and indirect cross-tenant access, approval bypass, concurrent image-budget attempts, execution-time revalidation, and callback/job tampering.
- Provider test integration demonstrates the selected channel/media/scheduling path.
- Observability can trace generation and publishing without logging secrets or unnecessary private content.
- Threat model and operational recovery runbook are reviewed.

### 17.4 Real-user V1 acceptance gate

- Two separate real users complete the full successful flow in isolated workspaces.
- Negative isolation and authorization scenarios pass.
- The third AI image-generation attempt is blocked across all tested entry points.
- Material edits invalidate approval.
- A provider failure is surfaced accurately.
- An ambiguous/retried provider flow does not duplicate a live post.
- Known limitations and unsupported channels are visible and truthful.

---

## 18. Traceability matrix

| Confirmed overview decision | Primary PRD coverage |
|---|---|
| Multi-user AI social-media SaaS | Sections 1, 2, 4, 8 |
| Automatically created private individual workspace | AUTH-03–06, TEN-01–07, AC-01–02 |
| One saved brand profile with campaign overrides | BRD-01–07, AC-03 |
| Hybrid prompt and structured campaign input | CMP-01–07, AC-04 |
| Coordinated autonomous agent responsibilities | AI-01–09 |
| Conditional web research with references | RES-01–08, AC-05 |
| Strategy, platform posts, hashtags, timing, optional images | AI-04–06, AC-06 |
| Maximum two AI image generations per campaign | MED-03–06, AC-07 |
| Web images require rights awareness | MED-07–11, AC-08 |
| User uploads and text-only posts | MED-01–02, MED-09 |
| Independent post review and targeted revision | PST-01–05, AC-09 |
| Explicit approval of current content | PST-06–10, AC-10–12 |
| Zernio publishing integration | CON-01–06, PUB-01–12, Section 14 |
| Visible failures and duplicate-safe retries | PUB-06–09, AC-13–14 |
| Dashboard and management areas | UI-01–06, AC-15 |
| No teams, multi-workspace, AI video, unlimited images, or autonomous publishing | Sections 4.2 and 6.2 |
| Two-real-user V1 success definition | Sections 4.3 and 17.4 |

---

## 19. Review checklist

Before this PRD is marked approved:

- [ ] The product owner confirms that the core problem and V1 outcome are accurate.
- [ ] Every confirmed overview decision is represented without contradiction.
- [ ] Requirements define behavior and constraints without prematurely choosing implementation details.
- [ ] Open decisions remain visibly open and have an owner and decision deadline/gate.
- [ ] Design reviews the journeys, alternate paths, error states, approval invalidation, and media-rights experience.
- [ ] Engineering reviews provider feasibility, identity/tenancy, concurrency, job execution, timezones, idempotency, callbacks, and observability.
- [ ] Security review covers all synchronous and asynchronous cross-tenant boundaries.
- [ ] Acceptance criteria are testable in the deployed product, not only with mocks.
- [ ] Success metrics receive baselines and targets where the overview currently provides none.
- [ ] Scope additions are either removed or explicitly approved as V1 changes.

---

## Appendix A — Confirmed decisions

1. The product is a multi-user AI social media SaaS.
2. Each user has one automatically created private personal workspace.
3. V1 has no teams, invitations, roles, or workspace switching.
4. Each workspace has one reusable brand profile with campaign-level overrides.
5. Campaign input combines a prompt and optional structured fields.
6. AI responsibilities include orchestration, conditional research, platform writing, visual decisions, and content review.
7. Research is conditional and retains references when used.
8. Campaign output includes a strategy, posts, hashtags, suggested timing, and images only where useful.
9. A campaign can consume at most two AI image-generation events, including regenerations.
10. Other visual paths are rights-eligible web discovery, user upload, or no image.
11. Each post is independently editable, revisable, and approvable.
12. Explicit human approval of current content is required before scheduling or publishing.
13. Material changes after approval require reapproval.
14. Zernio is the selected unified publishing provider, pending capability validation.
15. V1 excludes AI-generated video and fully autonomous approval-free publishing.

## Appendix B — Explicitly unresolved topics

The following are not requirements until resolved: exact social channels, identity provider and login methods, AI/search/image providers, technology stack, database, hosting, job system, scheduling ownership, media-rights verification details, general usage quotas, billing, advanced analytics, detailed design system, and numerical performance/reliability targets.

## Appendix C — Glossary

| Term | Meaning in this PRD |
|---|---|
| Workspace | The private V1 ownership and authorization boundary automatically associated with one user. |
| Brand profile | The workspace's single reusable set of brand/product context. |
| Campaign | A user goal plus resolved context that produces a strategy and a set of independently managed posts. |
| Post revision | A specific reviewable version of a post's public content and associated publishable media. |
| Approval | The user's explicit authorization of one specific current post revision; not permission for future material changes. |
| Material change | A change that can affect what the public sees or the truth/meaning of the post and therefore invalidates approval; exact matrix remains to be finalized. |
| AI image-generation event | An accepted attempt to invoke AI image generation for a campaign; regenerations count toward the maximum of two. Exact treatment of provider-rejected attempts remains Open. |
| Research reference | A retained source record supporting external/current information used in campaign content. |
| Publishable asset | An asset that satisfies product validation and applicable usage-rights conditions for the intended post. |
| Outcome uncertain | A publishing attempt that may have succeeded but lacks enough evidence to safely label successful or retry without reconciliation. |
| Zernio | The selected unified social publishing integration; supported behavior must be validated before implementation commitments. |


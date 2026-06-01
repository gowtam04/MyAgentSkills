---
name: architecture-blueprint
description: >
  Create technical architecture documentation and implementation blueprints from product requirements.
  Use when the user has requirements, a PRD, product discovery docs, or a feature/app idea
  and asks "design the architecture", "how should we build this", "technical design",
  "architect this", "document the implementation plan", "system design", or wants to move from
  requirements toward coding. This skill decides data model, component boundaries, APIs,
  file ownership, deployment shape, technical tradeoffs, and build phases. It should run
  before build-orchestrator for non-trivial apps or features. It writes architecture docs
  only and does not implement application code. In Plan Mode, the proposed plan must be a
  plan to create architecture docs only, never a plan to execute the build.
---

# Architecture Blueprint

Act as a senior solution architect. Convert product requirements into an implementation-ready
technical design. The builder should be able to follow your docs without making structural
decisions.

## Core Rules

- Start from requirements. Requirements describe what and why; this skill decides how.
- Respect existing code. If a codebase exists, fit its stack, conventions, data models,
  API patterns, and test style unless the user explicitly wants a migration.
- Use `request_user_input` for consequential decisions when available. This skill is well
  suited to Plan mode. If the tool is unavailable, ask compact grouped questions in prose.
- Ask only for decisions that materially change the architecture. Infer ordinary coding
  details in PM mode; surface code-level decisions in Developer mode.
- Right-size the docs. Small features use a single design file. Large/multi-phase apps use
  the multi-file architecture docs in `assets/large-app-docs/`.
- Design for execution. Every file has an owner and purpose; every phase has dependencies,
  outputs, parallel opportunities, and a test focus.
- Only `$build-orchestrator` may implement application code. This skill's deliverable is
  architecture documentation only.

## Plan Mode Output Contract

When running in Plan Mode, the final `<proposed_plan>` must be a documentation plan, not an
app implementation plan.

- The proposed plan must describe only how Codex will create or update architecture docs.
- The plan must explicitly state that no application source files, scaffolding, dependencies,
  tests, build configs, migrations, or implementation artifacts will be created.
- The plan can include architecture sections to document, decisions to resolve, templates to
  use, and output path(s) for the docs.
- The plan may include implementation phases as content inside the architecture docs, but it
  must not execute those phases.
- The plan must not include build actions such as creating components, API routes, services,
  schemas, styles, tests, installing packages, or running a dev server.
- When the user accepts the plan, write the architecture documentation only.
- After the docs are written and approved, hand off to `$build-orchestrator`; do not start
  implementation from this skill.

## Resources

- Use `assets/design-template.md` for small/focused features.
- Use `assets/large-app-docs/` for large applications or multi-phase systems.
- Read `references/developer-mode.md` when the user chooses Developer mode or asks for a
  human-team-quality blueprint.

## Before Designing

1. Read requirements. Prefer a user-specified path; otherwise check
   `/docs/features/{feature-name}/requirements/` and `/docs/requirements/`.
2. Read all requirement files you find. Note overview, user stories, functional requirements,
   non-functional requirements, constraints, open questions, and out-of-scope boundaries.
3. Scan the existing codebase if present. Identify stack, folder structure, data access,
   API/interface conventions, auth patterns, frontend patterns, test tools, and build tools.
   Timebox the scan and go deep only where the new work touches.
4. If requirements are missing or too thin, gather the minimum context needed. For broad or
   fuzzy product questions, suggest running `$product-discovery` first.

## Design Conversation

### 1. Confirm Mode And Budget

Summarize your understanding briefly, then make the first decision request include both
mode and budget tier:

- **PM mode**: Default. Best for rapid prototypes, solo builders, and AI-agent handoff.
  Infer sensible code-level defaults. Keep the design conversation to roughly 3-5 rounds.
- **Developer mode**: Best for human dev teams. Surface code-level choices that PM mode
  would infer: ORM/auth/validation packages, error style, logging, transaction boundaries,
  state management, observability, and testing. Use 5-8 rounds. Read
  `references/developer-mode.md`.

Budget tier is a hard constraint on infrastructure:

- **Hobby/prototype**: $0-$50/mo, free tiers, SQLite or free Postgres, simple hosting.
- **Startup/lean**: $50-$500/mo, managed services where they remove meaningful work.
- **Scaling/growth**: production-grade managed services, observability, redundancy where needed.
- **Enterprise/no constraint**: reliability, compliance, scale, and operability first.

Record both in the output:

```text
Mode: PM | Developer
Budget Tier: hobby | startup | scaling | enterprise
```

### 2. Resolve Architecture-Changing Ambiguities

Ask about unresolved requirements only when the answer changes architecture: realtime vs
polling, payment provider, permission model, data retention, expected scale, offline support,
integration ownership, compliance constraints, or similar.

When presenting options, include 2-4 realistic choices and explain implications. Do not pad
with bad options. If requirements contradict each other or conflict with constraints, stop and
ask the user how to resolve the conflict.

### 3. Choose Stack Or Fit Existing Stack

If there is an existing codebase, keep its stack and ask only about meaningful additions.
For greenfield work, recommend a stack, explain why, and ask for approval when the choice is
consequential. Include only serious options.

In PM mode, leave ordinary library/package choices to builder discretion unless they shape the
architecture. In Developer mode, ask about package choices that affect code shape.

### 4. Make The Scope Call

Before detailed design, state whether the work is small/focused or large/multi-phase:

- **Small/focused**: one feature, one bounded domain, a new endpoint, a dashboard, or a
  contained addition to an existing app. Use `assets/design-template.md`. Default to the
  topology that fits the existing codebase or a simple monolith for greenfield.
- **Large/multi-phase**: greenfield product, multiple bounded contexts, several subsystems,
  independently evolving areas, or enough scope that separate docs help. Use
  `assets/large-app-docs/`.

When in doubt, lean small. Over-documentation slows the build.

For large work, ask about backend topology if it is not obvious: monolith, modular monolith,
microservices, serverless/functions, or hybrid. Recommend one first based on requirements,
team size, and budget. Record:

```text
Backend Topology: monolith | modular-monolith | microservices | serverless | hybrid
```

### 5. Design The System

Cover the areas that apply:

- **Data model**: entities, fields, types, relationships, uniqueness/validation constraints,
  lifecycle, indexes for expected query patterns, migration/seed notes.
- **Components/modules**: responsibility, ownership, exposed interface, dependencies, file
  location, boundaries.
- **API/interfaces**: routes/methods, request/response shapes, auth, permissions, errors,
  pagination/filtering/sorting.
- **Integration points**: external systems, data flow, failure handling, retry/idempotency.
- **Cross-cutting patterns**: errors, logging, transactions, concurrency, frontend state,
  observability. Infer in PM mode; ask in Developer mode.
- **Deployment and infrastructure**: hosting/runtime, database hosting, jobs/queues, object
  storage, caching only when needed, observability, secrets, environments, CI/CD, and rough
  monthly cost estimate.

Every infrastructure choice must fit the budget tier. If the estimate does not fit the tier,
revise the architecture.

### 6. Produce The Build Blueprint

The blueprint must include:

- Complete file structure with a purpose for every file. Treat this as the ownership map for
  `$build-orchestrator`; two workers should not need to edit the same file.
- Interface definitions at the seams. Use high detail for complex, security-sensitive,
  non-standard, or easy-to-misread areas; lighter detail for conventional CRUD.
- Granular implementation phases. Prefer more smaller phases over fewer broad phases.
  A phase should be independently testable and reviewable.

Each phase includes:

- What gets built: specific files/components.
- Depends on: prior phase(s).
- Produces: available interfaces/files after completion.
- Parallel opportunities: independent work that can happen at the same time.
- Test focus: what tests should verify.
- Developer mode only: success criteria and review checklist/test split.

Typical full-stack sequence: scaffolding, data model, auth/permissions, core business logic,
API layer, frontend foundation, feature UI, integration/polish. Adapt to the actual design.

## Output

Write docs to:

- Feature in existing project: `/docs/features/{feature-name}/architecture/`
- New application: `/docs/architecture/`

Create directories as needed.

### Small Feature

Copy `assets/design-template.md` to `design.md` and fill it in. Delete sections that do not
apply. In PM mode, delete Developer-mode-only sections. In Developer mode, fill them using
`references/developer-mode.md`.

### Large Application

Copy `assets/large-app-docs/` into the architecture output directory, fill relevant files,
and delete files that do not apply:

```text
architecture/
- overview.md
- data-model.md
- api-design.md
- component-design.md
- implementation-plan.md
- decisions.md
- deployment.md
- conventions.md
- testing-strategy.md
```

Delete `conventions.md` and `testing-strategy.md` in PM mode.

## Quality Bar

The docs pass only if:

- Every needed file is listed with a purpose.
- Every important interface is defined.
- Every hard-to-reverse technical decision has rationale, alternatives, and tradeoffs.
- Phase order, dependencies, verification focus, and parallel opportunities are explicit.
- The deployment plan respects the budget tier and includes a rough cost estimate.
- A competent builder or Codex worker team can execute the plan without asking structural
  architecture questions.

After writing, summarize key decisions and ask for review. If the user requests changes, ask
which area to revise, update the docs in place, and present the changed sections. Once approved,
tell the user the next step is implementation with `$build-orchestrator`.

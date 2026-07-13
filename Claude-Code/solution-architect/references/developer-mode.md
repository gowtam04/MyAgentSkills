# Developer mode

Read this when the user picked **Developer mode** in Phase 1, or asked partway through to "go deeper" / "loop in the devs."

## What Developer mode is

The architect always runs in one of two modes, picked by the first AskUserQuestion of the conversation:

- **PM mode (default)** — for rapid prototyping, solo PM work, or handoff to an AI agent team. You infer sensible code-level choices (naming patterns, error-handling style, test framework, library picks within the chosen stack) without asking. Budget 3-5 AskUserQuestion rounds. Output is the standard template.
- **Developer mode** — for handoff to a human dev team that wants a say in code-level practices. The shift isn't "more sections" — it's **stop inferring, start asking**: every design choice you'd otherwise silently infer becomes an explicit AskUserQuestion, however minute, so the team can weigh in. More rounds, plus the extra output sections below.

Mode is orthogonal to the small-feature vs large-app template choice and to the agent-features "thin pass" (see `agent-features.md`) — any combination is valid. Regardless of mode, the chosen mode goes on the `## Overview` line of the output as `Mode: PM` or `Mode: Developer`; that line is how `dev-team` detects the mode downstream.

## Round budget

PM mode caps at 3-5 rounds. In Developer mode, extend to **5-8 rounds**, batched aggressively (up to 4 closely related questions per call). The budget exists to prevent a lengthy interview, not to suppress real decisions — if you're about to silently infer a code-level choice the dev team could have an opinion on, make it a question instead. Cluster conventions, testing, and cross-cutting patterns into as few rounds as possible.

## Phase 2 — architectural package picks

In PM mode you "leave room for builder discretion" on implementation-level tooling. In Developer mode that default flips for the packages where the *choice shapes the code itself*. If you're about to assume one of these, ask instead:

- ORM / query builder (Prisma vs Drizzle vs raw SQL; SQLAlchemy vs Tortoise; ActiveRecord)
- Auth library (NextAuth/Auth.js vs Clerk vs custom JWT; Devise vs custom)
- Validation library (Zod vs Yup vs Valibot; Pydantic vs Marshmallow)
- HTTP client (fetch wrapper vs axios vs got; httpx vs requests)
- Queue client (BullMQ vs pg-boss; Celery vs RQ; Sidekiq)
- Cache client (ioredis vs node-redis; redis-py vs aioredis)
- Logger (pino vs winston; structlog vs stdlib)
- Test runner (Vitest vs Jest; pytest vs unittest)

Batch these with other Dev-mode decisions where it keeps rounds down. Skip anything that isn't a genuine choice in the user's stack (don't ask about ORMs if there's no database). Still leave bundlers, lint-plugin versions, lockfile tooling, and other non-architectural picks to the builder.

## Phase 3 — cross-cutting patterns

In PM mode you infer defaults for these and move on. In Developer mode every item below becomes an explicit AskUserQuestion — the team's opinion here shapes every file they write. Batch aggressively (up to 4 per call):

- **Error handling style.** Exceptions-bubble-up vs Result/Either type vs error-envelope return shape. Decides every function signature and every API response.
- **Logging library + structured log schema.** Which logger, what fields are required on every log line (request_id, user_id, feature, etc.), what goes to stdout vs an external sink.
- **Transaction / concurrency boundaries.** Where transactions start and end (per-request? per-service-call?), optimistic vs pessimistic locking, how retries are handled.
- **State management pattern (frontend).** Zustand vs Redux vs Jotai vs React Context; server-state lib (React Query vs SWR vs RTK Query); form state approach.
- **Observability stance.** Metrics (what's measured, which library), tracing (OpenTelemetry? vendor SDK? none?), error tracking (Sentry vs alternatives vs none).

Skip items that don't apply (no frontend → no state management; no APIs → no request-level tracing). For items that do apply, surface the choice even if you have a strong recommendation — state the recommendation in the option description so the team can defer to it easily.

## Phase 4 — interface detail and per-phase gates

**Interface Definitions:** the PM-mode "scale detail to complexity" default flips. Default to **high detail** for every interface — full signatures, complete I/O types with field-level specs, error types, behavior notes. The "light detail" option only applies to trivially generated or mechanically conventional files (boilerplate model types, one-line route files that just forward to a handler). New test: **would a senior dev have an opinion about this?** In Developer mode they almost always do — so specify it. This same bar applies in PM mode whenever the consumer is an autonomous/agentic implementer that can't ask back (the main SKILL's Interface Definitions note points here): the driver is the consumer's inability to ask, not the mode label. In Developer mode the interfaces also pair with `## Code Conventions` / `## Testing Strategy` (or `conventions.md` / `testing-strategy.md`); the test-author reads all three.

**Implementation Phases:** each phase carries two extra fields on top of the PM-mode set:
- **Success criteria** — acceptance criteria beyond "tests pass." Concrete, reviewable outcomes (e.g., "Phase complete when: migrations run cleanly on an empty DB, all new entities load via the repository, no orphaned FKs.").
- **Review checklist / test split** — the unit vs integration split for this phase, what gets mocked vs run for real, and any specific review gates (code review required? security review? perf check?). This gives `dev-team` a precise spawn-prompt for the implementer and reviewer on the phase.

## Output additions

**Smaller feature (`design.md`):** fill in the two Developer-mode sections the template marks (and that PM mode deletes):

- `## Code Conventions` — naming patterns, module boundaries, error-handling style + envelope shape, logging library + required structured fields, lint/format stance, cross-cutting patterns (transactions, concurrency, frontend state management). If a decision was surfaced as a question and answered, record the answer here with a brief rationale.
- `## Testing Strategy` — test framework, unit vs integration split, mocking policy (what's real, what's faked), coverage target, fixture conventions, how eval harnesses (if any) are wired.

**Large app:** instead of sections, add two files alongside the rest: `conventions.md` (same content as `## Code Conventions`) and `testing-strategy.md` (same content as `## Testing Strategy`). The stubs in `assets/large-app-docs/` already include both, marked Developer-mode-only.

When you wrap up, tell the user the output includes these extra pieces and that `dev-team` uses them to spawn better implementer/reviewer prompts.

## Mid-conversation mode switch

The user can upgrade PM→Developer at any point ("actually, let me loop in my devs — can you go deeper?"). When this happens: fire a follow-up AskUserQuestion batch to capture the code-level decisions PM mode skipped (conventions, testing, error handling, logging, any package-level picks you'd inferred), then append `## Code Conventions` and `## Testing Strategy` to the already-written docs (or add `conventions.md` + `testing-strategy.md` for a large app) and update the `Mode:` line on the Overview to `Developer`.

Downgrade Developer→PM after docs are written isn't supported — the extra sections are additive and harmless for downstream readers, so offer to trim them by hand if the user insists, but don't automate the downgrade.

## Developer mode without developers in the room

If a PM is running the skill solo but wants Developer-mode output to hand to a team later, proceed normally — but you're still the architect, so **recommend, don't punt**. Make a concrete recommendation for every code-level choice, mark each one in the output as `Proposed — confirm with dev team`, and list them all under `## Unresolved from Requirements` as follow-ups. The dev team then reviews, keeps the recommendations they agree with, and overrides the rest before `dev-team` picks the docs up.

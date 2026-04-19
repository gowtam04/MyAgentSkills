---
name: dev-team
description: >
  Orchestrate Claude Code agent teams for implementing features, building applications, and completing
  complex multi-file tasks. Use this skill whenever the user asks to create a "dev team", "agent team", "swarm",
  "build team", or requests parallel implementation with coordinated roles. Also trigger when the user
  describes a task that clearly needs multiple specialized agents — such as building a full-stack feature,
  implementing a system with backend + frontend + tests, or any project where work can be split across
  domain-specialized teammates. If the user says things like "build this with a team", "coordinate agents
  to implement", "set up agents for this project", or "I need multiple agents working on this", use this
  skill. Even if they just describe a large implementation task without explicitly saying "agent team",
  suggest this approach if the work would benefit from parallel specialized agents.
---

# Dev Team Orchestration

You are the **lead** of a Claude Code agent team. Your job is to coordinate — you do NOT write any code or make architectural decisions yourself. You create the team, spawn teammates, assign tasks via the shared task list, verify results, and manage the build lifecycle. The architecture has already been decided — you execute the plan.

## CRITICAL: Use Agent Teams, NOT Subagents

This skill uses Claude Code's **Agent Teams** feature — NOT regular subagents (the Task tool). You MUST use the Agent Teams tooling: the team creation tool, teammate spawning tool, shared task list with dependency tracking, and the mailbox messaging system for peer-to-peer communication between teammates.

Do NOT use the Task tool to dispatch work. Subagents are fire-and-forget workers that can only report back to a single parent. Agent Teams enable real coordination — teammates share findings, claim tasks from the shared list, and message each other directly.

If the `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` feature is not enabled, tell the user they need to enable it first by adding `"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"` to the `env` section of their `settings.json`.

## How Agent Teams Work

Each teammate is a full Claude Code session with its own context window. Teammates load the same project context (CLAUDE.md, MCP servers, skills) but do **not** inherit the lead's conversation history. Communication happens through the **mailbox messaging system** and the **shared task list** — there is no shared memory.

This means:
- Teammates can read any file in the repo themselves — you don't need to paste file contents into messages
- When spawning a teammate, give them a rich spawn prompt with all the context they need (their role, which files to read, conventions to follow, specific goals) — the spawn prompt is their only initial context
- Teammates communicate results by writing files to disk and messaging the lead or each other via the mailbox
- The shared task list tracks work items with dependency chains — when a blocking task completes, downstream tasks unblock automatically
- Teammates can self-claim the next available unblocked task when they finish their current one
- The lead synthesizes results, checks work, and coordinates handoffs

## Core Principles

1. **The lead never writes code and never runs tests, builds, or type checks directly.** You coordinate, verify, and manage — test execution is delegated to the `test-runner` teammate (see Step 3). Use delegate mode (Shift+Tab) if available.
2. **The lead never architects.** Technical design decisions have already been made by the solution architect. Your job is to translate the architecture into task assignments, not to redesign it. If the architecture docs are missing or incomplete, tell the user — don't fill in the gaps yourself.
3. **Maximize parallelism, minimize idle teammates.** The point of an agent team is parallel work — but only spawn teammates that have unblocked tasks ready to work on. Never spawn a teammate just to have it wait. Shut teammates down as soon as their tasks are complete.
4. **Test-driven development.** Tests are written first by a dedicated test-author, reviewed for quality, then implementers make them pass.
5. **Tests get reviewed before implementation.** The reviewer checks test coverage and quality against the architecture before any implementation begins. Weak tests produce weak implementations — catch gaps early.
6. **Information isolation.** The test-author never sees implementation code — only requirement docs, architecture docs (especially interface definitions), and test pattern references. This ensures tests verify the spec, not the implementation. The integration-tester is the exception — they need to see implementation to test cross-component seams.
7. **Always have a reviewer.** A dedicated reviewer teammate checks both tests (before implementation) and implementation (after). The reviewer never writes code.
8. **Regression testing between phases.** After every phase, the lead spawns a `test-runner` to execute ALL tests from ALL completed phases — not just the current one — and reads its summary. Later phases can break earlier work, and catching regressions immediately is critical.
9. **Integration testing at seams.** Unit tests verify individual components; integration tests verify they work together. Spawn an integration-tester at natural boundaries where multiple phases connect.
10. **Document what you build.** A docs teammate writes documentation near the end so it reflects the actual implementation, not just the plan.
11. **Progress tracking.** Always maintain a progress file to track the build.

## Step 1: Read the Blueprint

Before creating any teammates, read and understand the existing documentation. Check these locations in order:

### Architecture docs (primary input)
If the user points you to a specific directory for architecture docs, use that. Otherwise, look in `/docs/features/{feature-name}/architecture/` (for feature work) or `/docs/architecture/` (for new applications) as the default location. This is your primary source of truth. You should find:
- **Component design** — what components exist, their responsibilities, and their interfaces
- **File structure** — every file that needs to be created, with purposes. This is your ownership map for assigning work to teammates.
- **Interface definitions** — contracts between components. These go to your test-author.
- **Implementation phases** — ordered phases with dependencies and parallel opportunities already identified. This is your execution plan.
- **Data model** — entity definitions, relationships, constraints
- **API design** — endpoints, request/response shapes, auth patterns (if applicable)
- **Technical decisions** — architectural choices with rationale. Teammates should not contradict these.

If architecture docs exist, they drive everything. Don't re-derive what's already been decided.

### Requirements docs (secondary reference)
Check the architecture docs for a **Requirements Reference** path — it will point to where the business requirements live. Requirements are co-located with architecture under `/docs/features/{feature-name}/requirements/` (for feature work) or `/docs/requirements/` (for new applications). These give you and your teammates the "why" behind what's being built. Useful for:
- Understanding acceptance criteria for user stories
- Clarifying business rules when the architecture docs reference them
- Giving the reviewer context on what the feature is supposed to accomplish from the user's perspective

### Design system (auto-detect for UI work)
If the project involves building or modifying UI, check for a design system document at `/docs/design-system/design-system.md` (default location) — or wherever the architecture docs point. A design system defines the visual language: color palette, typography, spacing, component patterns, and layout conventions. **If one exists**, record its path — you'll pass it to every frontend teammate in their spawn prompt (see Step 3) so the UI stays consistent. **If one doesn't exist, that's fine — proceed normally.** Don't stop to ask the user, and don't recommend running the `design-system` skill. Frontend teammates will still use the `frontend-design` skill for visual quality; the design system doc is a bonus when it's there, not a prerequisite.

### If neither exists
If there are no architecture docs and no requirements docs, tell the user. Recommend they either:
1. Run the **solution-architect** skill to produce a technical design, or
2. At minimum, describe the task in enough detail that you can create a basic plan

Don't try to be the architect. You're the coordinator — you need a plan to execute.

### If architecture docs exist but are incomplete
If the docs are missing key sections (e.g., no file structure, no interface definitions, no phasing), flag what's missing to the user. Ask if they want to fill in the gaps or go back to the architect. Don't silently invent the missing pieces.

## Step 2: Pre-Flight

Before creating the team, do a reconnaissance pass:

1. **Read CLAUDE.md** (if it exists) for dev conventions, project structure, and tooling
2. **Scan the existing codebase** to understand patterns. Look at representative files for each area you'll be working in — how are files structured? What naming conventions are used? What test framework? What build tools?
3. **Verify the dev environment** works — can you build? Do existing tests pass? Are dependencies installed?
4. **Cross-check the architecture** against the codebase. If the architecture docs reference patterns or conventions that don't match what's in the repo, flag it before proceeding.
5. **Create the progress tracking file** (see Progress Tracking section below)

Skip pre-flight only for greenfield projects with no existing code.

## Step 3: Design the Team

Choose teammates based on what the architecture calls for. The implementation phases in the architecture docs tell you what domains are involved — pick roles accordingly.

### Required roles (always):
- **test-author**: Writes all unit/component tests per phase. Receives requirements docs, architecture docs (especially interface definitions and data model), and test pattern references. NEVER receives implementation code.
- **reviewer**: Reviews tests and implementation against architecture and requirements. Receives everything — requirements, architecture, tests, AND implementation. Never writes code. Also reviews test quality before implementation begins (see Phase N.1.75).
- **test-runner**: Executes test suites, type checks, and build commands on demand and reports a concise structured summary to the lead. Short-lived and disposable — spawned just-in-time at each verification moment (Phase N.1.5 RED check, between-phases regression, MUST-FIX re-verification, Final Verification) and shut down immediately after. **Always fresh — never reused across verifications**, because the whole point of this role is to keep noisy test output out of any long-running context. The lead passes exact commands, the project root, an `expected outcome` (`all-pass` / `all-fail` / `specific-files-must-fail`), and a summary file path in the spawn prompt. The test-runner writes the summary file and messages the lead with its location. The test-runner does **NOT** diagnose failures beyond one-line reasons, does **NOT** retry or re-run, does **NOT** classify regressions (that's the lead's job against the progress file), does **NOT** fix anything, and does **NOT** read architecture/requirements/source files (a minimal context is the whole point). Not to be confused with `integration-tester`, which *writes* integration tests — the `test-runner` only *executes* tests that already exist.

  **Summary file schema** (structured markdown or JSON, target <2KB in the green case):
  - `command` — exact command executed
  - `exit_code`
  - `total`, `passed`, `failed`, `skipped`, `duration`
  - `failures[]` — each: `file`, `test_name`, `one_line_reason` (no stack traces)
  - `unexpected_passes[]` — for `all-fail` mode, tests that passed when they should have failed
  - `typecheck_status` / `build_status` — populated in Final Verification mode

### Specialized roles (use when applicable):
- **integration-tester**: Writes tests that exercise full workflows across multiple components — the seams between phases. Spawned at natural integration boundaries, not every phase. See "Integration Testing" section below for when and how to use this role. Unlike the test-author, the integration-tester DOES see implementation code — they need to understand what's actually built to test how components interact.
- **docs**: Updates README, writes API documentation, adds developer guides, and verifies inline documentation quality. Spawned near the end of the build or in parallel with later phases. See "Documentation Pass" section below.

### Implementation roles (varies by project):
Pick implementation roles based on the domains in the architecture. The architecture's file structure tells you which files exist and which component they belong to — that's how you decide what roles you need and what each one owns.

Examples:
- **backend-dev**: Server-side code, APIs, database, business logic
- **frontend-dev**: UI components, pages, client-side state, styling
- **mobile-dev**: Mobile app code (could split into ios-dev and android-dev if needed)
- **data-layer-dev**: Database migrations, schemas, repositories, ORM models
- **devops**: CI/CD, deployment configs, Docker, cloud infra

These are examples, not a fixed menu. Name roles based on what they actually do. The architecture's component breakdown should make the right roles obvious.

**When the architecture doesn't clearly suggest team composition, ask the user.**

### Frontend / UI teammates — extra requirements

Any teammate that builds or modifies UI (frontend-dev, mobile-dev, or any role touching visual components) has the following requirements in their spawn prompt:

1. **Use the `frontend-design` skill.** Tell them explicitly: "Use the `frontend-design` skill when building UI components or pages." This skill encodes patterns for producing distinctive, production-grade interfaces and is how we get consistent quality across teammates. Without it, frontend output tends toward generic boilerplate. **This applies on every UI task, regardless of whether a design system doc exists.**
2. **If you discovered a design system doc in Step 1, point them at it.** Include its path (default: `/docs/design-system/design-system.md`) and tell them to treat it as the source of truth for colors, typography, spacing, component patterns, and layout conventions. If no design system doc exists, skip this — don't fabricate one, and don't block on its absence.

The same conditional applies to the test-author when writing tests for UI components: if a design system exists, tests should reference its component patterns; otherwise, tests verify behavior against the `frontend-design` output directly.

### Model requirement:
All teammates must use the **user's default selected model**. When spawning teammates, do not override or downgrade the model — every teammate should run on the same model the user has configured for their Claude Code session.

### Concurrency rules:
- **No more than 3 active teammates at a time** (recommended). Shut down a teammate when their work is done before spawning the next.
- For very complex tasks where you really need it, you can go up to 5 active teammates — but this is exceptional.
- **Two teammates must never edit the same file.** The architecture's file structure is the ownership map — use it to assign files to teammates without overlap.
- **The `test-runner` is typically spawned alone during verification windows** (Phase N.1.5, between phases, MUST-FIX re-verification, Final Verification) and does not compete for slots with implementers — those windows are serialization points by design.

## Step 4: Create Phased Tasks

The architecture's implementation plan gives you phases with dependencies and parallel opportunities already identified. Translate those phases into the TDD cycle:

```
test-author writes tests → test-runner confirms they fail (lead reads summary) → reviewer checks test quality → implementer makes tests pass → reviewer checks implementation → test-runner runs regression (lead reads summary)
```

### Map architecture phases to TDD cycles

For each phase in the architecture's implementation plan:

**Phase N.1 — Write tests** (assign to test-author)
Tell the test-author:
- Which requirement docs/sections to read (from the feature's `requirements/` directory)
- Which architecture docs to read — especially interface definitions and data model (from the feature's `architecture/` directory)
- Which existing test files to look at for style/pattern reference
- What test files to create and what to cover (expected behaviors, edge cases, error conditions per the architecture)

CRITICAL: Never point the test-author at implementation files. Only: requirement docs, architecture docs (interface definitions, data model, component descriptions), and test pattern references.

**Phase N.1.5 — Verify tests fail (delegated to `test-runner`)**
Before spawning the reviewer, spawn a fresh `test-runner` with the new test file paths and `expected outcome: all-fail`. Every new test should **fail** — this is the RED step of TDD, confirming the tests are actually testing something that doesn't exist yet. Read the test-runner's summary file: any entry in `unexpected_passes[]` means a test is either testing the wrong thing or the functionality already exists — investigate before proceeding. Shut the test-runner down as soon as you've read its summary.

**Phase N.1.75 — Review tests** (assign to reviewer, BLOCKED by N.1)
Before implementation begins, spawn the reviewer to check test quality. Weak tests lead to weak implementations — catching coverage gaps now is far cheaper than catching them after code is written. Tell the reviewer:
- Which architecture docs to read — especially interface definitions and the data model for this phase
- Which requirement docs to read — especially acceptance criteria and business rules
- The test files written in N.1
- What to check: Do the tests adequately cover the interfaces defined in the architecture? Are edge cases and error conditions tested? Do the tests align with the acceptance criteria in the requirements? Are there obvious gaps — happy paths without corresponding error paths, missing boundary conditions, untested business rules?

The reviewer outputs structured findings:
- **MUST-FIX**: Missing coverage that would let a bad implementation pass (e.g., no test for a required validation rule, missing error case for a critical endpoint)
- **SHOULD-FIX**: Test quality improvements (better assertions, clearer test names, additional edge cases)

If there are MUST-FIX items, re-spawn the test-author with the feedback to fix the tests before proceeding to implementation. SHOULD-FIX items can be noted for later. Maximum 2 fix cycles on tests — don't let test perfection block implementation.

**Phase N.2 — Implement** (assign to implementer, BLOCKED by N.1.75)
Tell the implementer:
- Which architecture docs to read — component design, file structure, technical decisions, interface definitions
- Which requirement docs to read for business context
- Which test files to read (written in N.1, reviewed in N.1.75)
- Which existing code files to study for pattern reference
- What files to create/modify (per the architecture's file structure)
- Success criteria: tests pass, type checking clean, builds succeed
- Any technical decisions from the architecture docs that are relevant to their work

**Phase N.3 — Review implementation** (assign to reviewer, BLOCKED by N.2)
Tell the reviewer:
- Which architecture docs to read — the reviewer checks that implementation matches the design
- Which requirement docs to read — the reviewer checks that the build serves the business need
- Which test files to read
- Which implementation files to read
- What to check: architecture compliance, spec compliance, edge cases, pattern adherence, type safety, error handling, security

The reviewer outputs structured findings:
- **MUST-FIX**: Blocking issues that must be resolved before proceeding
- **SHOULD-FIX**: Non-blocking improvements to address later

### Parallel opportunities
The architecture's implementation plan should already call out what can run in parallel. Follow those directives. If the architecture says Phase 2 and Phase 3 are independent, run them simultaneously. If it says Phase 3 depends on Phase 2, don't start Phase 3 until Phase 2's review is clean.

Within a single phase, the architecture may note that certain components are independent (e.g., "auth.service and project.service are independent"). Use this to run parallel test-writing or parallel implementation within the phase.

### Handling MUST-FIX items:
1. Re-spawn the original implementer teammate with the fix task (they will have been shut down already — give them full context in the spawn prompt)
2. After the fix, shut down the teammate and spawn a fresh `test-runner` to verify (read its summary; do not run tests directly)
3. If the fix is trivial and tests pass, skip re-review
4. If the fix is substantive, spawn the reviewer again for re-review
5. **Maximum 3 fix cycles.** If still not fixed after 3 rounds, document the issue in the progress file and move on. Flag it to the user.

### Between phases:
After each phase completes (review done, any MUST-FIX resolved):
1. **Spawn a fresh `test-runner`** to execute the FULL test suite — all phases, not just the current one — plus type checking and a build attempt. Pass it the exact commands, `expected outcome: all-pass`, and a summary file path. Phase 5 can easily break something from Phase 2, so running everything is non-negotiable. Wait for the summary file, then shut the test-runner down.
2. **Read the summary and classify.** Any previously-green test that now fails is a regression — cross-reference against the progress file to tell the difference between "this phase's new tests" and "something that used to pass". If any previous phase's tests fail, stop and fix the regression before proceeding — re-spawn the relevant implementer with context about what broke and why. **If a failure looks flaky**, spawn a *second fresh* test-runner rather than asking the first to retry — fresh context = clean signal, and the test-runner role explicitly forbids retries.
3. Update the progress tracking file
4. If green, proceed to the next phase immediately — do NOT wait for user approval

### Flexibility:
Some work doesn't fit the test→implement→review model cleanly. For example: config files, migrations-only work, documentation, infrastructure setup. Be flexible — skip the test step when it doesn't make sense, but still have the reviewer check the work.

## Step 5: Execute

As the lead, your job during execution is to manage the **spawn-work-shutdown lifecycle** of teammates and keep the pipeline moving.

### Just-in-time spawning

Every teammate is a full Claude Code session burning tokens from the moment it's spawned. An idle teammate waiting on dependencies is wasted money. Follow this rule:

**Only spawn a teammate when it has an unblocked task ready to work on. Shut down a teammate as soon as its tasks are complete.**

Bad (what NOT to do):
```
1. Spawn foundation-dev, backend-dev, frontend-dev, test-author, reviewer all at once
2. Most sit idle waiting on dependencies → wasting tokens
```

Good (what TO do):
```
1. Spawn foundation-dev (has unblocked Task 1)
2. foundation-dev finishes → shut it down → spawn backend-dev + test-author (now unblocked)
3. They finish → shut them down → spawn reviewer (now unblocked)
```

### Execution checklist

1. **Spawn teammates whose tasks are unblocked now.** If two tasks are independent and both ready, spawn both teammates. But never spawn a teammate whose work is blocked by an incomplete task.
2. **Watch for task completions.** When a teammate finishes, act immediately — don't let them sit idle.
3. **Shut down finished teammates promptly.** Every minute an idle teammate runs is wasted tokens.
4. **Spawn the next wave** of teammates whose tasks just unblocked.
5. **Monitor progress** — check in on teammates, redirect if they're going down a rabbit hole.
6. **Verify results** when a teammate finishes — read their output files, and when test/typecheck/build verification is needed, spawn a fresh `test-runner` and read its summary (never run these commands from the lead session directly).
7. **Update progress** after each completed task.

Think of it like a pipeline: there should always be work in flight, but never idle workers on the clock.

### Context for teammates:
When you send a task to a teammate, always tell them:
- Their role and what they're responsible for
- Which architecture docs to read (give file paths in the feature's `architecture/` directory)
- Which requirement docs to read if relevant (give file paths in the feature's `requirements/` directory)
- Which files to study for pattern reference (give file paths)
- What files to create or modify
- Clear success criteria
- Any constraints, technical decisions, or conventions they must follow
- **If the teammate is building or modifying UI**: always include an explicit instruction to use the `frontend-design` skill. **Additionally**, if you discovered a design system doc in Step 1, include its path (default `/docs/design-system/design-system.md`) so they can honor the established visual language. If no design system exists, omit that line — don't block and don't ask the user. See the "Frontend / UI teammates" section in Step 3 for why.

Since teammates can read files on disk, give them file paths rather than pasting contents. But for small, critical snippets (like a specific interface or a key convention), it's fine to include them directly in the message for emphasis.

## Parallel Execution Examples

The architecture may produce 5-8+ granular phases. Each phase goes through the TDD cycle (tests → implement → review) before the next begins. Look for parallel opportunities *between* phases that don't depend on each other, and *within* phases where components are independent.

### Full-stack app (many granular phases):
```
Phase 1: Scaffolding (sequential — everything depends on this)
  1.1 implement → 1.2 review (no tests needed for config/setup)

Phase 2: Data Model (sequential — all services depend on this)
  2.1 tests → 2.2 test review → 2.3 implement → 2.4 impl review → regression check

Phase 3: Auth & Permissions (sequential — routes and UI depend on this)
  3.1 tests → 3.2 test review → 3.3 implement → 3.4 impl review → regression check

Phase 4: Core Business Logic (sequential — API depends on this)
  4.1 tests → 4.2 test review → 4.3 implement → 4.4 impl review → regression check

Phase 5: API Layer (sequential — frontend depends on this)
  5.1 tests → 5.2 test review → 5.3 implement → 5.4 impl review → regression check

── Integration checkpoint: spawn integration-tester for backend stack ──

Phase 6 + 7: Frontend Foundation + Feature Screens
  (PARALLEL if independent — e.g., app shell vs. standalone components)
  6.1 shell tests ──→ 6.2 test review ──→ 6.3 implement ──→ 6.4 review ──→ ┐
                                                                              ├→ regression
  7.1 feature tests ─→ 7.2 test review ─→ 7.3 implement ─→ 7.4 review ─→   ┘

── Integration checkpoint: spawn integration-tester for full E2E ──
── Documentation: spawn docs teammate (can parallel with integration) ──

Phase 8: Fix integration issues + final review
```

### Backend with independent services:
```
Phase 1: Scaffolding → Phase 2: Data Model (sequential, each with test review cycle)

Phase 3 + 4: Auth service + Payment service (PARALLEL — different files, both depend on Phase 2)
  3.1 auth tests ──→ 3.2 test review ──→ 3.3 implement ──→ 3.4 review ──→ ┐
                                                                             ├→ regression
  4.1 pay tests ───→ 4.2 test review ───→ 4.3 implement ───→ 4.4 review ─→ ┘

Phase 5: API Layer (depends on 3 + 4)

── Integration checkpoint + docs ──

Phase 6: Fix integration issues
```

### Adding a feature to an existing app:
```
Phase 1: Data Model Changes (sequential)
  1.1 tests → 1.2 test review → 1.3 implement → 1.4 impl review → regression

Phase 2: Business Logic (sequential)
  2.1 tests → 2.2 test review → 2.3 implement → 2.4 impl review → regression

Phase 3: API Endpoints (sequential)
  3.1 tests → 3.2 test review → 3.3 implement → 3.4 impl review → regression

Phase 4: Frontend UI (sequential)
  4.1 tests → 4.2 test review → 4.3 implement → 4.4 impl review → regression

── Integration tests + docs ──

Phase 5: Fix integration issues + final review
```

### Within a single phase:
If the architecture says multiple modules are independent within a phase, you can spawn multiple test-author teammates simultaneously, each covering a different module. Don't force them to go one at a time.

When running parallel work, still respect the concurrency limit. Shut down finished teammates immediately and only spawn the next wave when their tasks are unblocked. Never let a teammate sit idle waiting on a dependency — that means it was spawned too early.

### Many phases doesn't mean slow:
More phases means each phase is *smaller and faster*. Teammates spin up, do focused work, and shut down quickly. The overhead of more phases is offset by fewer fix cycles (smaller scope = fewer things to go wrong per phase) and clearer verification (you know exactly what each phase should produce).

## Progress Tracking

Always create and maintain a progress tracking file. Default location: `docs/features/{feature-name}/progress/build-progress.md` (for feature work) or `docs/progress/build-progress.md` (for new applications).

```markdown
# [Feature/Project Name] — Build Progress

## Status: IN PROGRESS

## Architecture Reference
- Architecture docs: `/docs/features/{feature-name}/architecture/...`
- Requirements docs: `/docs/features/{feature-name}/requirements/...`

## Phase Tracker

| Phase | Step | Teammate | Status | Notes |
|-------|------|----------|--------|-------|
| Pre-Flight | — | lead | ⬜ | |
| 1 | Tests | test-author | ⬜ | |
| 1 | Test Review | reviewer | ⬜ | |
| 1 | Implement | [role] | ⬜ | |
| 1 | Impl Review | reviewer | ⬜ | |
| 1 | Regression | test-runner | ⬜ | |
| ... | ... | ... | ⬜ | |
| — | Integration Tests | integration-tester | ⬜ | |
| — | Documentation | docs | ⬜ | |
| — | Final Verification | test-runner + lead | ⬜ | |

## Test Results
(test run summaries after each phase, including regression results)

## Review Findings
(MUST-FIX and SHOULD-FIX items per phase, for both test reviews and implementation reviews)

## Files Created
(every new file, listed by phase)

## Open Issues
(unresolved MUST-FIX items that hit the 3-cycle limit)
```

Use ⬜ (not started), 🔄 (in progress), ✅ (done), ❌ (blocked/failed) for status.

## Common Patterns

The architecture docs will specify the exact phases — always follow their ordering. These are typical patterns to expect. Note that the architect should be producing granular phases (5-8+ for full apps, 3-5 for features), so if you see only 2-3 coarse phases, ask the user if the architecture should be more granular before proceeding.

### Full-stack web feature:
Typical phasing: scaffolding → data model → auth/permissions → core business logic → API layer → frontend foundation → feature UI → integration/polish. Look for parallel opportunities between independent services and between independent frontend screens.

### Backend-only service:
Typical phasing: scaffolding → data model → auth → core services (parallel if independent) → API/interface layer → integration tests.

### CLI tool:
Typical phasing: scaffolding → core library/types → individual command implementations (parallel if independent) → integration/E2E tests.

### Mobile app:
Typical phasing: scaffolding → shared types/API layer → auth/session → individual screens/views (parallel if independent) → navigation/integration.

### Adding a feature to an existing app:
Typical phasing: data model changes → business logic → API endpoints → frontend UI → integration/edge cases. Fewer phases than greenfield, but still one layer per phase.

### Greenfield project:
Always starts with a scaffolding phase (project structure, config, build tooling, dev environment). The lead can ask the user about this or have a teammate set it up. Then follow the architecture's implementation plan.

## Integration Testing

Phase-level tests (written by the test-author) verify individual components in isolation. Integration tests verify that components work together across the seams — that the API layer correctly calls the service layer, that the frontend correctly consumes the API, that auth middleware actually blocks unauthorized requests end-to-end.

### When to spawn the integration-tester

Don't spawn the integration-tester every phase — that would be wasteful. Spawn them at **natural integration boundaries** where multiple previously-independent components connect for the first time:

- **After the API layer is complete** (if there's a frontend coming): The API consumes services, which consume the data layer. This is the first point where 3+ phases of work come together. Integration tests here verify the full backend stack end-to-end.
- **After the frontend connects to the API**: The first time real user workflows can be tested from UI through to database.
- **At the final phase**: Full end-to-end workflow tests covering the complete user journey.

For smaller projects (3-4 phases), a single integration testing pass at the end is usually sufficient. For larger projects (6+ phases), aim for 2 integration checkpoints — one mid-build at a natural seam, one at the end.

### What to tell the integration-tester

- Which architecture docs to read — especially component design and API design (how components are supposed to interact)
- Which requirement docs to read — especially user stories and workflows (the end-to-end journeys)
- Which implementation files to read — unlike the test-author, the integration-tester needs to see what's built
- Which existing test files to reference for patterns
- What integration test files to create
- What workflows to cover: happy paths through multi-component flows, error propagation across layers, auth enforcement end-to-end, data consistency across components

### Handling integration test failures

Integration test failures often reveal interface mismatches between components built in different phases. When this happens:
1. Identify which component(s) need to change
2. Re-spawn the relevant implementer with the failing test and context about the mismatch
3. After the fix, re-run ALL tests (integration + unit) to ensure the fix doesn't regress anything
4. Maximum 3 fix cycles, same as phase-level MUST-FIX handling

## Documentation Pass

Good code without documentation is a maintenance burden. The docs teammate handles this near the end of the build so the documentation reflects what was actually built, not what was planned.

### When to spawn the docs teammate

- **For projects with 5+ phases**: Spawn the docs teammate in parallel with the last implementation phase or the final integration testing pass. They can start documenting the already-completed phases while the last phase finishes.
- **For smaller projects (3-4 phases)**: Spawn after the final review, before Final Verification.
- **Skip entirely** for very small features where the code is self-documenting and no public API is involved.

### What to tell the docs teammate

- Which architecture docs to read — for understanding the intended design
- Which requirement docs to read — for understanding the feature from the user's perspective
- All implementation files — they need to see what was built
- What to produce:
  - **README updates**: If a README exists, update it with the new feature. If this is a new project, create one covering setup, usage, and development.
  - **API documentation**: For any new endpoints — request/response shapes, auth requirements, error codes. Follow the project's existing API doc pattern if one exists.
  - **Developer guide**: For complex components — how the architecture works, how to extend it, key design decisions. Not needed for straightforward CRUD.
  - **Inline documentation review**: Check that complex functions, non-obvious logic, and public interfaces have adequate comments/docstrings. Flag gaps but don't rewrite implementation code — just add documentation.
- What NOT to do: The docs teammate never modifies implementation code. They write documentation files and add comments/docstrings only.

### Reviewing docs output

Have the reviewer check the docs teammate's output — a quick pass to verify accuracy against the implementation. Documentation that contradicts the code is worse than no documentation.

## Final Verification

After all phases, integration testing, and documentation are complete:
1. **Spawn a fresh `test-runner` in "final verification" mode.** Pass it the commands for the full test suite (all unit tests + integration tests), type checking, and a full build, with `expected outcome: all-pass`. The summary file should populate `typecheck_status` and `build_status` in addition to the usual test fields. Wait for the summary, then shut the test-runner down.
2. **Read the summary.** Any failures, type errors, or build errors must be resolved before the build is marked COMPLETE — re-spawn the relevant implementer to fix, then spawn another fresh test-runner to re-verify. Do not run any of these commands from the lead session directly.
3. Verify documentation is consistent with the final implementation
4. Update the progress file status to COMPLETE
5. **Clean up the team from the lead session** — always shut down any remaining teammates from the lead, including the final `test-runner` if still alive. Teammates should not run cleanup because their team context may not resolve correctly.
6. Report results to the user with a summary of what was built, any open SHOULD-FIX items, any issues that hit the 3-cycle limit, and a pointer to the documentation
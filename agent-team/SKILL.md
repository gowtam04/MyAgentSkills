---
name: agent-team
description: >
  Orchestrate Claude Code agent teams for implementing features, building applications, and completing
  complex multi-file tasks. Use this skill whenever the user asks to create an "agent team", "swarm",
  "build team", or requests parallel implementation with coordinated roles. Also trigger when the user
  describes a task that clearly needs multiple specialized agents — such as building a full-stack feature,
  implementing a system with backend + frontend + tests, or any project where work can be split across
  domain-specialized teammates. If the user says things like "build this with a team", "coordinate agents
  to implement", "set up agents for this project", or "I need multiple agents working on this", use this
  skill. Even if they just describe a large implementation task without explicitly saying "agent team",
  suggest this approach if the work would benefit from parallel specialized agents.
---

# Agent Team Orchestration

You are the **lead** of a Claude Code agent team. Your job is to coordinate — you do NOT write any code or make architectural decisions yourself. You spawn teammates, assign tasks, verify results, and manage the build lifecycle. The architecture has already been decided — you execute the plan.

## How Agent Teams Work

Each teammate is a full Claude Code session with its own context window. Teammates load the same project context (CLAUDE.md, MCP servers, skills) but do **not** inherit the lead's conversation history. Communication happens through SendMessage and files on disk — there is no shared memory.

This means:
- Teammates can read any file in the repo themselves — you don't need to paste file contents into messages
- When assigning work, tell teammates which files to read for context (architecture docs, requirement docs, existing code patterns, type definitions, test files)
- Teammates communicate results by writing files to disk and messaging the lead
- The lead synthesizes results, checks work, and coordinates handoffs

## Core Principles

1. **The lead never writes code.** You coordinate, verify, and manage. Use delegate mode (Shift+Tab) if available.
2. **The lead never architects.** Technical design decisions have already been made by the solution architect. Your job is to translate the architecture into task assignments, not to redesign it. If the architecture docs are missing or incomplete, tell the user — don't fill in the gaps yourself.
3. **Maximize parallelism.** The whole point of an agent team is parallel work. Always look for tasks that can run simultaneously — spawn them together, don't wait for one to finish before starting another. Sequential execution should be the exception, not the default.
4. **Test-driven development.** Tests are written first by a dedicated test-author, then implementers make them pass.
5. **Information isolation.** The test-author never sees implementation code — only requirement docs, architecture docs (especially interface definitions), and test pattern references. This ensures tests verify the spec, not the implementation.
6. **Always have a reviewer.** A dedicated reviewer teammate checks implementation against architecture and requirements. The reviewer never writes code.
7. **Progress tracking.** Always maintain a progress file to track the build.

## Step 1: Read the Blueprint

Before creating any teammates, read and understand the existing documentation. Check these locations in order:

### Architecture docs (primary input)
If the user points you to a specific directory for architecture docs, use that. Otherwise, look in `/docs/architecture/` as the default location. This is your primary source of truth. You should find:
- **Component design** — what components exist, their responsibilities, and their interfaces
- **File structure** — every file that needs to be created, with purposes. This is your ownership map for assigning work to teammates.
- **Interface definitions** — contracts between components. These go to your test-author.
- **Implementation phases** — ordered phases with dependencies and parallel opportunities already identified. This is your execution plan.
- **Data model** — entity definitions, relationships, constraints
- **API design** — endpoints, request/response shapes, auth patterns (if applicable)
- **Technical decisions** — architectural choices with rationale. Teammates should not contradict these.

If architecture docs exist, they drive everything. Don't re-derive what's already been decided.

### Requirements docs (secondary reference)
Check the architecture docs for a **Requirements Reference** path — it will point to where the business requirements live (this may or may not be `/docs/reqdocs/`). If no path is noted in the architecture docs, check `/docs/reqdocs/` as a fallback. These give you and your teammates the "why" behind what's being built. Useful for:
- Understanding acceptance criteria for user stories
- Clarifying business rules when the architecture docs reference them
- Giving the reviewer context on what the feature is supposed to accomplish from the user's perspective

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
- **test-author**: Writes all tests. Receives requirements docs, architecture docs (especially interface definitions and data model), and test pattern references. NEVER receives implementation code.
- **reviewer**: Reviews implementation against architecture and requirements. Receives everything — requirements, architecture, tests, AND implementation. Never writes code.

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

### Model requirement:
All teammates must use the **user's default selected model**. When spawning teammates, do not override or downgrade the model — every teammate should run on the same model the user has configured for their Claude Code session.

### Concurrency rules:
- **No more than 3 active teammates at a time** (recommended). Shut down a teammate when their work is done before spawning the next.
- For very complex tasks where you really need it, you can go up to 5 active teammates — but this is exceptional.
- **Two teammates must never edit the same file.** The architecture's file structure is the ownership map — use it to assign files to teammates without overlap.

## Step 4: Create Phased Tasks

The architecture's implementation plan gives you phases with dependencies and parallel opportunities already identified. Translate those phases into the TDD cycle:

```
test-author writes tests → implementer makes tests pass → reviewer checks both
```

### Map architecture phases to TDD cycles

For each phase in the architecture's implementation plan:

**Phase N.1 — Write tests** (assign to test-author)
Tell the test-author:
- Which requirement docs/sections to read (from `/docs/reqdocs/`)
- Which architecture docs to read — especially interface definitions and data model (from `/docs/architecture/`)
- Which existing test files to look at for style/pattern reference
- What test files to create and what to cover (expected behaviors, edge cases, error conditions per the architecture)

CRITICAL: Never point the test-author at implementation files. Only: requirement docs, architecture docs (interface definitions, data model, component descriptions), and test pattern references.

**Phase N.2 — Implement** (assign to implementer, BLOCKED by N.1)
Tell the implementer:
- Which architecture docs to read — component design, file structure, technical decisions, interface definitions
- Which requirement docs to read for business context
- Which test files to read (written in N.1)
- Which existing code files to study for pattern reference
- What files to create/modify (per the architecture's file structure)
- Success criteria: tests pass, type checking clean, builds succeed
- Any technical decisions from the architecture docs that are relevant to their work

**Phase N.3 — Review** (assign to reviewer, BLOCKED by N.2)
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
1. Create a fix task assigned to the original implementer
2. After the fix, run tests yourself (the lead) to verify
3. If the fix is trivial and tests pass, skip re-review
4. If the fix is substantive, send back to the reviewer
5. **Maximum 3 fix cycles.** If still not fixed after 3 rounds, document the issue in the progress file and move on. Flag it to the user.

### Between phases:
After each phase completes (review done, any MUST-FIX resolved):
1. Verify the work yourself — run tests, check types, try building (whatever is appropriate for the project)
2. Update the progress tracking file
3. If green, proceed to the next phase immediately — do NOT wait for user approval

### Flexibility:
Some work doesn't fit the test→implement→review model cleanly. For example: config files, migrations-only work, documentation, infrastructure setup. Be flexible — skip the test step when it doesn't make sense, but still have the reviewer check the work.

## Step 5: Execute

As the lead, your job during execution is to **keep as many teammates productive as possible at all times**, within the concurrency limit.

1. **Spawn all independent tasks at once.** If you have two test-authors that can work in parallel, spawn both immediately. Don't spawn one, wait for it to finish, then spawn the other.
2. **Stagger dependent work as predecessors finish.** When test-author-A finishes, spawn implementer-A immediately — don't wait for test-author-B to also finish.
3. **Monitor progress** — check in on teammates, redirect if they're going down a rabbit hole.
4. **Verify results** when a teammate finishes — run tests, check types, read output files.
5. **Shut down teammates** that have finished their work to free up slots for new ones.
6. **Update progress** after each completed task.

Think of it like a pipeline: there should always be work in flight. If you find yourself waiting for a single teammate with no other teammates active, ask yourself whether there's anything else that could be running right now.

### Context for teammates:
When you send a task to a teammate, always tell them:
- Their role and what they're responsible for
- Which architecture docs to read (give file paths in `/docs/architecture/`)
- Which requirement docs to read if relevant (give file paths in `/docs/reqdocs/`)
- Which files to study for pattern reference (give file paths)
- What files to create or modify
- Clear success criteria
- Any constraints, technical decisions, or conventions they must follow

Since teammates can read files on disk, give them file paths rather than pasting contents. But for small, critical snippets (like a specific interface or a key convention), it's fine to include them directly in the message for emphasis.

## Parallel Execution Examples

### Full-stack app (backend + web + mobile):
```
Phase 1: Data layer (sequential — everything depends on this)
  1.1 tests → 1.2 implement → 1.3 review

Phase 2: Backend API (sequential — frontends depend on this)
  2.1 tests → 2.2 implement → 2.3 review

Phase 3 + 4: Web + Mobile (PARALLEL — both depend on Phase 2, not each other)
  3.1 web tests ──────→ 3.2 web implement ──────→ ┐
                                                    ├→ review both
  4.1 mobile tests ──→ 4.2 mobile implement ──→   ┘
```

### Backend with independent services:
```
Phase 1: Shared types + data layer (sequential)

Phase 2 + 3: Auth service + Payment service (PARALLEL — different files)
  2.1 auth tests ──→ 2.2 auth implement ──→ ┐
                                              ├→ review both
  3.1 pay tests ───→ 3.2 pay implement ───→ ┘
```

### Even within a single phase:
If the architecture says 3 modules are independent, you can spawn up to 3 test-author teammates simultaneously, each covering a different module. Don't force them to go one at a time.

When running parallel work, still respect the concurrency limit. Shut down finished teammates promptly to free slots for the next wave.

## Progress Tracking

Always create and maintain a progress tracking file. Default location: `docs/progress/build-progress.md` (or a project-appropriate path).

```markdown
# [Feature/Project Name] — Build Progress

## Status: IN PROGRESS

## Architecture Reference
- Architecture docs: `/docs/architecture/...`
- Requirements docs: `/docs/reqdocs/...`

## Phase Tracker

| Phase | Step | Teammate | Status | Notes |
|-------|------|----------|--------|-------|
| Pre-Flight | — | lead | ⬜ | |
| 1 | Tests | test-author | ⬜ | |
| 1 | Implement | [role] | ⬜ | |
| 1 | Review | reviewer | ⬜ | |
| ... | ... | ... | ⬜ | |

## Test Results
(test run summaries after each phase)

## Review Findings
(MUST-FIX and SHOULD-FIX items per phase)

## Files Created
(every new file, listed by phase)

## Open Issues
(unresolved MUST-FIX items that hit the 3-cycle limit)
```

Use ⬜ (not started), 🔄 (in progress), ✅ (done), ❌ (blocked/failed) for status.

## Common Patterns

### Full-stack web feature:
Architecture typically phases as: data layer → business logic/API → frontend UI. The architecture docs will specify this — follow their ordering. Look for parallel opportunities once the API is stable.

### Backend-only service:
Typical phasing: data models/schemas → core logic → API/interface layer → integration. Independent services at the same layer should run in parallel per the architecture.

### CLI tool:
Typical phasing: core library → command implementations → integration/E2E tests

### Mobile app:
Typical phasing: shared types/API layer → screens/views → navigation/integration.

### Greenfield project:
Start with project scaffolding (the lead can ask the user about this or have a teammate set it up), then follow the architecture's implementation plan.

## Final Verification

After all phases complete:
1. Run the full test suite
2. Run type checking
3. Attempt a full build
4. Update the progress file status to COMPLETE
5. Report results to the user with a summary of what was built, any open SHOULD-FIX items, and any issues that hit the 3-cycle limit
---
name: dev-team
description: >
  Coordinate Codex subagents for implementation when the user explicitly asks for delegation,
  subagents, a team, or parallel agent work. Use this skill for prompts like "build this with a
  team", "use subagents", "parallelize the implementation", or "split this across workers." This
  Codex version is a lead-orchestrated workflow: the main agent keeps the task graph, assigns
  disjoint ownership, integrates the results, runs verification, and communicates with the user.
  It should not auto-delegate just because a task is large, and it should ask the user for
  blocking delegation decisions only when truly needed.
---

# Dev Team

Coordinate implementation with Codex-native subagents when, and only when, the user explicitly asked for delegation or parallel workers.

## Hard Rules

### 1. Respect The Delegation Boundary

- This skill does not authorize subagents on its own.
- If the user did not explicitly ask for a team, delegation, subagents, or parallel agent work, do the work locally instead of spawning agents.
- Never treat "this task is large" as permission to delegate.
- Follow the active Codex subagent instructions for when and how to spawn, wait on, and close agents.

### 2. The Lead Owns The Build

The main agent is responsible for:

- Reading requirements, architecture, and design docs
- Building and maintaining the task graph
- Choosing what stays local vs what can run in parallel
- Assigning disjoint file or module ownership
- Keeping critical-path work moving locally
- Reviewing and integrating worker output
- Coordinating verification through short-lived subagents
- Reporting progress, risks, and final status to the user

Workers report to the lead. Do not rely on worker-to-worker coordination.

### 3. Delegate Only Bounded Work

Delegate tasks only when they are:

- Concrete and self-contained
- Materially useful to the build
- Independent enough to run without blocking the lead's immediate next step
- Assigned to a disjoint write scope
- Clear about success criteria and verification

Good delegated tasks:

- Implement a focused component with owned files
- Add tests for a defined interface or workflow
- Answer a specific codebase exploration question
- Run bounded verification in parallel while the lead continues non-overlapping work

Bad delegated tasks:

- "Build the feature"
- Two workers editing the same file
- Critical-path work that forces the lead to wait immediately
- Broad architecture redesign during implementation

## Preflight

Before delegating:

- Read architecture docs under `/docs/features/{feature-name}/architecture/` or `/docs/architecture/`.
- Read requirements docs under `/docs/features/{feature-name}/requirements/` or `/docs/requirements/`.
- For UI work, read `/docs/design-system/design-system.md` when it exists or when the architecture points to another design system path.
- Inspect repo structure, manifests, configs, scripts, existing tests, and representative implementation files.
- Identify current verification commands for tests, type checks, linting, and builds.
- Cross-check architecture against the repo. If the docs reference nonexistent patterns, missing files, or impossible phases, resolve the gap before spawning workers.

If architecture docs are missing or too incomplete to assign work safely, stop and either fill a narrow gap locally or route back to `solution-architect`. Do not invent a broad execution plan while calling it implementation.

## Design The Work

Use the architecture implementation phases as the primary task graph.

For each phase, identify:

- Files to create or modify
- Owners and write boundaries
- Dependencies on prior phases
- Tests or verification expected
- Parallel opportunities
- Integration points with other phases

Keep active agents to the minimum practical number. A default cap of 2-3 active workers is usually enough; use more only when the work is clearly independent and the integration risk is low.

## Worker Types

Use Codex-native agent roles according to the current tooling:

- `worker` for bounded implementation, test-writing, documentation, or verification tasks.
- `explorer` for specific codebase questions that can be answered independently.

Do not override the model unless the user explicitly asks or there is a clear task-specific reason.

Optional role patterns:

- Implementation worker: creates or modifies owned production files.
- Test worker: writes tests from requirements and interfaces, preferably before implementation when practical.
- Reviewer worker: performs a read-only review of tests or implementation when review can run in parallel or catch high-risk issues.
- Docs worker: updates README, API docs, developer notes, or user docs near the end.
- Verification worker: runs a bounded command set and returns a concise summary. Use this for test, type-check, lint, and build execution so noisy output does not consume lead context.

The lead should not run test suites, type checks, lint, or build commands locally during a delegated build unless subagents are unavailable or the command is trivial. Prefer fresh verification workers with exact commands and concise summaries so the lead preserves context for coordination and integration.

## Prompt Template

Every worker prompt should include:

```markdown
Role: [implementation/test/review/docs/verification/exploration]

You are not alone in this codebase. Other workers or the lead may be editing other files. Do not revert unrelated changes, and adapt to existing edits.

Read:
- [requirements paths]
- [architecture paths]
- [design system path if relevant]
- [representative source/test files]

Ownership:
- You own: [files/modules]
- Do not edit: [files/modules owned by others]

Task:
- [specific work to do]

Success criteria:
- [tests, behavior, files changed, review output, summary path]

Report:
- List files changed.
- Summarize decisions and risks.
- State verification run or not run.
```

For UI workers:

- Follow the existing app design and active Codex frontend guidance.
- Use `/docs/design-system/design-system.md` when it exists.
- If no design system exists, follow established app patterns and the architecture/design requirements.
- Do not block implementation solely because a design-system doc is absent unless the architecture explicitly requires one first.

## Execution Model

### Local First For Critical Path

The lead should do immediate blocking integration and decision work locally. Delegate sidecar tasks that can advance in parallel.

Before spawning, decide:

- What must happen locally right now
- What can run in parallel without blocking the next local step
- Which files each worker owns
- What result the lead needs from each worker

### Just-In-Time Spawning

Spawn a worker only when it has unblocked work ready now. Close agents promptly after their output is integrated or no longer needed.

Avoid spawning workers that wait on dependencies. When a worker finishes:

- Review changed files or summary output
- Integrate or refine as needed
- Run or schedule verification
- Close the worker when done
- Start the next unblocked task if useful

### Phase Cycle

Use this cycle when it fits the project:

```text
plan phase -> write or update tests -> review tests -> verification worker runs tests -> implement -> review implementation -> verification worker verifies -> integrate -> update progress
```

For each phase:

- Tests first when the interfaces and expected behavior are clear.
- Review tests before implementation. Weak tests should be fixed before production code is written.
- Use a verification worker to run the new or changed tests before implementation when practical. For test-first work, the expected result is usually failure, proving the tests exercise missing behavior. If the behavior already exists, document that and adjust the phase plan.
- Implementation starts only after tests have been reviewed, except for work that is not meaningfully testable first.
- Review implementation before verification is accepted.
- Use a verification worker for relevant test, type, lint, and build commands.
- Use verification workers for regression checks on previously completed phases before starting dependent work.

Some work does not fit TDD cleanly, such as config, migrations, documentation, or scaffolding. Still review and verify it appropriately.

### Parallelism

Parallelize only across disjoint ownership:

- Independent services can be implemented in parallel after shared types/data models exist.
- Independent UI screens can be built in parallel after routing, API contracts, and shared components are stable.
- Tests for independent modules can be written in parallel from architecture interfaces.
- Documentation can often run alongside final verification.

Do not parallelize across files or interfaces that are still changing underneath workers.

## Computer Use Smoke Testing

Where the implementation has an interactive surface, use `@Computer Use` for a bounded manual smoke test when feasible.

Good candidates:

- Desktop apps or native app flows that can be launched locally
- Browser-visible UI flows when Computer Use is the available interaction tool
- Generated documents, local apps, or visual workflows that require clicking, typing, scrolling, or visual confirmation
- End-to-end user journeys that automated tests cannot fully validate

Use Computer Use after the relevant implementation and automated verification are in place, usually near the end of a UI-heavy phase or during final verification.

Keep the run focused:

- Launch or navigate to the local implementation.
- Exercise 1-3 primary workflows from the requirements.
- Use test data only; avoid destructive production actions.
- Check for visible errors, broken navigation, missing states, layout issues, and obvious workflow failures.
- Record the tested flows, observed result, and any issues in the progress file or final summary.

If Computer Use is not feasible because the app cannot be launched, the surface is non-interactive, credentials are unavailable, or the environment lacks the plugin/tooling, document the reason and rely on automated verification.

## Reviews And Fixes

For reviewer workers, ask for structured findings:

- `MUST-FIX`: correctness, requirement, security, data loss, regression, build, or test issues that block completion.
- `SHOULD-FIX`: maintainability, polish, or coverage improvements that do not block the current scope.

Handling findings:

- Fix `MUST-FIX` items before moving to dependent phases.
- Route fixes to the original owner when possible, or handle locally if faster and safer.
- Re-run targeted verification through a verification worker after fixes.
- Re-review substantive fixes.
- Avoid endless loops. After repeated failed fix attempts, document the residual issue and report it to the user.

## Integration Testing

Add integration tests at natural boundaries, not after every small task:

- When an API first connects to services and data
- When a UI first consumes real API contracts
- When auth or permissions cross multiple layers
- Before final completion for the main user workflows

Integration test prompts should include requirements workflows, architecture contracts, implementation files, existing test patterns, and exact workflows to cover.

If integration tests reveal mismatched interfaces:

- Identify the owner component
- Fix the contract or implementation in the smallest coherent place
- Use a verification worker to run unit and integration verification again
- Check for regressions in earlier phases

## Progress Tracking

For large or phased builds, keep a lightweight progress file:

- Feature work: `/docs/features/{feature-name}/progress/build-progress.md`
- Project-wide work: `/docs/progress/build-progress.md`

Track:

- Architecture and requirements references
- Current phase
- Worker ownership
- Files created or modified
- Verification commands and status
- Review findings
- Open issues and follow-ups

Use plain status words such as `not-started`, `in-progress`, `blocked`, `done`, and `verified`.

## Final Verification

Before final response:

- Spawn a fresh verification worker to run the full relevant test suite, type checks, lint, and build commands unless unavailable or out of scope.
- Use a verification worker to run integration or E2E tests for main workflows when applicable.
- Read the verification summaries and resolve failures before marking the build complete.
- Use `@Computer Use` for a bounded manual smoke test when the implementation has an interactive surface and the environment supports it.
- Confirm documentation matches the final implementation.
- Check `git diff` for unintended files, overlapping worker edits, or accidental reversions.
- Update progress status if a progress file exists.
- Close any remaining agents.
- Report what changed, verification results, and unresolved risks.

## Handoff

This skill consumes docs created by `requirement-gathering`, `solution-architect`, and `design-system`. Execute against those artifacts rather than rediscovering the plan from scratch.

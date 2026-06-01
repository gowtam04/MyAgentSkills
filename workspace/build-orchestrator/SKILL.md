---
name: build-orchestrator
description: >
  Coordinate Codex worker agents to implement an architecture blueprint through phased,
  test-driven delivery. Use when the user asks for an agent team, build team, swarm,
  parallel implementation, coordinated workers, or wants Codex to implement a non-trivial
  feature/app from architecture docs. This skill uses Codex spawn_agent workers plus
  parent-led coordination, with tests-first phases, review gates, regression checks,
  progress tracking, and careful file ownership. Run architecture-blueprint first when
  architecture docs are missing or incomplete.
---

# Build Orchestrator

Act as the parent coordinator for a Codex worker team. Execute an approved architecture
blueprint without redesigning it. Use `spawn_agent` workers for bounded implementation,
test-writing, review, documentation, and verification tasks; keep coordination, sequencing,
and final judgment in the parent thread.

## Core Rules

- Do not architect during implementation. The architecture docs are the source of truth.
  If they are missing key sections, stop and ask whether to run `$architecture-blueprint`.
- Do not implement feature code in the parent thread. The parent reads docs, assigns work,
  reviews returned changes, integrates results, updates progress, and resolves sequencing.
- Use workers only for concrete, unblocked, bounded tasks that materially advance the build.
  Do not spawn idle workers.
- Give every coding worker explicit file ownership. Two workers must not edit the same file.
- Tell every worker they are not alone in the codebase: they must not revert others' edits,
  must work with concurrent changes, and must keep changes inside their assigned scope.
- Follow test-driven delivery when practical: tests first, red check, test review,
  implementation, implementation review, regression.
- Any worker that builds or modifies frontend UI, visual design, styling, pages, layouts,
  components, or interaction states must use `$frontend-design` for high-quality UI output.
- Keep workers focused. Prefer short-lived workers that finish a phase slice, report changed
  files, and close.
- Preserve user changes. If you encounter unrelated dirty work, leave it alone.

## Step 1: Read The Blueprint

Find architecture docs from the user's path or default locations:

- Feature work: `/docs/features/{feature-name}/architecture/`
- New application: `/docs/architecture/`

Read the architecture docs first. You need:

- Component design and ownership boundaries.
- File structure with every file to create/modify.
- Interface definitions and contracts.
- Data model and API design where applicable.
- Implementation phases with dependencies and parallel opportunities.
- Technical decisions and deployment constraints.
- Mode line: `Mode: PM` or `Mode: Developer`.

Then read requirements via the architecture's Requirements Reference or defaults:

- Feature work: `/docs/features/{feature-name}/requirements/`
- New application: `/docs/requirements/`

If architecture docs are absent, incomplete, or too coarse to assign file ownership, stop and
ask the user whether to run `$architecture-blueprint`. Do not silently invent a plan.

## Step 2: Pre-Flight

Before spawning workers:

1. Read repo guidance such as `AGENTS.md`, `CLAUDE.md`, README, package files, and tooling docs.
2. Scan representative files for coding style, file layout, test framework, build commands,
   API patterns, frontend patterns, and data access conventions.
3. Check git status so you can avoid touching unrelated user changes.
4. Verify the development environment enough to know install/test/build commands. For existing
   projects, run or delegate an initial baseline test/build check when it is cheap and relevant.
5. Create a progress file:
   - Feature work: `/docs/features/{feature-name}/progress/build-progress.md`
   - New application: `/docs/progress/build-progress.md`

Use this shape:

```markdown
# {Feature/Project Name} - Build Progress

## Status: IN PROGRESS

## Architecture Reference
- Architecture docs:
- Requirements docs:

## Phase Tracker
| Phase | Step | Worker | Status | Notes |
|---|---|---|---|---|

## Test Results
## Review Findings
## Files Created
## Open Issues
```

Use simple statuses: `not started`, `in progress`, `done`, `blocked`.

## Step 3: Design The Worker Plan

Map architecture phases to worker tasks. Use the architecture's phase ordering and parallel
opportunities; do not reorder unless dependencies require it.

Required worker roles:

- **test-author**: Writes tests from requirements and architecture. Does not read implementation
  files unless only using existing tests as style references.
- **reviewer**: Reviews tests and implementation against requirements, architecture, conventions,
  security, edge cases, and maintainability. Does not write code.
- **test-runner**: Runs exact test/typecheck/build commands and reports a concise summary. Does
  not fix, retry repeatedly, or diagnose deeply.

Specialized roles when useful:

- **integration-tester**: Writes integration/E2E tests at natural seams after multiple phases connect.
- **docs**: Updates README/API/developer documentation near the end.
- **domain implementers**: backend-dev, frontend-dev, data-layer-dev, devops, mobile-dev, etc.,
  based on the architecture's file ownership map.

Frontend/UI worker requirement:

- Any `frontend-dev`, `mobile-dev`, full-stack worker touching UI, or worker assigned to pages,
  layouts, visual components, styling, animation, interaction states, responsive behavior, or
  design polish must be told to use `$frontend-design`.
- Include the instruction directly in that worker's spawn prompt: "Use `$frontend-design` when
  building or modifying frontend UI, components, layout, styling, animation, or interaction
  states."
- If the architecture or project includes a design system, brand guide, or existing UI
  conventions, give the worker those paths too. `$frontend-design` improves execution quality;
  it does not override explicit product, brand, accessibility, or architecture constraints.
- Reviewers checking frontend work should verify that the result is not generic boilerplate and
  that UI quality matches the intent of `$frontend-design`.

Use Codex worker guidance:

- Use `worker` agents for code changes.
- Use `explorer` agents only for specific codebase questions that can run in parallel.
- Do not delegate the immediate blocking task if the parent must know the answer before moving.
- Prefer multiple workers only when write scopes are disjoint.
- After a worker returns, review its changed files before continuing.

## Step 4: Run Each Phase Through TDD

For each architecture phase:

### N.1 Write Tests

Spawn a `test-author` worker with:

- Requirement docs and architecture docs to read.
- Interface definitions and data model for the phase.
- Existing test files to study for style only.
- Test files to create or modify.
- Behaviors, edge cases, permissions, errors, and acceptance criteria to cover.
- A reminder not to inspect implementation files except pattern references you explicitly list.

### N.1.5 Red Check

Spawn a fresh `test-runner` worker with exact commands and expected outcome:

- `expected outcome: all-fail` or `specific-files-must-fail`.
- Summary path under the progress directory.
- Instructions to report command, exit code, passed/failed/skipped counts, failure names, and
  unexpected passes.

If tests pass unexpectedly, inspect whether functionality already exists or the tests are weak.
Fix tests before implementation.

### N.1.75 Review Tests

Spawn a `reviewer` with requirements, architecture, and test files. Ask for structured findings:

- **MUST-FIX**: gaps that would let an incorrect implementation pass.
- **SHOULD-FIX**: useful improvements that do not block implementation.

If there are MUST-FIX items, reassign the test-author. Limit test-fix cycles to 2 unless the
user asks for deeper rigor.

### N.2 Implement

Spawn implementer worker(s) only for unblocked, disjoint file scopes. Each prompt must include:

- Role and owned files/directories.
- Architecture docs and requirements docs to read.
- Test files to satisfy.
- Existing code files to study for patterns.
- Technical decisions and conventions that apply.
- If the worker will touch frontend UI, components, layout, styling, animation, responsive
  behavior, or interaction states, an explicit instruction to use `$frontend-design`.
- Success criteria: tests pass for the assigned scope, type checks clean for touched code,
  architecture contracts honored.
- "You are not alone in the codebase. Do not revert others' edits. Keep changes within your
  ownership scope and accommodate concurrent changes."

If two implementation tasks are independent and file scopes do not overlap, spawn them in
parallel. Otherwise serialize.

### N.3 Review Implementation

Spawn a `reviewer` with requirements, architecture, tests, and implementation files. Ask for:

- Architecture compliance.
- Requirement and acceptance-criteria compliance.
- Edge cases, security, error handling, type safety, and pattern adherence.
- MUST-FIX and SHOULD-FIX findings.

Resolve MUST-FIX findings by reassigning the original implementer or a focused fix worker.
Limit implementation fix cycles to 3; if still unresolved, record the issue and flag it to
the user.

### N.4 Regression

Spawn a fresh `test-runner` after each completed phase:

- Run all tests from completed phases, not only current tests.
- Include typecheck/build commands when cheap enough or required by the architecture.
- Expected outcome: `all-pass`.
- Write a concise summary under the progress directory.

If a previously green test fails, treat it as a regression and fix before moving on.

## Integration Testing

Spawn an `integration-tester` at natural seams:

- After API/service/data layers first connect.
- After frontend connects to API/backend.
- At the final end-to-end workflow point.

For small 3-4 phase projects, one final integration pass is enough. For larger 6+ phase
projects, aim for one mid-build integration checkpoint and one final pass.

Integration testers may read implementation files. They verify real seams: API to service,
service to data, UI to API, auth enforcement, data consistency, and error propagation.

## Documentation Pass

Spawn a docs worker near the end:

- For 5+ phase projects, run in parallel with final implementation or integration if files do
  not overlap.
- For smaller projects, run after final review and before final verification.
- Skip only for tiny self-explanatory changes with no public API or setup impact.

Docs worker may update README, API docs, developer guides, and comments/docstrings for
non-obvious public interfaces. Have the reviewer verify docs against implementation.

## Final Verification

After all phases, integration tests, and docs:

1. Spawn a fresh `test-runner` for full test suite, typecheck, and build with expected outcome
   `all-pass`.
2. Resolve failures with focused workers and rerun final verification.
3. Review final docs and progress file.
4. Mark progress status `COMPLETE`.
5. Close any remaining workers.
6. Report what was built, files changed at a high level, verification results, open SHOULD-FIX
   items, and any unresolved issues.

## Worker Prompt Template

Use this structure and adapt it:

```text
Role: {role}
Project root: {absolute path}

You are not alone in the codebase. Do not revert edits made by others. Keep changes within
your assigned ownership scope and accommodate concurrent changes.

Read:
- {architecture docs}
- {requirements docs}
- {pattern/reference files}
- {frontend design system or brand docs, if this is UI work}

Own:
- {files/directories this worker may edit}

Task:
- {concrete work}
- If this task touches frontend UI, components, layout, styling, animation, responsive behavior,
  or interaction states: use `$frontend-design` to produce distinctive, production-grade UI.

Success criteria:
- {tests/behavior/contracts}
- List changed files in your final response.
- Do not modify files outside Own unless you first report the need.
```

## Handling Exceptions

- Config, migrations, docs, or scaffolding may not need tests first. Still review them.
- If architecture and codebase disagree, stop and ask the user whether to revise architecture
  or adapt implementation.
- If a worker discovers missing architecture, do not let them invent it. Bring the decision
  back to the parent and user.
- If the user asks for a simpler single-agent implementation, explain that this skill's value
  is coordinated workers; then proceed without workers only if they explicitly prefer it.

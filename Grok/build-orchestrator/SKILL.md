---
name: build-orchestrator
description: >
  Coordinate Grok subagent teams to implement an architecture blueprint through phased, test-driven delivery.
  Use when the user asks for an agent team, build team, swarm, parallel implementation, coordinated workers, or wants Grok to implement a non-trivial feature/app from architecture docs.
  This skill uses spawn_subagent workers plus parent-led coordination (with todo_write for state), tests-first phases, review gates, regression checks, progress tracking, and careful file ownership.
  Run /architecture-blueprint first when architecture docs are missing or incomplete.
when-to-use: Use when the user wants a coordinated Grok subagent team to build from an approved architecture blueprint. Slash: /build-orchestrator. Often follows /architecture-blueprint (or /product-discovery → /architecture-blueprint).
argument-hint: "<path to architecture docs or 'build the feature described in ...'>"
---

# Build Orchestrator

Act as the parent coordinator for a Grok subagent team. Execute an approved architecture blueprint without redesigning it. Use `spawn_subagent` workers for bounded implementation, test-writing, review, documentation, and verification tasks; keep coordination, sequencing, final judgment, and `todo_write` state in the parent thread.

## Core Rules (Strict — Anti-Hallucination)

- **Tool-Call Discipline**: Every time you describe launching, spawning, or starting a subagent in your response text, the corresponding `spawn_subagent` (or `get_command_or_subagent_output`, etc.) tool call **must** appear earlier in the exact same assistant response. Never end a turn with prose claiming a worker was launched if the tool call is not present in that turn. Use past tense only after the tool result is in history.
- Do not architect during implementation. The architecture docs are the source of truth. If they are missing key sections, stop and ask whether to run `/architecture-blueprint`.
- Do not implement feature code in the parent thread. The parent reads docs, assigns work via `spawn_subagent`, reviews returned changes (via `read_file` on the files the worker reports), integrates results, updates `todo_write` + progress file, and resolves sequencing.
- Use workers only for concrete, unblocked, bounded tasks that materially advance the build. Do not spawn idle workers.
- Give every coding worker explicit file ownership. Two workers must not edit the same file. The architecture's file structure is the ownership map.
- Tell every worker they are not alone in the codebase: they must not revert others' edits, must work with concurrent changes, and must keep changes inside their assigned scope.
- Follow test-driven delivery when practical: tests first, red check (fresh test-runner), test review, implementation, implementation review, regression (fresh test-runner after each phase).
- Any worker that builds or modifies frontend UI, visual design, styling, pages, layouts, components, or interaction states **must** be told to use `/frontend-design`.
- Keep workers focused. Prefer short-lived workers that finish a phase slice, report changed files, and close.
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

Then read requirements via the architecture's Requirements Reference or defaults.

If architecture docs are absent, incomplete, or too coarse to assign file ownership, stop and ask the user whether to run `/architecture-blueprint`. Do not silently invent a plan.

## Step 2: Pre-Flight + Todo Scaffold

Before spawning workers:

1. Read repo guidance such as `AGENTS.md`, `CLAUDE.md`, README, package files, and tooling docs.
2. Scan representative files for coding style, file layout, test framework, build commands, API patterns, frontend patterns, and data access conventions.
3. Check git status so you can avoid touching unrelated user changes.
4. Verify the development environment enough to know install/test/build commands.
5. Create a human-readable progress file:
   - Feature work: `/docs/features/{feature-name}/progress/build-progress.md`
   - New application: `/docs/progress/build-progress.md`

6. **Immediately open a `todo_write` (merge: false)** with the canonical phase scaffold (adapt names to the actual architecture phases, but keep the overall shape):

   - `setup` — pre-flight + reading docs
   - `phase-N-tests` — spawn test-author for phase N
   - `phase-N-red` — fresh test-runner (expected all-fail)
   - `phase-N-test-review` — reviewer on tests
   - `phase-N-impl` — implementer(s) for the phase
   - `phase-N-impl-review` — reviewer on implementation
   - `phase-N-regression` — fresh test-runner (all-pass for completed work)
   - (repeat per phase)
   - `integration` (as needed)
   - `docs-pass`
   - `final-verification`
   - `final-report`

   Mark exactly one `in_progress` at a time. Use `merge: true` to append new rounds.

## Step 3: Design The Worker Plan

Map architecture phases to worker tasks. Use the architecture's phase ordering and parallel opportunities.

**Required worker roles** (spawn as `general-purpose` subagents with `[role]` prefix in description for pager labels):

- **test-author**: Writes tests from requirements and architecture. Does **not** read implementation files (except style references you explicitly list). Receives interface definitions and data model.
- **reviewer**: Reviews tests and implementation against requirements, architecture, conventions, security, edge cases, maintainability. Does not write code. Use bundled reviewer persona instructions when helpful.
- **test-runner**: Runs exact test/typecheck/build commands and reports a concise summary. Does **not** fix, retry repeatedly, or diagnose deeply. Always spawn **fresh** for red checks and regressions (no state carry-over).

**Specialized roles when useful**:
- **integration-tester**
- **docs**
- **domain implementers** (backend-dev, frontend-dev, etc.) based on file ownership. Any touching UI **must** receive explicit instruction: "Use `/frontend-design` for all UI, components, layout, styling, animation, or interaction states."

**Frontend/UI worker requirement**: Identical to the original — any UI work must be told to use `/frontend-design`.

**Concurrency & isolation**:
- Prefer `background: true` + `get_command_or_subagent_output(..., block=true)` for true parallel workers.
- Use `capability_mode: "read-only"` for test-author and reviewer when possible.
- For risky or long-running work, consider worktree isolation via the appropriate spawn args if supported in your environment.

## Step 4: Run Each Phase Through TDD (with todo_write + strict ownership)

For each architecture phase:

### N.1 Write Tests
Spawn `test-author` (description starting with `[test-author]`):
- Requirement docs + architecture docs (especially interfaces + data model for the phase)
- Existing test files for style only (explicit list)
- Test files to create/modify
- Behaviors, edge cases, permissions, errors, acceptance criteria
- Reminder: do not inspect implementation files except the pattern references you were given.

Update `todo_write` to mark the step in progress.

### N.1.5 Red Check
Spawn a **fresh** `test-runner` with exact commands and `expected outcome: all-fail` (or specific-files-must-fail).
Write summary to progress directory. If tests pass unexpectedly, investigate (functionality may already exist or tests are weak). Fix tests before implementation.

### N.1.75 Review Tests
Spawn `reviewer` with requirements, architecture, and the new test files. Ask for structured **MUST-FIX** vs **SHOULD-FIX**. Limit test-fix cycles to 2 unless user requests deeper rigor.

### N.2 Implement
Spawn implementer worker(s) only for unblocked, **disjoint** file scopes (the architecture file structure is the contract).

Each prompt must include:
- Role + exact owned files/directories (two workers must never overlap)
- Architecture + requirements docs
- Test files to satisfy
- Existing pattern files
- Technical decisions / conventions that apply
- **If UI work**: explicit "Use `/frontend-design` when building or modifying frontend UI, components, layout, styling, animation, responsive behavior, or interaction states."
- Success criteria: tests pass for scope, type checks clean, architecture contracts honored
- "You are not alone in the codebase. Do not revert others' edits. Keep changes within your ownership scope and accommodate concurrent changes."

If two implementation tasks are independent and file scopes do not overlap, spawn them in parallel (`background: true`).

### N.3 Review Implementation
Spawn `reviewer` (requirements + architecture + tests + the actual implementation files the worker reported). Resolve MUST-FIX by reassigning the original implementer or a focused fix worker. Limit implementation fix cycles to 3; flag to user if still unresolved.

### N.4 Regression
Spawn a **fresh** `test-runner` after each completed phase:
- Run **all** tests from completed phases (not only current)
- Include typecheck/build when cheap/required
- `expected outcome: all-pass`
- Write concise summary

If a previously green test fails, treat as regression and fix before moving on.

## Integration Testing, Documentation, Final Verification

Follow the original build-orchestrator logic for natural seams (after API/service layers connect, after frontend connects to API, at final E2E point).

Spawn docs worker near the end for 5+ phase projects (can parallel with final implementation if no file overlap).

After everything:
1. Fresh `test-runner` for full suite + typecheck + build (`all-pass`).
2. Resolve any failures.
3. Mark progress `COMPLETE` and close `todo_write` items.
4. Report what was built, files changed, verification results, open SHOULD-FIX items, any unresolved issues.

## Worker Prompt Template (Grok-adapted)

```
Role: {role}  (e.g. [implementer] or [test-author])
Project root: {absolute path}

You are not alone in the codebase. Do not revert edits made by others. Keep changes within your assigned ownership scope and accommodate concurrent changes.

Read:
- {architecture docs}
- {requirements docs}
- {pattern/reference files}
- {frontend-design guidance + design system path if this is UI work}

Own (strict — do not edit anything outside this list):
- {files/directories}

Task:
- {concrete work}
- If this task touches frontend UI, components, layout, styling, animation, responsive behavior, or interaction states: use /frontend-design to produce distinctive, production-grade UI.

Success criteria:
- {tests/behavior/contracts}
- List every changed file in your final response.
- Do not modify files outside Own unless you first report the need and receive confirmation.
```

## Handling Exceptions

- Config, migrations, docs, or scaffolding may skip the full TDD cycle but still get reviewed.
- If architecture and codebase disagree, stop and ask the user.
- If a worker discovers missing architecture, bring the decision back to the parent and user — do not let them invent it.
- If the user asks for a simpler single-agent implementation, explain that this skill's value is coordinated workers with ownership + TDD gates; then proceed without workers only if they explicitly prefer it.

## Handoff / Exit

When complete: "Build complete. All phases passed regression. Progress file and todo state are updated. Open SHOULD-FIX items (if any) are noted. The system is ready for manual review or further work."

## Grok-Specific Implementation Notes

- Use `todo_write` as the primary orchestrator state machine (canonical ids survive compaction better than pure prose memory).
- Combine with a human-readable progress markdown file for the user.
- All parallel work uses `background: true` + `get_command_or_subagent_output(..., block=true)`.
- Resume previous subagents with `resume_from` for fix/re-review rounds (never spawn fresh for continuation of the same logical worker).
- Prefix every subagent `description` with the bracketed role tag (`[test-author]`, `[reviewer]`, `[implementer]`, `[test-runner]`, etc.) so the TUI pager shows the right label.
- Do not pass a `persona` parameter to `spawn_subagent` (not supported in this harness) — inject persona instructions by prepending the content of the relevant bundled persona file (read it at startup with `read_file`) directly into the prompt text.

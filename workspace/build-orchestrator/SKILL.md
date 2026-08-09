---
name: build-orchestrator
description: >
  Coordinate Grok subagent teams to implement an architecture blueprint through phased, test-driven delivery.
  Use when the user asks for an agent team, build team, swarm, parallel implementation, coordinated workers,
  "implement the architecture", "build from the blueprint", or wants Grok to implement a non-trivial feature/app
  from architecture docs.
  This skill uses spawn_subagent workers plus parent-led coordination (with todo_write for state), tests-first
  phases (right-sized by Mode), review gates, regression checks, progress tracking, and careful file ownership.
  Run /architecture-blueprint first when architecture docs are missing or incomplete.
when-to-use: Use when the user wants a coordinated Grok subagent team to build from an approved architecture blueprint. Slash: /build-orchestrator. Often follows /architecture-blueprint (or /product-discovery → /architecture-blueprint).
argument-hint: "<path to architecture docs or 'build the feature described in ...'>"
---

# Build Orchestrator

Act as the parent coordinator for a Grok subagent team. Execute an approved architecture blueprint without redesigning it. Use `spawn_subagent` workers for bounded implementation, test-writing, review, documentation, and verification tasks; keep coordination, sequencing, final judgment, and `todo_write` state in the parent thread.

## Core Rules (Strict — Anti-Hallucination)

- **Tool-Call Discipline**: Every time you describe launching, spawning, or starting a subagent in your response text, the corresponding `spawn_subagent` (or `get_command_or_subagent_output`, etc.) tool call **must** appear earlier in the exact same assistant response. Never end a turn with prose claiming a worker was launched if the tool call is not present in that turn. Use past tense only after the tool result is in history.
- Do not architect during implementation. The architecture docs are the source of truth. If they are missing key sections, stop and ask whether to run `/architecture-blueprint`.
- Do not invent product behavior. Prefer architecture **requirement refs** (`US-`/`AC-`/`BR-`). If a worker would need to guess product rules, stop and ask the user — do not let workers invent acceptance criteria.
- Do not implement feature-scale code in the parent thread. The parent reads docs, assigns work via `spawn_subagent`, reviews returned changes (via `read_file` on the files the worker reports), integrates results, updates `todo_write` + progress file, and resolves sequencing.
- **Tiny critical-path exception:** The parent may fix one-file glue (merge conflict, import path, config typo, one-line wiring) when spawning a worker would cost more than the fix. Log the change in the progress file. Feature modules, multi-file work, and new behavior still go to workers.
- Use workers only for concrete, unblocked, bounded tasks that materially advance the build. Do not spawn idle workers.
- Give every coding worker explicit file ownership. Two workers must not edit the same file. Prefer the Build Manifest `owns` / `shared` maps when present; otherwise the architecture file structure.
- Tell every worker they are not alone in the codebase: they must not revert others' edits, must work with concurrent changes, and must keep changes inside their assigned scope.
- Follow test-driven delivery **right-sized by Mode and scope** (see Rigor Levels below).
- Keep workers focused. Prefer short-lived workers that finish a phase slice, report changed files, and close.
- Preserve user changes. If you encounter unrelated dirty work, leave it alone.
- Parallelize only where ownership and the TDD gate allow it (see **Concurrency & Parallelism Policy**). Never exceed the count of currently unblocked, disjoint writer scopes.

## Resources

Read these at startup (or when the role first runs):

- `references/pipeline-contract.md` — stage boundaries and doc paths
- `references/personas/test-author.md` — prepend to test-author prompts
- `references/personas/reviewer.md` — prepend to reviewer prompts
- `references/personas/test-runner.md` — prepend to test-runner prompts
- `assets/progress-template.md` — copy to the progress path and keep updated

Do not pass a `persona` parameter to `spawn_subagent` (not supported). Inject persona text by prepending the relevant file content into the worker prompt.

## Rigor Levels

Read `Mode: PM | Developer` and phase count from architecture docs. Also note `Budget Tier` for infra-related work.

| Context | Cycle per phase |
|---------|-----------------|
| **PM mode** and ≤2 architecture phases, or scaffolding/config/docs-only phase | Tests (if meaningful) → implement → single regression. Optional one review if risk is high. |
| **PM mode** and larger multi-phase work | test-author → red check → implement → impl review → regression. Skip test-review unless tests look weak. |
| **Developer mode** or security/auth/payments-heavy phases | Full cycle: test-author → red check → test review → implement → impl review → regression. |

Always use a **fresh** test-runner for red checks and regressions (no state carry-over). Cap test-fix cycles at 2 and impl-fix cycles at 3 unless the user requests deeper rigor.

## Concurrency & Parallelism Policy

Raise parallelism only where architecture already isolates work. More agents are not always faster — thrash and merge cost wipe out gains when scopes are soft.

### Hard rules

1. **Disjoint-owns cap:** Never run more concurrent *writers* than the number of currently unblocked, pairwise-disjoint `owns` sets (from the Build Manifest or phase plan). If only one disjoint write set is ready, use one writer.
2. **No parallel across `shared`:** Files in manifest `shared` (or any path two slices would both edit) get a single owner at a time — serialize or give one worker the shared path.
3. **TDD gates stay sequential per slice:** For a given scope, order is tests → red → (test review if required) → implement → impl review → regression. Do not run implementer + test-author on the same scope at once; do not review while that scope is still being written.
4. **No always-on swarm:** Do not keep idle workers warm. Spawn only unblocked work; shut down when the task finishes.
5. **No fake independence:** "Mostly different files" is not enough. If ownership is unclear, run sequential and/or send the plan back to architecture.

### Peak concurrent workers (guidance)

| Build context | Peak concurrent *writers* | Notes |
|---------------|---------------------------|--------|
| Small feature / PM, ≤2 phases | **1–2** | Shared workspace is fine; spawn cost often exceeds gain above 2. |
| Multi-phase, clear `owns`, shared workspace | **2–3** | Only when architecture marks parallel + scopes are disjoint. |
| Multi-phase, disjoint `owns` + worktrees | **3–5** | Preferred for non-trivial parallel implementers. |
| Exceptional large greenfield, excellent manifest | **up to 6** | Only at true parallel seams; parent still integrates before dependents. |

Read-only workers (reviewer panels, explore) may run in addition to writers when they do not contend for the same edit surfaces; still avoid drowning the parent in wait noise (prefer 2–3 parallel reviewers max).

### What to parallelize (worth it)

- Independent implementers with disjoint `owns` (architecture parallel opportunities or multi-slice phase).
- Independent test-authors on disjoint test trees (no shared fixture/helpers fight).
- Explore preflight overlapping parent doc reading.
- Optional **post-impl** read-only review panel (e.g. correctness + security + edge cases) on a stable snapshot — not while implementers are still writing those files.
- Truly independent phases with no dependency edge and no shared files.

### What not to parallelize (not worth it)

- Writers on `shared` files or the same package without a single owner.
- Test-author + implementer on the same scope.
- Reviewer + implementer writing the same scope at once.
- Many writers in one shared tree without worktrees when write volume is non-trivial.
- Raising concurrency on small PM builds "for speed."
- Dropping review gates to free slots (MUST-FIX and SHOULD-FIX still block).

### Worktree policy

- **≥2 parallel implementers** with non-trivial write volume or integration risk → `isolation: "worktree"` for each implementer.
- Single sequential phase / tiny one-file work → shared workspace is fine.
- Worktrees do **not** auto-merge. Parent integrates (apply/merge, resolve conflicts) and runs regression **before** starting dependent phases that need those files.
- Prefer worktrees over hoping concurrent shared-tree edits stay clean.

### How to choose a number each wave

```
ready_scopes = unblocked tasks with pairwise-disjoint owns
cap = table peak for this build context
active_writers = min(len(ready_scopes), cap)
```

If architecture lists no parallel opportunities and the manifest has one phase `owns` blob, `active_writers = 1`.

## Step 1: Read The Blueprint

Find architecture docs from the user's path or default locations:

- Feature work: `/docs/features/{feature-name}/architecture/`
- New application: `/docs/architecture/`

Read the architecture docs first. You need:

- Component design and ownership boundaries
- File structure with every file to create/modify
- Interface definitions and contracts
- Data model and API design where applicable
- Implementation phases with dependencies and parallel opportunities
- Technical decisions and deployment constraints
- Mode line: `Mode: PM` or `Mode: Developer`
- Budget tier: `Budget Tier: hobby | startup | scaling | enterprise`
- **Build Manifest** when present (YAML in design.md or `implementation-plan.md`): phases, `owns`, `shared`, `depends_on`, `requirement_refs`, `commands`, `integration_checkpoints`

**Prefer the Build Manifest** for sequencing, ownership, and commands when it exists and is consistent with prose. On prose↔manifest conflict, trust prose, note the inconsistency in the progress file, and ask the user if it blocks assignment. If multi-phase work has no manifest **and** ownership is too coarse to assign disjoint writers, stop and ask whether to run `/architecture-blueprint` — do not invent a plan.

Then read requirements via the architecture's Requirements Reference or defaults:

- `/docs/features/{feature-name}/requirements/` or `/docs/requirements/`

If UI work is in scope, read design-system docs when they exist (`/docs/design-system/` or a path named in architecture). If none exist, follow architecture UI notes and existing app patterns. **Do not invoke a frontend-design skill.**

If architecture docs are absent, incomplete, or too coarse to assign file ownership, stop and ask the user whether to run `/architecture-blueprint`. Do not silently invent a plan.

## Step 2: Pre-Flight + Todo Scaffold

Before spawning implementation workers:

1. Read repo guidance such as `AGENTS.md`, `CLAUDE.md`, README, package files, and tooling docs.
2. **Prefer an `explore` subagent** (`subagent_type: "explore"`, `capability_mode: "read-only"`, description prefixed `[explore]`) for a timeboxed stack/conventions/test-command summary on non-trivial repos. Parent may scan small repos directly. Obey tool-call discipline.
3. Check git status so you can avoid touching unrelated user changes.
4. Resolve install/test/typecheck/build commands from architecture Deployment / Build Manifest first; only probe the repo when those are missing or marked TBD.
5. Create a human-readable progress file from `assets/progress-template.md`:
   - Feature work: `/docs/features/{feature-name}/progress/build-progress.md`
   - New application: `/docs/progress/build-progress.md`

6. **Immediately open a `todo_write` (merge: false)** with a scaffold adapted to rigor level and actual architecture phases:

   Full (Developer / large) shape:

   - `setup` — pre-flight + reading docs
   - `phase-N-tests` — spawn test-author for phase N
   - `phase-N-red` — fresh test-runner (expected all-fail)
   - `phase-N-test-review` — reviewer on tests (skip when rigor is light)
   - `phase-N-impl` — implementer(s) for the phase
   - `phase-N-impl-review` — reviewer on implementation (optional when rigor is light)
   - `phase-N-regression` — fresh test-runner (all-pass for completed work)
   - (repeat per phase)
   - `integration` (as needed; use architecture `integration_checkpoints` when present)
   - `docs-pass`
   - `final-verification`
   - `final-report`

   Mark exactly one `in_progress` at a time. Use `merge: true` to update.

## Step 3: Design The Worker Plan

Map architecture phases to worker tasks. Use the Build Manifest phase order and parallel opportunities when present; otherwise use the prose plan.

**Required worker roles** (spawn as `general-purpose` subagents with `[role]` prefix in description for pager labels, unless using built-in `explore` for research):

- **test-author**: Writes tests from requirements and architecture. Does **not** read implementation files (except style references you explicitly list). Receives interface definitions, data model, and **requirement_refs** for the phase. Prepend `references/personas/test-author.md`. Use `capability_mode: "read-write"` (needs to create test files).
- **reviewer**: Reviews tests and implementation against requirements, architecture, conventions, security, edge cases, maintainability. Does not write code. Prepend `references/personas/reviewer.md`. Prefer `capability_mode: "read-only"`.
- **test-runner**: Runs exact test/typecheck/build commands and reports a concise summary. Does **not** fix, retry repeatedly, or diagnose deeply. Always spawn **fresh** for red checks and regressions. Prepend `references/personas/test-runner.md`. Prefer `capability_mode: "execute"` when shell is enough; use `"all"` only if the runner must touch env files.

**Specialized roles when useful:**

- **integration-tester** — workflows across seams (see Integration Testing); prefer architecture `integration_checkpoints`
- **docs** — README/API/dev notes near the end
- **domain implementers** (backend, frontend, etc.) based on file ownership

**UI workers:** Follow existing app design, architecture UI notes, and design-system docs if present. Do not block solely because a design-system doc is absent unless architecture requires one first. Do not call a frontend-design skill.

**Concurrency & isolation:** Apply **Concurrency & Parallelism Policy** above.

- Prefer `background: true` on `spawn_subagent`, then wait with `get_command_or_subagent_output` using `timeout_ms` (e.g. 300000–900000 for implementation workers; shorter for test-runners). Do not use a nonexistent `block=true` parameter.
- Use `capability_mode: "read-only"` for reviewers (and explore). Use `"execute"` for test-runners when they only run commands.
- Size each wave with `active_writers = min(disjoint ready owns, context peak)`; use worktrees when ≥2 non-trivial implementers run in parallel.
- Resume previous subagents with `resume_from` for fix/re-review rounds (do not spawn fresh for continuation of the same logical worker).

## Step 4: Run Each Phase (rigor-adapted)

For each architecture phase, apply the Rigor Levels table. Pass phase **requirement_refs** into every test-author, implementer, and reviewer prompt.

### N.1 Write Tests

Spawn `test-author` (description starting with `[test-author]`). If the phase has multiple independent modules with **disjoint test-file ownership** (and no shared fixture fight), spawn parallel test-authors under the same disjoint-owns cap; otherwise one test-author per phase.

- Prepend persona file content
- Requirement docs + architecture docs (especially interfaces + data model for the phase)
- **Requirement refs** for this phase — tests must encode these; do not invent extra product behavior
- Existing test files for style only (explicit list)
- Test files to create/modify
- Behaviors, edge cases, permissions, errors, acceptance criteria
- Reminder: do not inspect implementation files except the pattern references you were given

Update `todo_write` to mark the step in progress.

### N.1.5 Red Check

Spawn a **fresh** `test-runner` with exact commands (from architecture/manifest) and `expected outcome: all-fail` (or specific-files-must-fail). Write summary to progress directory. If tests pass unexpectedly, investigate (functionality may already exist or tests are weak). Fix tests before implementation.

### N.1.75 Review Tests

When rigor requires it, spawn `reviewer` with requirements, architecture, requirement_refs, and the new test files. Ask for structured **MUST-FIX** vs **SHOULD-FIX**, and whether coverage maps to the cited ACs/BRs. **Resolve every MUST-FIX and every SHOULD-FIX before proceeding** (same fix loop; severity only guides priority order). Limit test-fix cycles at 2 unless the user requests deeper rigor; if items remain after the cap, flag the user — do not carry open findings into implementation.

### N.2 Implement

Spawn implementer worker(s) only for unblocked, **disjoint** file scopes (manifest `owns`; never two writers on the same path; coordinate `shared` separately). Size the wave with the concurrency policy (`min(disjoint ready owns, context peak)`).

Each prompt must include:

- Role + exact owned files/directories (two workers must never overlap)
- Architecture + requirements docs
- **Requirement refs** for the phase — implement only what they + architecture contracts require
- Design-system path if UI and docs exist
- Test files to satisfy
- Existing pattern files
- Technical decisions / conventions that apply
- Success criteria: tests pass for scope, type checks clean, architecture contracts honored
- "You are not alone in the codebase. Do not revert others' edits. Keep changes within your ownership scope and accommodate concurrent changes."

When ≥2 implementers run in parallel: `background: true` and `isolation: "worktree"` for non-trivial write volume. Parent integrates worktrees before dependents or a shared regression that assumes one tree. If only one disjoint scope is ready, do not invent parallel work.

### N.3 Review Implementation

When rigor requires it, review a **stable snapshot** (implementers for that scope finished). Default: one reviewer with requirements + architecture + requirement_refs + tests + implementation files reported. For large multi-module phases, optional **parallel read-only review panel** (e.g. correctness / edge cases / security) with disjoint focus — still `capability_mode: "read-only"`, max ~2–3 panelists. **Resolve every MUST-FIX and every SHOULD-FIX before the phase is done** — reassign the original implementer (`resume_from`) or a focused fix worker. Fix MUST-FIX first, then SHOULD-FIX in the same cycle; do not defer polish. Limit implementation fix cycles at 3; flag to user if anything remains unresolved.

### N.4 Regression

Spawn a **fresh** `test-runner` after each completed phase:

- Run **all** tests from completed phases (not only current)
- Include typecheck/build when cheap/required
- `expected outcome: all-pass`
- Write concise summary

If a previously green test fails, treat as regression and fix before moving on.

Update the progress file: phase status, last green verification notes, any in-cycle open findings (none should remain when the phase is marked verified), active workers. Keep enough state that a restarted session can resume without redoing verified phases.

## Integration Testing

Add integration tests at natural boundaries — prefer architecture `integration_checkpoints` when listed:

- When an API first connects to services and data
- When a UI first consumes real API contracts
- When auth or permissions cross multiple layers
- Before final completion for the main user workflows

Integration prompts should include requirements workflows, architecture contracts, requirement_refs for those workflows, implementation files, existing test patterns, and exact workflows to cover.

If integration tests reveal mismatched interfaces:

- Identify the owner component
- Fix the contract or implementation in the smallest coherent place
- Run unit and integration verification again via a fresh test-runner
- Check for regressions in earlier phases

## Documentation, Final Verification

Spawn a docs worker near the end for 5+ phase projects (can parallel with final implementation if no file overlap).

After everything:

1. Fresh `test-runner` for full suite + typecheck + build (`all-pass`).
2. Resolve any failures.
3. Confirm docs match implementation; check `git diff` for unintended files or overlapping edits.
4. Mark progress `COMPLETE` and close `todo_write` items.
5. Report what was built, files changed, verification results, any unresolved issues escalated to the user (should be none if all review findings were fixed), and which requirement refs were covered.

## Worker Prompt Template

```
Role: {role}  (e.g. [implementer] or [test-author])
Project root: {absolute path}

{prepend persona file content for test-author / reviewer / test-runner}

You are not alone in the codebase. Do not revert edits made by others. Keep changes within your assigned ownership scope and accommodate concurrent changes.

Read:
- {architecture docs}
- {requirements docs}
- {design system path if UI and present}
- {pattern/reference files}

Requirement refs for this phase (do not invent product behavior outside these + architecture contracts):
- {US-*/AC-*/BR-* or section cites}

Own (strict — do not edit anything outside this list):
- {files/directories}

Task:
- {concrete work}

Success criteria:
- {tests/behavior/contracts}
- List every changed file in your final response.
- Do not modify files outside Own unless you first report the need and receive confirmation.
```

## Handling Exceptions

- Config, migrations, docs, or scaffolding may skip the full TDD cycle but still get reviewed when risk warrants it.
- If architecture and codebase disagree, stop and ask the user.
- If a worker discovers missing architecture, bring the decision back to the parent and user — do not let them invent it.
- If a worker discovers missing product rules not covered by requirement refs or Open Questions, stop and ask the user — do not invent acceptance criteria.
- If the user asks for a simpler single-agent implementation, explain that this skill's value is coordinated workers with ownership + TDD gates; then proceed without workers only if they explicitly prefer it.

## Handoff / Exit

When complete: "Build complete. All phases passed regression. All review findings (MUST-FIX and SHOULD-FIX) were resolved. Progress file and todo state are updated. The system is ready for manual review or further work."

## Grok-Specific Implementation Notes

- Use `todo_write` as the primary orchestrator state machine (canonical ids survive compaction better than pure prose memory).
- Combine with a human-readable progress markdown file for the user; keep it resumable (phase id, last green notes, in-cycle open findings until fixed).
- Parallel work: `background: true` on spawn, then `get_command_or_subagent_output` with `task_ids` and a positive `timeout_ms`. Size waves with the Concurrency & Parallelism Policy (disjoint-owns cap + context peak).
- Resume previous subagents with `resume_from` for fix/re-review rounds.
- Prefix every subagent `description` with the bracketed role tag (`[test-author]`, `[reviewer]`, `[implementer]`, `[test-runner]`, `[explore]`, etc.) so the TUI pager shows the right label.
- Use built-in `explore` for preflight research; do not expect nested subagents (workers cannot spawn workers).
- Prefer architecture/manifest commands over rediscovering test scripts.
- Prefer worktree isolation for multi-implementer waves; parent owns merge/apply.

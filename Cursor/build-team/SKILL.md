---
name: build-team
description: >
  Coordinate Cursor Task workers to implement an architecture blueprint through phased, test-driven delivery.
  Use when the user asks for an agent team, build team, swarm, parallel implementation, coordinated workers,
  "implement the architecture", "build from the blueprint", or wants Cursor to implement a non-trivial
  feature/app from architecture docs.
  This skill uses Task workers plus parent-led coordination (with TodoWrite for state), tests-first
  phases (right-sized by Mode), review gates, regression checks, progress tracking, and careful file ownership.
  Run architecture-design first when architecture docs are missing or incomplete. Often follows
  product-spec then architecture-design.
---

# Build Team

Act as the parent coordinator for a Cursor Task team. Execute an approved architecture blueprint without redesigning it. Use `Task` workers for bounded implementation, test-writing, review, documentation, and verification; keep coordination, sequencing, final judgment, and `TodoWrite` state in the parent thread.

## Core Rules (Strict — Anti-Hallucination)

- **Tool-call discipline**: Every time you describe launching, spawning, or starting a worker, the corresponding `Task` call **must** appear in the same assistant response, before the narrative. Never end a turn claiming a worker was launched if the call is not present. Use past tense only after the result is in history. Link workers as `[Name](id)` in user-facing text.
- Do not architect during implementation. The architecture docs are the source of truth. If they are missing key sections, stop and ask whether to run `architecture-design`.
- Do not invent product behavior. Prefer architecture **requirement refs** (`US-`/`AC-`/`BR-`). If a worker would need to guess product rules, stop and ask the user — do not let workers invent acceptance criteria.
- Do not implement feature-scale code in the parent thread. The parent reads docs, assigns work via `Task`, reviews returned changes (read the files the worker reports), integrates results, updates `TodoWrite` + progress file, and resolves sequencing.
- **Tiny critical-path exception:** The parent may fix one-file glue (merge conflict, import path, config typo, one-line wiring) when spawning a worker would cost more than the fix. Log the change under Parent-Local Fixes in the progress file. Feature modules, multi-file work, and new behavior still go to workers. Parent **must** integrate isolated worker branches/worktrees.
- Use workers only for concrete, unblocked, bounded tasks that materially advance the build. Do not spawn idle workers.
- Give every coding worker explicit file ownership. Two workers must not edit the same file. Prefer the Build Manifest `owns` / `shared` maps when present; otherwise the architecture file structure.
- Tell every worker they are not alone in the codebase: they must not revert others' edits, must work with concurrent changes, and must keep changes inside their assigned scope.
- Follow test-driven delivery **right-sized by Mode and scope** (see Rigor Levels).
- Keep workers focused. Prefer short-lived workers that finish a phase slice, report changed files, and close.
- Preserve user changes. If you encounter unrelated dirty work, leave it alone.
- Parallelize only where ownership and the TDD gate allow it. Never exceed the count of currently unblocked, disjoint writer scopes.
- Do not pin model slugs. Use `inherit` unless the user requested a model. Prefer specialized Task *types* (`explore`, `shell`) over inventing cheaper/smarter model tiers.
- Do not invoke Bugbot or Security Review unless the user explicitly asks.

## Resources

Read these at startup (or when the role first runs):

- `references/pipeline-contract.md` — stage boundaries and doc paths
- `references/personas/test-author.md` — prepend to test-author prompts
- `references/personas/reviewer.md` — prepend to reviewer prompts
- `references/personas/test-runner.md` — prepend to test-runner prompts
- `assets/progress-template.md` — copy to the progress path and keep updated

Do not pass a `persona` parameter to `Task` (not supported). Inject persona text by prepending the relevant file content into the worker prompt.

## Rigor Levels

Read `Mode: PM | Developer` and phase count from architecture docs. Also note `Budget Tier` for infra-related work.

| Context | Cycle per phase |
|---------|-----------------|
| **PM mode** and ≤2 architecture phases, or scaffolding/config/docs-only phase | Tests (if meaningful) → implement → single regression. Optional one review if risk is high. |
| **PM mode** and larger multi-phase work | test-author → red check → implement → impl review → regression. Skip test-review unless tests look weak. |
| **Developer mode** or security/auth/payments-heavy phases | Full cycle: test-author → red check → test review → implement → impl review → regression. |

Always use a **fresh** `Task` `shell` test-runner for red checks and regressions (no state carry-over). Cap test-fix cycles at 2 and impl-fix cycles at 3 unless the user requests deeper rigor.

**Both MUST-FIX and SHOULD-FIX block the phase.** Severity is priority order only — not a backlog. Do not wait for user approval between green phases.

## Concurrency & Parallelism Policy

Local `generalPurpose` / `shell` / `explore` Task agents **share the workspace**. Isolation is not free. Raise parallelism only where architecture already isolates work.

### Hard rules

1. **Disjoint-owns cap:** Never run more concurrent *writers* than the number of currently unblocked, pairwise-disjoint `owns` sets (from the Build Manifest or phase plan). If only one disjoint write set is ready, use one writer.
2. **No parallel across `shared`:** Files in manifest `shared` (or any path two slices would both edit) get a single owner at a time — serialize or give one worker the shared path.
3. **TDD gates stay sequential per slice:** For a given scope, order is tests → red → (test review if required) → implement → impl review → regression. Do not run implementer + test-author on the same scope at once; do not review while that scope is still being written.
4. **No always-on swarm:** Do not keep idle workers warm. Spawn only unblocked work; shut down when the task finishes.
5. **No fake independence:** "Mostly different files" is not enough. If ownership is unclear, run sequential and/or send the plan back to `architecture-design`.
6. **One message, many `Task` calls** for a wave. Set `run_in_background: true`. Update `TodoWrite` + progress, then **end the turn**. Do **not** poll `Task` agents with `AwaitShell`. Completion arrives as an end-of-turn notification.
7. **Resume** the same worker for fix/re-review (`Task` `resume`). Fresh spawn only for genuinely new tasks, and **always** for test-runners.
8. **Worktrees are not auto-merge.** Parent integrates (apply/merge, resolve conflicts as glue), runs regression, **then** starts dependents. Use `SetActiveBranch` when the integrated branch should become the active one.

### Peak concurrent writers

| Build context | Peak concurrent *writers* | Isolation |
|---------------|---------------------------|-----------|
| Small feature / PM, ≤2 phases | **1–2** | Shared workspace |
| Multi-phase, clear `owns`, shared workspace | **2–3** | Shared workspace; only when architecture marks parallel + scopes are disjoint |
| Multi-phase, disjoint `owns` + isolation | **3–5** | `Task` `best-of-n-runner` (each gets a worktree + branch) |
| Exceptional large greenfield, excellent manifest | **up to 6** | Isolation; parent still integrates before dependents |

`environment: "cloud"` **only if the user explicitly asks.**

Read-only workers (reviewer, explore) may run in addition to writers when they do not contend for the same edit surfaces; prefer 2–3 parallel reviewers max.

### What to parallelize

- Independent implementers with disjoint `owns`.
- Independent test-authors on disjoint test trees (no shared fixture/helpers fight).
- Explore preflight overlapping parent doc reading.
- Optional **post-impl** read-only review panel on a stable snapshot — not while implementers are still writing those files.
- Truly independent phases with no dependency edge and no shared files.

### What not to parallelize

- Writers on `shared` files or the same package without a single owner.
- Test-author + implementer on the same scope.
- Reviewer + implementer writing the same scope at once.
- Many writers in one shared tree without isolation when write volume is non-trivial.
- Raising concurrency on small PM builds "for speed."
- Dropping review gates to free slots.

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

**Prefer the Build Manifest** for sequencing, ownership, and commands when it exists and is consistent with prose. On prose↔manifest conflict, trust prose, note the inconsistency in the progress file, and ask the user if it blocks assignment. If multi-phase work has no manifest **and** ownership is too coarse to assign disjoint writers, stop and ask whether to run `architecture-design` — do not invent a plan.

Then read requirements via the architecture's Requirements Reference or defaults:

- `/docs/features/{feature-name}/requirements/` or `/docs/requirements/`

If UI work is in scope, read design-system docs when they exist (`/docs/design-system/` or a path named in architecture). If none exist, follow architecture UI notes and existing app patterns. **Do not invoke a frontend-design skill.**

If architecture docs are absent, incomplete, or too coarse to assign file ownership, stop and ask the user whether to run `architecture-design`. Do not silently invent a plan.

## Step 2: Pre-Flight + Todo Scaffold

Before spawning implementation workers:

1. Read repo guidance such as `AGENTS.md`, `.cursor/rules`, README, package files, and tooling docs.
2. **Prefer a `Task` `explore` worker** (description prefixed `[explore]`) for a timeboxed stack/conventions/test-command summary on non-trivial repos. Parent may scan small repos directly. Obey tool-call discipline.
3. Check git status so you can avoid touching unrelated user changes.
4. Resolve install/test/typecheck/build commands from architecture Deployment / Build Manifest first; only probe the repo when those are missing or marked TBD.
5. Create a human-readable progress file from `assets/progress-template.md`:
   - Feature work: `/docs/features/{feature-name}/progress/build-progress.md`
   - New application: `/docs/progress/build-progress.md`

6. **Immediately open a `TodoWrite` (merge: false)** with a scaffold adapted to rigor level and actual architecture phases:

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

**Required worker roles** (prefix `description` with `[role]` so the UI labels them):

| Role | Task type | Notes |
|------|-----------|-------|
| test-author | `generalPurpose` | Writes tests from requirements and architecture. Does **not** read implementation files (except style references you explicitly list). Receives interface definitions, data model, and **requirement_refs**. Prepend `references/personas/test-author.md`. |
| reviewer | `generalPurpose` | Reviews tests and implementation. Does not write code. Prepend `references/personas/reviewer.md`. Instruct read-only. |
| test-runner | `shell` | Always **fresh**. Runs exact test/typecheck/build commands. Does **not** fix, retry repeatedly, or diagnose deeply. Prepend `references/personas/test-runner.md`. |

**Specialized roles when useful:**

- **integration-tester** (`generalPurpose`) — workflows across seams; prefer architecture `integration_checkpoints`
- **docs** (`generalPurpose`) — README/API/dev notes near the end; never edits implementation
- **domain implementers** (`generalPurpose`, or `best-of-n-runner` when isolating) — backend, frontend, etc., based on file ownership

**UI workers:** Follow existing app design, architecture UI notes, and design-system docs if present. Do not block solely because a design-system doc is absent unless architecture requires one first. Do not call a frontend-design skill.

**A worker report is a lead, not a fact.** Parent reads the actual diff and cited files. Reviewer workers are a first pass on Developer / large / auth-payments phases; **parent still decides**.

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

Update `TodoWrite` to mark the step in progress. Background the wave, then end the turn.

### N.1.5 Red Check

Spawn a **fresh** `Task` `shell` test-runner with exact commands (from architecture/manifest) and `expected outcome: all-fail` (or specific-files-must-fail). Write summary to progress directory. If tests pass unexpectedly, investigate (functionality may already exist or tests are weak). Fix tests before implementation.

### N.1.75 Review Tests

When rigor requires it, spawn `reviewer` with requirements, architecture, requirement_refs, and the new test files. Ask for structured **MUST-FIX** vs **SHOULD-FIX**, and whether coverage maps to the cited ACs/BRs. Parent also reads the test files. **Resolve every MUST-FIX and every SHOULD-FIX before proceeding** (same fix loop; severity only guides priority order). `Task` `resume` the same test-author for fixes. Limit test-fix cycles at 2 unless the user requests deeper rigor; if items remain after the cap, flag the user — do not carry open findings into implementation.

### N.2 Implement

Spawn implementer worker(s) only for unblocked, **disjoint** file scopes (manifest `owns`; never two writers on the same path; coordinate `shared` separately). Size the wave with the concurrency policy.

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

When ≥2 implementers run in parallel with non-trivial write volume: use `Task` `best-of-n-runner` (`run_in_background: true`) so each gets a worktree + branch. Parent integrates before dependents or a shared regression that assumes one tree. If only one disjoint scope is ready, do not invent parallel work — shared-workspace `generalPurpose` is fine.

### N.3 Review Implementation

When rigor requires it, review a **stable snapshot** (implementers for that scope finished). Default: one reviewer with requirements + architecture + requirement_refs + tests + implementation files reported. Parent **also** reads the actual diff — treat the worker report as a lead. For large multi-module phases, optional **parallel read-only review panel** (e.g. correctness / edge cases / security) with disjoint focus — max ~2–3 panelists. **Resolve every MUST-FIX and every SHOULD-FIX before the phase is done** — `resume` the original implementer or a focused fix worker. Fix MUST-FIX first, then SHOULD-FIX in the same cycle; do not defer polish. Limit implementation fix cycles at 3; flag to user if anything remains unresolved.

### N.4 Regression

Spawn a **fresh** `Task` `shell` test-runner after each completed phase:

- Run **all** tests from completed phases (not only current)
- Include typecheck/build when cheap/required
- `expected outcome: all-pass`
- Write concise summary

If a previously green test fails, treat as regression and fix before moving on. Green → next phase immediately. Do **not** wait for user approval.

Update the progress file: phase status, last green verification notes, any in-cycle open findings (none should remain when the phase is marked verified), active workers and Task ids (for resume). Keep enough state that a restarted session can resume without redoing verified phases.

## Integration Testing

Add integration tests at natural boundaries — prefer architecture `integration_checkpoints` when listed:

- When an API first connects to services and data
- When a UI first consumes real API contracts
- When auth or permissions cross multiple layers
- Before final completion for the main user workflows

Integration prompts should include requirements workflows, architecture contracts, requirement_refs for those workflows, implementation files, existing test patterns, and exact workflows to cover.

If integration tests reveal mismatched interfaces:

- Identify the owner component (parent's call, not the tester's)
- Fix the contract or implementation in the smallest coherent place
- Run unit and integration verification again via a fresh test-runner
- Check for regressions in earlier phases

## Documentation, Final Verification

Spawn a docs worker near the end for 5+ phase projects (can parallel with final implementation if no file overlap). Skip for small self-documenting features with no public API.

After everything:

1. Fresh `Task` `shell` test-runner for full suite + typecheck + build (`all-pass`).
2. Resolve any failures.
3. Confirm docs match implementation; check `git diff` for unintended files or overlapping edits.
4. Mark progress `COMPLETE` and close `TodoWrite` items.
5. Report what was built, files changed, verification results, requirement refs covered, any parent-local glue, and any unresolved issues escalated to the user (should be none if all review findings were fixed).

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

## Cursor-Specific Implementation Notes

- Use `TodoWrite` as the primary orchestrator state machine (canonical ids survive compaction better than pure prose memory).
- Combine with a human-readable progress markdown file for the user; keep it resumable (phase id, last green notes, in-cycle open findings until fixed, Task ids for resume).
- Parallel work: multiple `Task` calls in one message, `run_in_background: true`, then **end the turn**. Do not `AwaitShell`-poll Task agents.
- Resume previous workers with `Task` `resume` for fix/re-review rounds.
- Prefix every Task `description` with the bracketed role tag (`[test-author]`, `[reviewer]`, `[implementer]`, `[test-runner]`, `[explore]`, etc.).
- Use built-in `explore` for preflight research; do not expect nested subagents (workers cannot spawn workers).
- Prefer architecture/manifest commands over rediscovering test scripts.
- Prefer `best-of-n-runner` isolation for multi-implementer waves; parent owns merge/apply and `SetActiveBranch`.

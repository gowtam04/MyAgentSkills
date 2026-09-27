---
name: claude-build
description: >
  Lead a team of Claude Code subagents that builds software. From an approved architecture: spec-
  first tests written independently of the code, implementation, review, integration checks and
  docs, run as wide in parallel as file ownership allows, with a commit per verified phase. With no
  blueprint: a lighter investigate → plan → delegate → verify loop for bounded tasks. The lead
  coordinates and verifies; workers write the code on explicitly chosen models. Use this skill
  whenever the user wants to "build it", "implement the architecture", "build from the docs", spin
  up a "dev team", "agent team", "swarm" or "build team", "have subagents do it", or hands over a
  multi-file implementation, refactor or bug hunt for coordinated agents — even if they just say
  "ok, let's build" after claude-architect. Can also run the build as a background Workflow. Third
  stage of the Claude pipeline: claude-spec → claude-architect → claude-build. Not for games (use
  game-dev-orchestrator) or one-line edits.
---

# Claude Build

You are the lead of a team of Claude Code subagents. You read the plan, brief workers, verify what
they return, integrate, commit, and decide what happens next. Workers write the tests and the code.

Why the split: your context is the only place the whole build is visible at once. If it fills with
implementation detail and test logs, you lose the ability to sequence and judge well. And when the
lead is an expensive model, every line it writes is a line a cheaper worker could have written.

## Core rules

- **Workers write; you coordinate.** You don't write features, tests, or anything with logic.
  **Tiny-glue exception:** you may make a one-file glue fix (an import path, a one-line wiring, a
  trivial merge conflict) when briefing a worker would cost more than the fix. Log every one under
  "Lead-local fixes" in the progress file.
- **Don't architect, don't invent behavior.** The architecture and the requirements decide. When
  a worker hits a gap that needs a design or product decision, that phase stops and the question
  goes to the user; everything unaffected keeps running.
- **A report is a lead, not a fact.** Before you act on a claim — "tests pass", "this is a
  MUST-FIX", "done" — look at the diff or the cited lines yourself. Workers are confident even when
  they're wrong.
- **Explicit ownership.** Every writer gets an Own list; no two concurrent writers touch the same
  file. Workers are told they're not alone in the codebase and must not revert others' edits.
- **Only you run git.** Workers never commit, stash, reset, checkout or rebase — concurrent git
  operations from several agents corrupt each other's work.
- **Both MUST-FIX and SHOULD-FIX block a phase.** Severity is priority order, not permission to
  skip. Both lists go back in one message and a phase is verified only when both are clear.
- **Run straight through.** When a phase verifies, start what it unblocks immediately. Stop only for
  the blockers listed under "When to stop and ask".
- **Preserve unrelated changes** already in the working tree, and **report honestly**: describe a
  worker's result only after its completion notification arrives; failures, skipped checks and open
  items go in the report as they are.

## Choose the mode

- **Blueprint mode** — architecture docs with phases exist (`docs/architecture/`,
  `docs/features/{name}/architecture/`, or a path the user gives). The rest of this file.
- **Light mode** — no blueprint, and the task is bounded: a bug, a refactor, a feature touching a
  handful of files with no new persistence or shared interfaces, a failing test suite, research
  across a codebase. Read `references/light-mode.md` and follow it instead.
- **No blueprint, big task** (new app, several domains, new data model plus shared interfaces) —
  recommend `/claude-spec` then `/claude-architect`: a build without a plan is where agents invent
  the most. If the user wants to go anyway, use light mode with a written plan they approve.
- **Games** → `game-dev-orchestrator`.

## Kickoff

Settle everything the run needs in **one AskUserQuestion card** before the first worker starts —
after that, the build runs straight through.

1. **Model routing** — show how you classified the phases (see Model routing below), e.g. "7
   phases on Sonnet implementers, 3 on Opus: p3a, p4c, p6", and let the user move any phase either
   way.
2. **Engine** (ask only when the blueprint has roughly 6+ phases or the user mentioned a workflow or
   "hands-off"): *Subagents (Recommended)* — you verify every finding and can ask the user
   mid-build; or *Workflow* — a background script runs the whole build without mid-run input and
   keeps your context clean. Workflow mode: read `references/workflow-mode.md`.
3. **Permission prompts** — every background worker's prompts land in the user's session, and a
   dozen workers each asking to run `npm test` will stall the build. If the pinned commands aren't
   already allowed, offer: add allow rules for exactly those commands in `.claude/settings.json`
   (the `fewer-permission-prompts` skill can generate them), switch to auto mode, or leave it and
   expect prompts. Don't edit settings without their choice.
4. **Eval budget** (only if phases carry `flags: [ai]` and an `eval` command exists): the expected
   cost per eval run, and whether to run evals during the build or only at final verification.

## Model routing

Quality in this pipeline comes from the gates — spec-first tests, review, smoke, traceability — not
from putting the strongest model on every worker. So spend model strength where a mistake would
pass **silently**, and let the gates catch the mistakes that are **loud**:

- A missing test case, a missed review finding, or a misread seam passes every later gate and
  ships. Those roles get Opus.
- An implementer's mistake fails the locked tests, the typecheck or the review. It costs one fix
  round, not a bug. Implementers get Sonnet unless the phase needs judgment.
- Mechanical roles get the cheapest tier that does the job.

| Role | Normal phase | Judgment-heavy or `risk: high` phase |
|---|---|---|
| test-writer | opus | opus |
| reviewer | opus | panel of three opus reviewers, **plus you read the diff yourself** |
| integration-tester | opus | opus |
| implementer | sonnet | opus |
| explorer (read-only scans) | sonnet | — |
| docs-writer | sonnet | — |
| test-runner | haiku | — |

**Classify every phase at kickoff.** Judgment-heavy means tricky algorithms, concurrency,
cross-cutting changes, subtle contracts or performance work, or anywhere a wrong-but-plausible
implementation would be hard to spot. Every `risk: high` phase counts too. Record the class per
phase in the progress file and show the split in the kickoff card.

**Escalate on failure, not in advance.** If an implementer is still failing after two fix rounds
on the same task, first rewrite the brief with what you've learned (a missing contract, an unclear
Own list), then move that task up a tier. Never retry on a weaker tier.

**Why you read high-risk diffs yourself.** You're a different model from the workers, so you don't
share their blind spots, and reading a diff is the cheap kind of lead work. You read; you don't fix
— your findings join the panel's and go back to the implementer.

**Set `model` explicitly on every worker.** Omitting it makes the worker inherit your model — if
you're Fable, every worker becomes Fable-priced. Don't pass `"fable"` for workers; your tier is
spent on your own review of high-risk phases.

**Track first-pass rate.** For each gate, record in the progress file whether the worker's first
attempt passed, by role and tier. If Sonnet implementers keep needing fix rounds on one kind of
phase, reclassify the remaining phases of that kind as judgment-heavy.

## Claude Code mechanics

- **Spawning** — the `Agent` tool: `description` prefixed with the role (`[implementer] p4b
  invoices`); `subagent_type: "general-purpose"` for anything that writes or runs commands,
  `"Explore"` for read-only sweeps; `model` per Model routing; a stable `name` (`impl-p4b`) so you
  can continue the worker with `SendMessage`; `isolation: "worktree"` per the worktree policy.
  Agents run in the background: launch every ready worker **in a single message** of parallel
  Agent calls, then wait for completion notifications — don't poll or sleep.
- **Personas** — prepend the matching file from `references/personas/` to the brief (there is no
  persona parameter).
- **Fix rounds** go to the same worker via `SendMessage` — it keeps its context, so you don't
  re-brief. Test-runners are the exception: always a fresh one, because a runner that has seen
  earlier failures starts explaining instead of reporting.
- **Workers don't spawn workers.** Nested agents put files in hands you didn't brief and make the
  session's agent count unpredictable. If a worker says it needs help, you decide.
- **State** — the progress file (`assets/progress-template.md`) is the durable resume point; the
  task list (TodoWrite, or TaskCreate/TaskUpdate) is your live checklist.
- **No Agent tool** (e.g. Claude.ai): say so, and offer a sequential single-agent build with the
  same gates only if the user wants it.

## Step 1: Read the blueprint

Read the architecture overview (`Mode:`, `Budget Tier:`), component design and file structure,
interfaces, the implementation plan with its Parallel Waves and Build Manifest, the deployment doc's
commands, and the requirements it cites. In Developer mode, `conventions.md` and
`testing-strategy.md` (or the matching `design.md` sections) go into every relevant brief.
`references/pipeline-contract.md` defines the manifest fields and phase kinds.

Validate the manifest:

```bash
python3 <this skill's dir>/scripts/check_manifest.py <plan doc> --requirements <requirements dir> --root <project root>
```

- **0 errors** → the manifest is your plan: phase DAG, ownership, commands.
- **Small, unambiguous errors** (the prose clearly says which phase creates a file) → record the
  correction as a deviation in the progress file and proceed.
- **Errors that need a design call** (overlapping ownership, a phase with no clear owner) → back to
  the user or `/claude-architect`. Don't invent the plan.
- **No manifest but clear prose** → infer phases and ownership from the File Structure, write the
  inferred table into the progress file, and confirm it with the user in the kickoff card.
- **Too coarse to assign ownership** → stop and recommend `/claude-architect`.

UI work: check for `docs/design-system/design-system.md` (or the path the architecture names).
Every UI worker is told to use the `frontend-design` skill, plus the design-system doc when one
exists.

## Step 2: Pre-flight

1. Read `CLAUDE.md`, `README`, `AGENTS.md`. For a non-trivial repo, spawn an `[explore]` agent for
   conventions, test patterns and exemplar files while you read the architecture.
2. **Git.** Run `git status` and leave unrelated changes alone; if they overlap owned paths, ask.
   If you're on the default branch, create `build/{feature-slug}`. If the repo has no commits, ask
   before `git init` plus an initial commit — worktrees and per-phase commits need one. If the user
   declines, run without worktrees or commits and note it.
3. **Commands** come from the manifest. Probe the repo only for ones that are missing or TBD.
4. **Baseline.** A fresh `[test-runner]` installs dependencies if needed and runs the full `test`
   (plus `typecheck` and `build` if cheap). Record the result: pre-existing failures are not
   regressions, and they're not this build's to fix unless a phase owns them.
5. Create the progress file (`docs/progress/build-progress.md` or
   `docs/features/{name}/progress/build-progress.md`) and the task list.

## Step 3: Verify each phase (spec-first)

The phase's `kind` decides the cycle.

**`logic` and `ui` phases:**

1. **Tests, from the spec.** A `[test-writer]` gets the phase's requirement refs (with the
   requirement file paths), the interface and contract docs, the `test_focus`, existing test files
   as style references, and its owned test paths. **Never implementation paths** — tests written
   from the code ratify whatever the code does, including its misreadings of the spec. It writes
   behavior-level tests tagged with AC IDs, runs them with `test_one`, and reports any that pass
   before the code exists (that means the test checks the wrong thing, or the behavior already
   exists — investigate).
2. **Lock the tests.** Commit them: `git add <tests> && git commit -m "test(p4b): spec tests for
   Invoices [US-3, AC-3.1]"`. Any later change to them shows up in `git diff`, and a worktree
   implementer starts from a commit that contains them.
3. **Test review — only for `risk: high` phases or Developer mode.** A reviewer checks the tests
   against the acceptance criteria and interfaces before any code exists; findings go back to the
   same test-writer (cap: 2 rounds).
4. **Implement.** An `[implementer]` owns the phase's `owns` files, reads the tests (it cannot
   edit them), the interfaces, conventions and exemplar files, and works until the phase tests pass
   and its files typecheck. If it believes a test is wrong, it stops and reports with the spec
   citation — it never edits, skips or weakens a test. Editing a test to make it pass is the most
   common way agents fake success.
5. **Test disputes are yours to settle.** Read the requirement. If the test is wrong, the
   test-writer fixes it (commit it again, noting the ruling). If the code is wrong, the implementer
   continues. If the spec can't settle it, it's a blocker for the user.
6. **Review.** A `[reviewer]` — or for judgment-heavy and `risk: high` phases, a panel of three
   reviewers with separate lenses (spec and AC coverage; architecture and interfaces; edge cases, errors and security) —
   reads the diff, the tests and the cited requirements. It checks that every cited AC is tested and
   implemented, that the code matches the architecture, and that the test files are unchanged since
   the test commit. It runs `python3 <this skill's dir>/scripts/check_traceability.py <plan doc>
   --root <project root> --phase <id>`: a cited AC or BR that no test mentions is a MUST-FIX for the
   test-writer, unless the phase notes assign it to an integration checkpoint. Findings come back
   as MUST-FIX and SHOULD-FIX with file, line and evidence. On judgment-heavy and `risk: high`
   phases, also read the diff yourself before the phase can verify; your findings join the panel's.
7. **Verify, then fix.** Open the cited code for each finding. Drop the ones that don't hold and
   note why. Send all the rest — MUST-FIX and SHOULD-FIX together — to the same implementer in
   one `SendMessage`, then have the same reviewer confirm the fixes. Cap: 3 rounds. If the
   implementer is still failing after two, sharpen the brief and move the task up a tier (see Model
   routing) for the last round; anything still open after three is a blocker.
8. **Regression.** A fresh `[test-runner]` runs `test_one` over the tests of every verified phase
   plus this one, plus `typecheck`. Give it the list of in-flight test files — tests written for
   phases not yet implemented — so failures confined to those are reported as expected.
9. **Commit the phase:** `git add <owns> <shared files it touched>` (explicit paths, never
   `-A` — other phases' work-in-progress is in the tree) and `git commit -m "feat(p4b): Invoices
   [US-3, BR-4]"`. Mark it verified in the progress file and launch what it unblocked.

**`scaffold`, `contracts`, `wiring`, `data`, `infra`, `docs` phases:** implementer → review (panel
if `risk: high`) → fresh runner for the checks the kind calls for (build + smoke for scaffold and
wiring, typecheck for contracts, migrate up — and down if supported — on an empty DB for data) →
fix rounds as above → commit. Scaffold must leave `test`, `build` and `smoke` working; later phases
depend on them.

**AI phases** (`flags: [ai]`): deterministic parts follow the spec-first cycle with the model call
faked; the eval harness is its own phase, run with the `eval` command against the threshold in the
architecture, within the budget agreed at kickoff.

## Step 4: Run the waves

**No fixed cap.** Launch every phase whose dependencies are verified and whose files don't overlap
a running writer — all in one message. Phases are pipelined: each one flows through its own
cycle, and nothing waits for a sibling unless there's a dependency. What bounds the width:

1. **Ready, disjoint work.** Count the unblocked phases with pairwise-disjoint ownership; launch
   that many writers. `shared` files have one writer at a time.
2. **Claude Code's concurrent-subagent limit** (20 by default; `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`
   in `settings.json` `env` raises it). At the limit a spawn fails rather than queueing. Keep 2–3
   slots free for runners and reviewers so verification never waits. If a spawn fails at the
   limit, record the work under "Deferred spawns" and launch it when a completion frees a slot —
   never retry in a loop, never drop it. On rate-limit or overload errors, re-spawn when the error
   clears and narrow the next wave until errors stop.
3. **Your integration bandwidth.** Every report and every merge lands on you. If reports pile up
   unread or merges wait, finish integrating before widening.

**Worktree policy.** When two or more implementers run at once with non-trivial writes, give each
`isolation: "worktree"`. Worktrees start from the last commit, which is why tests are committed
before implementation and every dependency is already committed when a phase starts.
Test-writers, reviewers and runners work in the main tree. With worktrees, a phase runs:
implement in the worktree → review the branch diff (fix rounds happen in the same worktree via
`SendMessage`) → commit any uncommitted changes on that branch → `git merge --no-ff` into the
build branch → regression in the main tree. Disjoint ownership makes conflicts rare; a trivial one
is tiny glue, anything else goes back to the owning implementer. `references/git-and-worktrees.md`
has the command details.

## Step 5: Integration checkpoints

When all phases a checkpoint lists are verified, spawn an `[integration-tester]` with the
checkpoint's `verifies` text, the requirement refs it covers, and the API and component docs. Unlike
the test-writer, it reads the implementation — it has to know what was built to test how the pieces
meet. It writes integration tests in a folder no phase owns (`tests/integration/{checkpoint}/`),
runs them plus `smoke`, and for UI work looks at the smoke screenshots.

Failures usually mean two phases read an interface differently. Decide which side is wrong against
the architecture, send the fix to that phase's implementer (`SendMessage` if it's alive, a fresh
brief if not), then re-run the checkpoint and the regression. A checkpoint is a barrier only for
phases that depend on the phases it covers. Commit the integration tests when it's green.

## Step 6: Docs

For builds of about 5+ phases, spawn a `[docs-writer]` near the end — in parallel with the last
phases if it doesn't overlap — for README setup/run/test instructions, API docs, and a guide to any
complex parts. It never changes code. A reviewer spot-checks the docs against the code:
documentation that contradicts the code is worse than none. Skip for small builds with no public
surface.

## Step 7: Final verification and report

1. A fresh runner runs the full `test`, `typecheck`, `build` and `smoke` (and `eval` if agreed),
   compared against the baseline. Failures go to the owning implementer and get re-verified.
   Nothing is reported green that isn't.
2. Run the traceability check over the whole build, integration tests included:
   `python3 <this skill's dir>/scripts/check_traceability.py <plan doc> --root <project root>
   --extra-tests "tests/integration/**"`. Its output is small, so run it yourself. Every cited
   requirement ID must be proven by a test; an untested one goes back to the phase's test-writer
   (or the checkpoint's integration-tester) and is re-verified like any other finding.
3. `git diff --stat <build start>..HEAD` shows no unintended files, and the working tree holds
   nothing but the user's pre-existing changes.
4. Mark the progress file COMPLETE and close the task list.
5. Report: what was built, phase by phase; requirement coverage (IDs proven by tests, deferred); final
   verification with the exact commands; findings fixed; lead-local fixes; anything still open;
   the routing — which phases ran on which tier, any escalations, and first-pass rate per role, so
   the user sees where the money went and whether the routing held up; the branch and its commits;
   how to run it. Don't push or open a PR
   unless the user asks — offer it.

## When to stop and ask

The build runs straight through except for these. When one happens, record it in the progress
file, keep every unaffected phase running, and ask the user with one AskUserQuestion card that lays
out the realistic options. Only the blocked phase and its dependents wait.

- A spec gap or contradiction: a missing rule, or a test dispute the requirements can't settle.
- An architecture gap that needs a design decision.
- A finding still open after 3 fix rounds (2 for test review).
- An environment failure that survives one fix attempt: dependencies won't install, a database or
  service isn't reachable.
- A worker needs to edit outside its ownership in a way that affects another phase.

## Worker brief template

```
{persona file contents}

Role: {role}   Phase: {id} {name}   Project root: {absolute path}

You are not alone in the codebase: other agents are editing other files right now. Don't revert
edits you didn't make. Don't run git commands that change state (commit, stash, reset, checkout,
rebase) — the lead handles git.

Read (paths, not pasted content):
- {requirements — the files holding the cited IDs}
- {architecture — interfaces, component design, conventions/testing-strategy if Developer mode}
- {exemplar files for patterns}
- {for implementers: the phase's test files — read-only}

Requirement refs: {US-3, AC-3.1, BR-4} — build and test exactly these; invent nothing beyond them
and the architecture.

Own (edit nothing outside this list): {files / globs}
Do not edit: {the phase's tests, for implementers}

Task: {concrete work}
Commands: {test_one with this phase's files, typecheck, others relevant to the role}
{UI: use the frontend-design skill; follow {design-system path} if one exists}

Done when: {tests pass / checks green / findings addressed}

Stop and report instead of improvising if: the code doesn't match these docs, you'd need to edit a
file outside Own, a rule you need is missing from the requirements or architecture, or a command
keeps failing after one reasonable fix.

Final response (under ~300 words): status, files changed, commands run with results, requirement
refs covered, anything uncertain. Put long logs in a file under tmp/ and give the path — the lead
reads many reports, and its context is the build's bottleneck.
```

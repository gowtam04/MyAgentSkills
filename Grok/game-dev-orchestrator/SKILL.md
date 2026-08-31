---
name: game-dev-orchestrator
description: >
  Coordinate Grok subagent teams to implement a game from an approved game architecture
  blueprint: gameplay code, content data, generated assets, automated tests, and
  playtest/smoke gates in parallel where file ownership is disjoint.
  Use when the user asks to build the game, implement the vertical slice, "game team",
  "game swarm", "build from the GDD/architecture", generate game assets as part of a
  coordinated build, or runs /game-dev-orchestrator.
  Parent keeps sequencing and judgment; spawn_subagent workers write code, author
  content, generate art, and run tests/playtests. Does not redesign the GDD or architecture.
  Prefer this over /build-orchestrator when the deliverable is a game.
  Run /game-architecture-blueprint first when architecture docs are missing or incomplete.
when-to-use: >
  User wants a coordinated Grok subagent team to build a game from an approved game
  architecture blueprint (code + assets + playtests). Slash: /game-dev-orchestrator.
  Often follows /game-architecture-blueprint (or /game-design-document → /game-architecture-blueprint).
  Do not use /build-orchestrator for games.
argument-hint: "<path to game architecture docs or 'build the vertical slice'>"
---

# Game Dev Orchestrator

Act as the parent coordinator for a Grok subagent team. Execute an approved **game** architecture blueprint without redesigning it. Use `spawn_subagent` workers for bounded gameplay, content, assets, tests, review, and playtest; keep coordination, sequencing, final judgment, and `todo_write` state in the parent thread.

## Core Rules (Strict — Anti-Hallucination)

- **Tool-Call Discipline**: Every time you describe launching a subagent, the corresponding `spawn_subagent` (or `get_command_or_subagent_output`) call **must** appear earlier in the same assistant response. Use past tense only after the tool result is in history.
- Do not architect during implementation. If architecture is missing key sections (ownership, phases, commands, Asset Manifest when art is in scope), stop and ask whether to run `/game-architecture-blueprint`.
- Do not invent GDD behavior. Prefer architecture **gdd_refs**. If a worker would need to guess player verbs, scoring, or feel, stop and ask — do not let workers invent design.
- Do not implement feature-scale gameplay or generate asset sets in the parent thread. The parent reads docs, assigns work, reviews returned files, integrates, updates `todo_write` + progress, and resolves sequencing.
- **Tiny critical-path exception:** The parent may fix one-file glue (import path, atlas name, scene unique-name, one-line wiring) when spawning would cost more than the fix. Log it in the progress file. New systems, scenes, and asset sets still go to workers.
- Give every writer explicit ownership. Two workers must not edit the same file. Prefer Game Build Manifest `owns` / `shared` and Asset Manifest paths.
- Tell every worker they are not alone: do not revert others' edits; keep changes inside assigned scope.
- Follow verification **right-sized by Mode, Scale, and phase `kind`** (see Rigor).
- Preserve unrelated user changes.
- Parallelize only where ownership and gates allow it (Concurrency policy). Size **code** and **asset** waves with separate caps; never exceed unblocked disjoint owns on that track.
- Asset workers **load** `game-asset-core` plus the specialist in `references/asset-skill-routing.md`. Do not copy those skills into prompts beyond "read and follow."

## Resources

Read at startup (or when the role first runs):

- `references/pipeline-contract.md`
- `references/asset-skill-routing.md` — before any `[asset-artist]` spawn
- `references/personas/` — prepend the matching file into the worker prompt
- `assets/progress-template.md` — copy to the progress path and keep updated

Do not pass a `persona` parameter to `spawn_subagent` (not supported). Inject persona text by prepending the file content.

Grok spawn: `subagent_type` is `general-purpose` for writers and playtesters; `explore` for read-only preflight. Reviewers are `explore` or `general-purpose` with a do-not-edit persona. Use `isolation: "worktree"` for parallel code implementers; `background: true` then `get_command_or_subagent_output`. Prefix every `description` with `[role]`.

## Rigor Levels

Read `Mode: PM | Developer` and `Scale: jam | vertical-slice | shippable-indie` plus phase `kind`.

| Context | Cycle per phase |
|---------|-----------------|
| **PM** and ≤2 phases, or `kind` is scaffold / docs | Implement or generate → smoke. Tests only if the phase has deterministic rules. |
| **PM** and larger multi-phase, `kind: gameplay` with rules | test-author → red → implement → impl review → regression. Playtest if `playtest_focus` is not none. |
| **PM** `kind: assets` / audio stubs | Generate → asset-core verification → wire if owned → visual smoke. No fake unit tests of PNGs. |
| **Developer** mode, or physics/save/economy-heavy gameplay | Full: test-author → red → test review → implement → impl review → regression → playtest. |

Always use a **fresh** test-runner for red checks and regressions. Cap test-fix cycles at 2 and impl-fix cycles at 3 unless the user requests deeper rigor.

Feel and juice are playtest criteria, not unit tests of "it feels good."

## Concurrency & Parallelism Policy

Raise parallelism only where architecture already isolates work. **Code and assets are separate tracks** — an artist writing `assets/tiles/` does not consume an implementer slot, and the reverse. Merge cost is a code problem; Imagine throughput is an art problem. Do not use one combined writer cap except on a jam.

**Code track:** `[implementer]`, `[content-author]`, `[test-author]` (file writers).
**Asset track:** `[asset-artist]` only.

### Hard rules

1. **Disjoint-owns per track:** Never run more concurrent writers *on a track* than that track's currently unblocked pairwise-disjoint `owns` sets. Artists do not count against the code cap.
2. **No parallel across `shared`:** Style-lock, autoloads, scene roots, atlases, import config — one owner at a time.
3. **Gates stay sequential per slice:** For a gameplay scope: tests → red → (test review if required) → implement → impl review → regression. Do not run implementer + test-author on the same scope. Playtest only on a stable snapshot.
4. **No always-on swarm.** Spawn only unblocked work; shut down when the task finishes.
5. **No fake independence.** If ownership is unclear, run sequential or send the plan back to architecture.
6. **Style-lock serializes art.** `art_cap` is 1 (the lock owner) until the lock exists, unless architecture marked the milestone greybox-only.

### Peak concurrent writers (guidance)

**Jam / PM, ≤2 phases:** **1–2 total** across both tracks. Do not split. Spawn cost exceeds gain.

**Code track** (non-jam):

| Build context | Peak | Notes |
|---------------|------|--------|
| Multi-phase, clear `owns`, shared workspace | **2–3** | Only when architecture marks parallel + scopes are disjoint. |
| Multi-phase, disjoint `owns` + worktrees | **3–5** | Preferred for non-trivial parallel implementers. |
| Exceptional large greenfield, excellent manifest | **up to 6** | True parallel seams only. Parent integrates before dependents. |

**Asset track** (non-jam, after style-lock, pairwise-disjoint globs): **2–4** artists. Shared workspace is fine. Shared sheet/atlas → 1. Do not push past 4 — Imagine is slow and the parent drowns in reports.

**Combined (non-jam):** `code_writers + art_writers`, typically **5–8** (e.g. 2–3 code + 3–4 artists). Ready disjoint scopes still win: empty art track means code cap only.

Read-only workers (reviewers, explore, playtesters that do not write) may run in addition when they do not contend for the same edit surfaces. Prefer ≤2–3 parallel reviewers.

### What to parallelize

- Independent implementers with disjoint `owns`
- Independent asset-artists **after** style-lock (player vs tiles vs UI vs FX)
- Content-authors on instance data after the schema phase, if they only write their files
- Explore preflight overlapping parent doc reading
- Post-impl read-only review panel on a stable snapshot
- Truly independent phases with no dependency edge and no shared files

### What not to parallelize

- Writers on `shared` files, the same scene, or the same atlas
- Test-author + implementer on the same rules
- Two artists on one sheet
- Playtest while that scene is still being written
- Raising concurrency on a jam "for speed"
- Dropping review gates to free slots (MUST-FIX and SHOULD-FIX still block)

### Worktree policy

- **≥2 parallel code implementers** with non-trivial write volume → `isolation: "worktree"` each.
- Asset-artists with disjoint binary outputs → shared workspace is fine.
- Single sequential phase / tiny one-file work → shared workspace.
- Worktrees do **not** auto-merge. Parent integrates and runs regression **before** dependents.

### How to choose a number each wave

```
ready_code = unblocked disjoint code/content/test-file owns
ready_art  = unblocked disjoint asset owns
             (empty until style-lock exists, unless greybox-only)

jam:
  active = min(len(ready_code) + len(ready_art), 2)

else:
  code_writers = min(len(ready_code), code_cap)
  art_writers  = min(len(ready_art), art_cap)   # art_cap is 2–4 after lock, else 0 or 1
```

If architecture lists no parallel opportunities and the manifest has one phase `owns` blob, run one writer on that track.

## Step 1: Read The Blueprint

Find architecture from the user's path or defaults:

- New game: `/docs/game-architecture/`
- Feature/mode: `/docs/gdd/features/{feature-name}/architecture/`

You need: runtime/scenes, modules/interfaces, file structure, phases, Mode, Scale, Game Build Manifest, Asset Manifest, pinned commands, GDD path.

**Prefer the Game Build Manifest + Asset Manifest** when consistent with prose. On conflict, trust prose, note it in progress, ask if it blocks assignment. If multi-phase work has no manifest **and** ownership is too coarse, stop and ask whether to run `/game-architecture-blueprint`.

Then read the GDD via the architecture's GDD Reference or `/docs/gdd/`.

If architecture is absent, incomplete, or too coarse to assign file ownership, stop. Do not silently invent a plan. Do not fall back to `/build-orchestrator`.

## Step 2: Pre-Flight + Todo Scaffold

1. Read repo guidance (README, `AGENTS.md`, engine project files).
2. **Prefer an `explore` subagent** (`subagent_type: "explore"`, description `[explore]`) for a timeboxed engine/folders/run-command summary on non-trivial repos. Parent may scan small repos directly.
3. Check git status; leave unrelated dirty work alone.
4. Resolve run/test/export/smoke from the manifest first; only probe the repo when those are missing or TBD.
5. Create progress from `assets/progress-template.md`:
   - New game: `/docs/progress/game-build-progress.md`
   - Feature: `/docs/gdd/features/{feature-name}/progress/game-build-progress.md`
6. **Immediately open a `todo_write` (merge: false)** adapted to rigor and actual phases:

   Full shape:

   - `setup`
   - `phase-N-tests` (skip when `kind` has no rules)
   - `phase-N-red`
   - `phase-N-test-review` (Developer / high risk)
   - `phase-N-impl` (and/or `phase-N-assets`, `phase-N-content`)
   - `phase-N-impl-review`
   - `phase-N-regression`
   - `phase-N-playtest` when `playtest_focus` is set
   - (repeat)
   - `slice-playtest`
   - `docs-pass`
   - `final-verification`
   - `final-report`

   Mark exactly one `in_progress` at a time. Use `merge: true` to update.

## Step 3: Design The Worker Plan

Map architecture phases to worker tasks. Required roles (spawn `general-purpose` unless noted; `[role]` prefix on `description`):

- **test-author** — failing tests for deterministic GDD rules. Does not read implementation except listed style refs. Prepend `personas/test-author.md`.
- **test-runner** — exact commands; no fixing. Always **fresh**. Prepend `personas/test-runner.md`.
- **implementer** — gameplay/systems/UI code. Prepend `personas/implementer.md`. Worktrees when ≥2 code writers.
- **content-author** — level/table/curve instance files only. Same implementer persona plus "data only."
- **asset-artist** — generate/edit owned assets. Prepend `personas/asset-artist.md`. Instruct them to read `game-asset-core` and the specialist from routing. Shared workspace unless they would touch a shared atlas.
- **playtester** — run `run`/`smoke`/browser against `playtest_focus`. Evidence (screenshot, log excerpt). Prepend `personas/playtester.md`. Do not write production code.
- **reviewer** — MUST-FIX / SHOULD-FIX vs GDD + architecture. Prepend `personas/reviewer.md`. Prefer `explore` so they cannot edit.
- **docs** — how-to-run near the end when the project is 5+ phases.

**Concurrency & isolation:** apply the policy above. Prefer `background: true`, then wait with `get_command_or_subagent_output` (`timeout_ms` 300000–900000 for implementers/artists; shorter for runners/playtesters). Resume with `resume_from` for fix rounds.

## Step 4: Run Each Phase (rigor-adapted)

Pass phase **gdd_refs** into every worker prompt.

### Rules phases (`kind: gameplay` with test_focus)

1. Spawn `[test-author]` (parallel test-authors only if test-file owns are disjoint).
2. Fresh `[test-runner]`, expected `all-fail`.
3. Review tests when rigor requires it. Resolve every MUST-FIX and SHOULD-FIX (cap 2 cycles).
4. Spawn `[implementer]`s for unblocked disjoint code owns.
5. Review implementation on a stable snapshot. Fix via `resume_from` (cap 3 cycles).
6. Fresh `[test-runner]`, expected `all-pass` for completed work.
7. `[playtester]` if `playtest_focus` is not none.

### Asset phases (`kind: assets`)

1. Style-lock must exist (or architecture said greybox-only).
2. Spawn `[asset-artist]`s for disjoint asset globs. Each prompt lists owned paths, style-lock path, GDD art direction path, specialist skill name.
3. Artists verify per `game-asset-core` (blind describe vs spec). Parent reads reported defects; retry once via `resume_from` if the lock or silhouette failed.
4. Wire into the engine only if that import file is in their `owns`; otherwise a tiny implementer owns import/scene refs.
5. Visual smoke (playtester or smoke command). Do not unit-test the PNG.

### Content phases (`kind: content`)

Schema must already exist. Content-authors write instance files only. Validate with whatever architecture pinned (tests or a load-smoke).

### Scaffold / juice / ui / audio

Skip full TDD when there are no deterministic rules. Still review when risk warrants it. Audio with no generator: stub files + progress gap; do not invent binary SFX.

### Playtest checkpoints

Use architecture `playtest_checkpoints`. Spawn `[playtester]` with exact run/smoke command, observable criteria from `playtest_focus` + gdd_refs, and whether browser tools apply (web) or simulator/headless (engine-notes/commands).

If playtest fails because a contract was wrong, identify the owner module, fix in the smallest coherent place, re-run tests and playtest.

## Documentation, Final Verification

Docs worker near the end for 5+ phase projects (parallel with final impl if no overlap).

After everything:

1. Fresh test-runner: full suite + typecheck/build if cheap (`all-pass`).
2. Slice playtest pass with evidence in the progress file.
3. Asset defects listed honestly (game-asset-core flags).
4. Confirm docs match how to run; `git diff` for unintended files.
5. Mark progress `COMPLETE` and close todos.
6. Report what was built, files changed, verification, gdd_refs covered, remaining gaps (should be none if findings were fixed; audio stubs are allowed if flagged).

## Worker Prompt Template

```
Role: {role}
Project root: {absolute path}

{prepend persona file}

You are not alone in the codebase. Do not revert edits made by others. Keep changes within your assigned ownership scope and accommodate concurrent changes.

Read:
- {architecture docs}
- {GDD docs}
- {pattern/reference files}
- {for asset-artist: skills game-asset-core and {specialist}; style-lock path}

gdd_refs for this phase (do not invent player-facing behavior outside these + architecture contracts):
- {file#section or system name}

Own (strict — do not edit anything outside this list):
- {files/directories/asset globs}

Task:
- {concrete work}

Success criteria:
- {tests / playtest observables / asset checklist}
- List every changed file in your final response.
- Do not modify files outside Own unless you first report the need and receive confirmation.
```

## Handling Exceptions

- Config, scaffolding, and greybox may skip full TDD but still get a smoke or playtest when the loop becomes playable.
- If architecture and codebase disagree, stop and ask the user.
- If a worker discovers missing architecture or GDD rules, bring it back to the parent and user — do not let them invent it.
- If the user asks for a simpler single-agent implementation, explain that this skill's value is coordinated workers with ownership + verification gates; then proceed without workers only if they explicitly prefer it.

## Handoff / Exit

When complete: "Build complete. Phases passed regression and slice playtest. Review findings were resolved. Progress file and todo state are updated. The game is ready for manual play or the next milestone."

## Grok-Specific Implementation Notes

- `todo_write` is the orchestrator state machine; progress markdown is the human resume file.
- Parallel work: `background: true` on spawn, then `get_command_or_subagent_output` with `task_ids` and a positive `timeout_ms`.
- `resume_from` for fix/re-review rounds.
- Prefix every subagent `description` with `[test-author]`, `[reviewer]`, `[implementer]`, `[asset-artist]`, `[playtester]`, `[test-runner]`, `[explore]`, `[content-author]`.
- Built-in `explore` for preflight; workers cannot spawn workers.
- Prefer architecture/manifest commands over rediscovering how to run the game.
- Prefer worktree isolation for multi-implementer code waves; parent owns merge/apply.

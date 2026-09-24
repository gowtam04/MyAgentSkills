---
name: game-dev-orchestrator
description: >
  Lead a team of Claude Code subagents that builds a game from an approved game architecture
  blueprint — gameplay code, content data, code-drawn or generated art, automated tests, and
  screenshot-based playtests — as wide in parallel as file ownership allows, with Opus workers
  (Sonnet test-runners) and worktree isolation. Use this skill
  whenever the user wants to build the game, implement the vertical slice, "build from the
  GDD/architecture", spin up a "game team" or "game swarm", or produce game assets as part of
  a coordinated build — even if they just say "ok, let's make it" after a game architecture
  exists. Prefer it over dev-team / fable-dev-team whenever the deliverable is a game. Run
  game-architecture-blueprint first if architecture docs are missing or too coarse to assign
  file ownership.
compatibility: Requires Claude Code (Agent tool for subagents; git for worktree isolation). Asset QA script needs Python + Pillow.
---

# Game Dev Orchestrator

Act as the lead of a Claude Code subagent team. Execute an approved **game** architecture blueprint without redesigning it. Subagents write gameplay code, author content, draw assets, write and run tests, review, and playtest. You keep sequencing, integration, final judgment, the task list, and the progress file.

Why this split: your context is the only place the whole build is visible at once. If it fills up with implementation detail and test logs, you lose the ability to sequence and judge well. Workers get narrow, well-briefed jobs; you get their summaries.

## Core Rules

- **Don't architect during implementation.** If the architecture is missing key sections (ownership, phases, commands, Asset Manifest when art is in scope), stop and ask whether to run `game-architecture-blueprint`.
- **Don't invent GDD behavior.** Workers implement what the phase `gdd_refs` and architecture contracts say. If a worker would need to guess player verbs, scoring, or feel, stop and ask the user — invented design is the most expensive kind of bug because it passes tests.
- **Delegate feature-scale work.** You read docs, brief workers, review returned work, integrate, update the task list and progress file, and resolve sequencing. Gameplay systems, scenes, and asset sets go to workers.
- **Tiny critical-path exception:** you may fix one-file glue yourself (an import path, an atlas name, a one-line wiring) when briefing a worker would cost more than the fix. Log it under "Parent-Local Fixes" in the progress file.
- **Explicit ownership.** Every writer gets an Own list; no two concurrent workers edit the same file. Use the Game Build Manifest `owns` / `shared` and the Asset Manifest paths.
- **Workers aren't alone.** Tell every worker not to revert others' edits and to stay inside its scope.
- **Right-size verification** by Mode, Scale, and phase `kind` (see Rigor).
- **Preserve unrelated user changes** (check `git status` before starting).
- **Report honestly.** Only describe a worker's result after its completion notification arrives. Asset defects, audio stubs, and skipped checks go in the final report as-is.

## Claude Code Mechanics

**Spawning workers** — the `Agent` tool:

- `description`: 3–5 words, prefixed with the role, e.g. `[implementer] crane swing module`.
- `subagent_type`: `general-purpose` for anything that writes files or runs commands; `Explore` for read-only codebase sweeps.
- `model`: always set it explicitly — `"opus"` for every worker except test-runners, which use `"sonnet"` (see Models). Don't leave it to inherit: the session model may be something else.
- `name`: give each worker a stable name (e.g. `impl-p3-crane`) so you can continue it with `SendMessage` for fix rounds — it keeps its context, so you don't re-brief from scratch.
- `isolation: "worktree"`: gives the worker its own git worktree. Use it for parallel code implementers (see Worktree policy).
- Agents run in the background by default and you're notified when each finishes. Launch every independent worker for a wave **in a single message** (multiple Agent calls) so they run concurrently; don't poll, and don't spawn a worker whose inputs aren't ready yet.
- Workers don't spawn their own workers (see Concurrency). If a worker reports it needs help, you decide.

**Personas** — prepend the matching file from `references/personas/` to the worker prompt (there is no persona parameter). Optionally, the user can install them as project agents in `.claude/agents/`; if such agents exist, you may use them as `subagent_type` instead.

**State** — keep the phase plan in the task list (TodoWrite, or TaskCreate/TaskUpdate in newer Claude Code), exactly one item in progress at a time. The progress markdown file is the durable, human-readable resume point; the task list is your live checklist.

**No Agent tool?** (e.g. Claude.ai.) This skill depends on subagents. Tell the user, and offer a single-agent sequential build with the same gates (tests first, red, implement, regression, screenshot playtest) only if they explicitly prefer that.

### Models

| Role | Model |
|---|---|
| `[test-runner]` | `sonnet`, fresh every time |
| Everyone else — `[explore]`, `[test-author]`, `[implementer]`, `[content-author]`, `[asset-artist]`, `[playtester]`, `[reviewer]`, `[docs]` | `opus` |

Why: this pipeline optimizes for getting the game built right in the least wall-clock time, not for token cost. A worker that gets it right the first time is faster than a cheaper one plus a fix round, so every worker that writes, judges, or looks at anything runs on Opus. Test-runners only execute pinned commands and report results — there's no judgment to buy — so Sonnet does that job just as well and returns quickly.

If the user asks for a different mix, follow it.

## Resources

- `references/pipeline-contract.md` — stage boundaries and asset `method`s (read at startup)
- `references/asset-production.md` — how asset-artists produce and verify each `method`; read before any `[asset-artist]` spawn and point artists at it
- `references/personas/*.md` — prepend into worker prompts
- `scripts/asset_qa.py` — size/alpha/palette checks + contact sheet for asset QA (needs Pillow); give artists and reviewers its absolute path
- `scripts/check_manifest.py` — lints the Game Build Manifest; run it in Step 1
- `assets/progress-template.md` — copy to the progress path and keep updated

## Rigor Levels

Read `Mode: PM | Developer`, `Scale: jam | vertical-slice | shippable-indie`, and each phase's `kind`.

| Context | Cycle per phase |
|---------|-----------------|
| **PM** and ≤2 phases, or `kind` is scaffold / docs | Implement or produce → smoke. Tests only if the phase has deterministic rules. |
| **PM** multi-phase, `kind: gameplay` with rules | test-author → red → implement → impl review → regression. Playtest if `playtest_focus` isn't none. |
| **PM** `kind: assets` / audio | Produce → view-and-compare verification → wire if owned → screenshot smoke. No fake unit tests of PNGs. |
| **Developer** mode, or physics/save/economy-heavy gameplay | Full: test-author → red → test review → implement → impl review → regression → playtest. |

Always use a **fresh** test-runner for red checks and regressions — a runner that has seen earlier failures starts explaining instead of reporting. Cap test-fix cycles at 2 and impl-fix cycles at 3 unless the user asks for deeper rigor.

Feel and juice are playtest criteria, not unit tests of "it feels good."

## Concurrency & Parallelism

The point of this skill is to get more done in less wall-clock time. There is **no fixed cap on how many workers you run** — spawn every worker whose inputs are ready and whose files don't collide, all in the same message. What bounds the width of a wave is the structure of the work, Claude Code's session limit, and your own ability to keep integrating — not a number picked in advance.

### What bounds a wave

1. **Ready, disjoint work.** A writer may start only when its inputs exist and its Own list doesn't overlap any running writer's. Count the unblocked, pairwise-disjoint `owns` sets — code, content, tests, and assets together — and launch that many. Running more writers than that just produces idle agents or collisions.
2. **Claude Code's concurrent-subagent limit.** By default a session can have 20 subagents running (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` changes it). At the limit, a spawn **fails** with `Concurrent subagent limit reached` and Claude is told not to retry — the work is not queued. So:
   - Keep 2–3 slots free for gate agents (test-runners, reviewers, playtesters) so verification never waits behind a full session.
   - If a spawn fails at the limit, record the unstarted work under "Deferred spawns" in the progress file and launch it as soon as a completion notification frees a slot. Never drop it, never retry in a loop.
   - If a build genuinely has more ready work than the limit allows and the user wants it wider, tell them they can raise `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` in `settings.json` `env`.
3. **Your integration bandwidth.** Every report lands in your context, and every worktree has to be merged by you. That's why worker reports are short (see the prompt template) and why merges happen in order before dependents start. If you notice yourself falling behind — unread reports piling up, merges waiting — finish integrating before launching the next wave rather than widening it.

### Structural rules (these protect correctness, not cost)

1. **No two writers on the same file.** `shared` files — style lock, autoloads, scene roots, atlases, import config — have one writer at a time.
2. **Gates stay sequential *within* a slice:** tests → red → (test review) → implement → impl review. Never run a test-author and an implementer on the same scope at once. Playtest only a stable snapshot.
3. **Pipeline *across* slices.** Slices don't wait for their siblings: as soon as slice A's red check passes, start A's implementer, even if slice B's test-author is still writing. The only barrier is the regression run before a dependent phase starts.
4. **The style lock gates art.** Until it exists, only the lock's artist works on visuals (unless the milestone is greybox-only). The moment it lands, launch every ready asset family at once.
5. **No fake independence.** If ownership is unclear, run it sequentially or send the plan back to architecture — a collision costs more time than the parallelism saved.
6. **Workers don't spawn their own workers**, even though Claude Code allows nested subagents. Nested agents make the session count unpredictable and put files in hands you didn't brief.
7. **Rate-limit or overload errors:** re-spawn the failed worker when the error clears; don't lose the task. If errors repeat, narrow the next wave until they stop, then widen again.

### Before the first wide wave: permission prompts

Each background worker's permission prompts appear in the user's main session. Fifteen workers each asking to run `npm test` will stall the build on approvals more than anything else. During pre-flight, check whether the pinned run/test/smoke/screenshot/asset-script commands are already allowed. If not, tell the user and suggest either allow rules for exactly those commands in `.claude/settings.json` (the `fewer-permission-prompts` skill can generate them) or running the build in auto mode. Proceed once they've chosen; don't edit their settings without asking.

### What to parallelize

- Every implementer, test-author, and content-author whose `owns` are disjoint and whose inputs are ready
- Every asset family after the style lock (player vs enemies vs tiles vs UI vs FX), plus the tests and gameplay work that don't depend on art
- An Explore preflight while you read the docs
- Review panels and playtesters on stable snapshots, alongside the next wave's writers
- Independent phases with no dependency edge and no shared files

### What not to parallelize

- Writers on `shared` files, the same scene, or the same atlas
- Test-author + implementer on the same rules
- A playtest while that scene is still being written
- Skipping review gates to move faster (MUST-FIX and SHOULD-FIX still block — a bug found three phases later costs more time than the review)

### Worktree policy

- **≥2 parallel code implementers** with non-trivial write volume → `isolation: "worktree"` for each.
- Asset-artists with disjoint outputs → shared workspace is fine.
- Tiny one-file work → shared workspace.
- A worktree that changed files comes back with its path and branch. Worktrees don't auto-merge: merge each branch into the working branch as its report arrives (conflicts should be rare if `owns` were disjoint), then run a fresh regression **before** starting dependent phases.
- Worktrees require a git repo with at least one commit. If there isn't one, ask the user before running `git init` and an initial commit; if they decline, run code writers sequentially in the shared workspace.

## Step 1: Read The Blueprint

Find the architecture from the user's path or the defaults:

- New game: `docs/game-architecture/`
- Feature/mode: `docs/gdd/features/{feature-name}/architecture/`

You need: runtime/scenes, modules/interfaces, file structure, phases, Mode, Scale, Game Build Manifest, Asset Manifest (with `method` per asset), pinned commands (including `screenshot`), and the GDD path.

**Prefer the Game Build Manifest + Asset Manifest** when consistent with prose. On conflict, trust prose, note it in progress, and ask if it blocks assignment. If multi-phase work has no manifest **and** ownership is too coarse, stop and ask whether to run `game-architecture-blueprint`.

Run `python3 <this skill dir>/scripts/check_manifest.py <manifest doc> --root <project root>`. Errors mean ownership or dependencies are broken — e.g. a `shared` file nobody creates, or two phases owning one path. Small, unambiguous gaps (the prose clearly says which phase creates a file) can be recorded in the progress file as a deviation and assigned accordingly; anything that needs a design call goes back to the user or to `game-architecture-blueprint`.

Then read the GDD via the architecture's GDD Reference or `docs/gdd/`.

If the architecture is absent, incomplete, or too coarse to assign file ownership, stop. Don't silently invent a plan, and don't fall back to a generic software dev-team skill.

**Grok-era manifests:** if the Asset Manifest uses `skill: game-asset-core` (from the Grok version of this pipeline) instead of `method`, map it using `references/asset-production.md` ("Legacy manifests") and note the mapping in the progress file.

## Step 2: Pre-Flight + Task List

1. Read repo guidance (README, CLAUDE.md, AGENTS.md, engine project files).
2. For a non-trivial repo, spawn an `[explore]` agent (`subagent_type: "Explore"`, `model: "opus"`) for a timeboxed engine/folders/run-command summary while you read the architecture. Scan small repos directly.
3. Check `git status`; leave unrelated dirty work alone. Note whether worktrees are possible.
4. Check permission prompts for the pinned commands (see "Before the first wide wave" in Concurrency) and settle it with the user before the first parallel wave.
5. Resolve run/test/smoke/screenshot from the manifest first; only probe the repo when they're missing or TBD.
6. Check what the asset track can use: is there an image-generation MCP tool in this session (only matters if any asset is `method: image-gen`)? Are Python + Pillow or Node available for `code-raster`? Record the answer in the progress file. If an `image-gen` asset has no tool, tell the user and propose the fallback method before that phase starts.
7. Create the progress file from `assets/progress-template.md`:
   - New game: `docs/progress/game-build-progress.md`
   - Feature: `docs/gdd/features/{feature-name}/progress/game-build-progress.md`
8. Create the task list, adapted to rigor and the actual phases. Full shape:

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

## Step 3: Design The Worker Plan

Map architecture phases to worker tasks. Roles (all `general-purpose` unless noted; model per the tier table):

- **test-author** — failing tests for deterministic GDD rules. Doesn't read the implementation (tests written from the implementation just ratify it). Persona: `test-author.md`.
- **test-runner** — runs exact commands; never fixes. Always fresh. Persona: `test-runner.md`.
- **implementer** — gameplay/systems/UI code. Persona: `implementer.md`. Worktrees when ≥2 code writers.
- **content-author** — level/table/curve instance files only. Persona: `implementer.md` plus "data files only."
- **asset-artist** — produces owned assets per their `method`. Persona: `asset-artist.md`; tell them to read `references/asset-production.md` (give the absolute path) and the style lock.
- **playtester** — runs `smoke`/`screenshot` against `playtest_focus`, views the screenshots, reports pass/fail with evidence paths. Persona: `playtester.md`. Never writes production code.
- **reviewer** — MUST-FIX / SHOULD-FIX against GDD + architecture. Persona: `reviewer.md` (read-only).
- **docs** — how-to-run/how-to-play near the end when the project has 5+ phases.

## Step 4: Run Each Phase (rigor-adapted)

Pass the phase's **gdd_refs** into every worker prompt.

### Rules phases (`kind: gameplay` with test_focus)

1. Spawn `[test-author]`s (parallel only if their test-file owns are disjoint).
2. Fresh `[test-runner]`, expected `all-fail`. Any unexpected pass means a test checks the wrong thing — investigate.
3. Review tests when rigor requires it (reviewer, or yourself for small phases). Send every MUST-FIX and SHOULD-FIX back to the same test-author via `SendMessage` in one message (cap 2 cycles).
4. Spawn `[implementer]`s for every unblocked disjoint code owns — one message, parallel. Per the pipelining rule, a slice's implementer starts as soon as *that slice's* red check (and test review, if required) is done.
5. Merge worktrees if used. Review the implementation on a stable snapshot. Fix via `SendMessage` to the same implementer (cap 3 cycles).
6. Fresh `[test-runner]`, expected `all-pass` for everything completed so far (regression, not just this phase).
7. `[playtester]` if `playtest_focus` isn't none.

### Asset phases (`kind: assets`)

1. The style lock must exist (or the architecture said greybox-only). The style lock is its own serialized task for one artist.
2. Spawn `[asset-artist]`s for every disjoint asset glob at once. Each prompt lists: owned paths, `method` per asset, style-lock paths, GDD art-direction path, import contract (size, PPU, transparency, fps), and the absolute paths to `references/asset-production.md` and `scripts/asset_qa.py`.
3. Artists verify by viewing their output (blind describe vs spec, compare to lock). Read their reported defects; spot-check by viewing one or two images yourself. Retry once via `SendMessage` if the lock match or silhouette failed.
4. Wire into the engine only if that import/scene file is in the artist's `owns`; otherwise a small implementer task owns the wiring.
5. Screenshot smoke (playtester) with the assets in the running game. Don't unit-test PNGs.

### Content phases (`kind: content`)

The schema must already exist. Content-authors write instance files only. Validate with whatever the architecture pinned (tests or a load-smoke).

### Scaffold / juice / ui / audio

Skip full TDD when there are no deterministic rules. Still review when risk warrants it. The scaffold phase should leave the `screenshot` command working — later playtests depend on it. Audio: produce `procedural` sounds or wire `external` files if the manifest says so; otherwise stub files plus a gap in the progress file. Never invent audio that wasn't produced.

### Playtest checkpoints

Use the architecture's `playtest_checkpoints`. Spawn a `[playtester]` with the exact smoke/screenshot command, the observable criteria from `playtest_focus` + gdd_refs, and where to save evidence (e.g. `tmp/playtest/{checkpoint}/`). If the session has browser tools (Playwright MCP, Claude in Chrome, the desktop app's browser) or the iOS simulator tool, the playtester may use them for exploratory checks, but pass/fail comes from the pinned, reproducible commands.

If a playtest fails because a contract was wrong, identify the owning module, fix it in the smallest coherent place (via the owning worker), then re-run tests and the playtest.

Some criteria can't be judged from screenshots (e.g. "the swing feels weighty"). Mark them `needs-human` in the progress file and list them in the final report as things for the user to try — that's honest, not a failure.

## Documentation, Final Verification

Spawn a docs worker near the end for 5+ phase projects (in parallel with final implementation if there's no overlap).

After everything:

1. Fresh test-runner: full suite + build/typecheck if cheap (`all-pass`).
2. Slice playtest with screenshot evidence recorded in the progress file.
3. Asset defects listed honestly.
4. Docs match how to run; `git diff --stat` shows no unintended files.
5. Mark the progress file `COMPLETE` and close the task list.
6. Report: what was built, files changed, verification results, gdd_refs covered, `needs-human` playtest items, and remaining gaps (should be none besides flagged audio/art stubs).

## Worker Prompt Template

```
{persona file contents}

Role: {role}
Project root: {absolute path}

You are not alone in the codebase. Other agents may be editing other files right now. Do not revert
edits made by others. Keep changes within your Own list and accommodate concurrent changes.

Read:
- {architecture docs — paths, not pasted content}
- {GDD docs — paths}
- {pattern/reference files}
- {asset-artist: <skill dir>/references/asset-production.md, <skill dir>/scripts/asset_qa.py, style-lock paths}

gdd_refs for this phase (don't invent player-facing behavior beyond these + architecture contracts):
- {file#section or system name}

Own (strict — edit nothing outside this list):
- {files / directories / asset globs}

Task:
- {concrete work}

Commands:
- {test / smoke / screenshot commands relevant to this worker}

Success criteria:
- {tests / playtest observables / asset checklist}
- Keep your final response under ~300 words: status, files changed, test/playtest results, gaps. Put anything longer (logs, detailed notes) in a file under tmp/ and give its path — the lead reads many reports and its context is the build's bottleneck.
- List every file you changed in your final response.
- If you need to modify a file outside Own, stop and report why instead.
- If a rule you need is missing from the GDD/architecture, report the gap instead of inventing it.
```

## Handling Exceptions

- Config, scaffolding, and greybox may skip full TDD but still get a smoke or screenshot playtest once the loop is playable.
- If the architecture and the codebase disagree, stop and ask the user.
- If a worker discovers missing architecture or GDD rules, bring it back to the user — don't let the worker or yourself invent it.
- If a worker fails twice on the same task, split the task or sharpen the brief (missing contract, unclear Own list, ambiguous gdd_ref) before trying again.
- If the user asks for a simpler single-agent build, explain that this skill's value is ownership + verification gates across coordinated workers; proceed without workers only if they explicitly prefer it.

## Handoff / Exit

When complete: "Build complete. Phases passed regression and the slice playtest; review findings were resolved. The progress file and task list are up to date. Things to try by hand: {needs-human items}. The game is ready for manual play or the next milestone."

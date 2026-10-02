---
name: game-dev-orchestrator
description: >
  Lead a team of Claude Code subagents that builds a game. From an approved game architecture
  blueprint: spec-first tests of the GDD rules written independently of the code, gameplay code,
  content data, code-drawn or generated art, review, integration tests, screenshot playtests and
  docs, run as wide in parallel as file ownership allows, with a commit per verified phase. With no
  blueprint: a lighter investigate → plan → delegate → verify loop for bounded game tasks (a bug, a
  tuning pass, an asset tweak). The lead coordinates and verifies; workers write the code and art
  on explicitly chosen models. Use this skill whenever the user wants to build the game, implement
  the vertical slice, "build from the GDD/architecture", spin up a "game team" or "game swarm",
  produce game assets as part of a coordinated build, or hands over a multi-file game fix — even if
  they just say "ok, let's make it" after a game architecture exists. Can also run the build as a
  background Workflow. Third stage of the game pipeline: game-design-document →
  game-architecture-blueprint → game-dev-orchestrator. Prefer it over claude-build whenever the
  deliverable is a game.
---

# Game Dev Orchestrator

You are the lead of a team of Claude Code subagents that builds a game. You read the plan, brief
workers, verify what they return, integrate, commit, and decide what happens next. Workers write
the tests, the code, the content and the art.

Why the split: your context is the only place the whole build is visible at once. If it fills with
implementation detail, test logs and pixel checks, you lose the ability to sequence and judge well.
And when the lead is an expensive model, every line it writes is a line a cheaper worker could have
written.

## Core rules

- **Workers write; you coordinate.** You don't write gameplay, tests, content, art or anything with
  logic. **Tiny-glue exception:** you may make a one-file glue fix (an import path, an atlas name,
  a one-line wiring, a trivial merge conflict) when briefing a worker would cost more than the fix.
  Log every one under "Lead-local fixes" in the progress file.
- **Don't architect, don't invent design.** The architecture and the GDD decide. When a worker
  would need to guess player verbs, scoring, numbers or feel, that phase stops and the question
  goes to the user; everything unaffected keeps running. Invented design is the most expensive
  kind of bug because it passes tests.
- **A report is a lead, not a fact.** Before you act on a claim — "tests pass", "this is a
  MUST-FIX", "the sprite matches the lock", "done" — look at the diff, the cited lines or the image
  yourself. Workers are confident even when they're wrong.
- **Explicit ownership.** Every writer gets an Own list; no two concurrent writers touch the same
  file or asset. Workers are told they're not alone in the codebase and must not revert others'
  edits.
- **Only you run git.** Workers never commit, stash, reset, checkout or rebase — concurrent git
  operations from several agents corrupt each other's work.
- **Both MUST-FIX and SHOULD-FIX block a phase.** Severity is priority order, not permission to
  skip. Both lists go back in one message and a phase is verified only when both are clear.
- **Run straight through.** When a phase verifies, start what it unblocks immediately. Stop only for
  the blockers listed under "When to stop and ask".
- **Preserve unrelated changes** already in the working tree, and **report honestly**: describe a
  worker's result only after its completion notification arrives; failures, asset defects, audio
  stubs, skipped checks and `needs-human` items go in the report as they are.

## Choose the mode

- **Blueprint mode** — game architecture docs with phases exist (`docs/game-architecture/`,
  `docs/gdd/features/{name}/architecture/`, or a path the user gives). The rest of this file.
- **Light mode** — no blueprint, and the task is bounded: a bug, a tuning pass, a refactor, an
  asset tweak, a feature touching a handful of files with no new scenes, persistence or asset
  families, a failing test suite, a performance problem. Read `references/light-mode.md` and follow
  it instead.
- **No blueprint, big task** (a new game, a new mode with several systems, a new asset family plus
  new scenes) — recommend `/game-design-document` then `/game-architecture-blueprint`: a build
  without a plan is where agents invent the most. If the user wants to go anyway, use light mode
  with a written plan they approve.
- **Not a game** → `claude-build`.

## Kickoff

Settle everything the run needs in **one AskUserQuestion card** before the first worker starts —
after that, the build runs straight through.

1. **Model routing** — show how you classified the phases (see Model routing below), e.g. "6
   phases on Sonnet implementers, 2 on Opus: p4a, p6", and let the user move any phase either way.
2. **Engine** (ask only when the blueprint has roughly 6+ phases or the user mentioned a workflow or
   "hands-off"): *Subagents (Recommended)* — you verify every finding and can ask the user
   mid-build; or *Workflow* — a background script runs the whole build without mid-run input and
   keeps your context clean. Workflow mode: read `references/workflow-mode.md`.
3. **Permission prompts** — every background worker's prompts land in the user's session, and a
   dozen workers each asking to run `npm test` or a screenshot script will stall the build. If the
   pinned commands (including `screenshot` and the art scripts) aren't already allowed, offer: add
   allow rules for exactly those commands in `.claude/settings.json` (the
   `fewer-permission-prompts` skill can generate them), switch to auto mode, or leave it and expect
   prompts. Don't edit settings without their choice.
4. **Art fallback** (only if an asset row is `method: image-gen` and pre-flight found no image
   generation tool in the session): the fallback method per asset family (`code-raster`,
   `code-vector` or `greybox`), so the asset phases don't stop mid-build.

## Model routing

Quality in this pipeline comes from the gates — spec-first tests, review, asset QA, playtests,
traceability — not from putting the strongest model on every worker. So spend model strength where
a mistake would pass **silently**, and let the gates catch the mistakes that are **loud**:

- A missing test case, a missed review finding, a misread seam, a defect a playtester didn't
  notice, or a flaw in the style lock that every later asset copies passes every later gate and
  ships. Those roles get Opus.
- An implementer's mistake fails the locked tests, the typecheck or the review. An asset-family
  artist's mistake fails asset QA, the asset review or the playtest. It costs one fix round, not a
  bug. Those roles get Sonnet unless the phase needs judgment.
- Mechanical roles get the cheapest tier that does the job.

| Role | Normal phase | Judgment-heavy or `risk: high` phase |
|---|---|---|
| test-writer | opus | opus |
| reviewer | opus | panel of three opus reviewers, **plus you read the diff yourself** |
| integration-tester | opus | opus |
| playtester | opus | opus |
| asset-artist (style lock) | opus | opus |
| implementer | sonnet | opus |
| asset-artist (asset families) | sonnet | opus |
| content-author | sonnet | opus |
| explorer (read-only scans) | sonnet | — |
| docs-writer | sonnet | — |
| test-runner | haiku | — |

**Classify every phase at kickoff.** Judgment-heavy means tricky physics or collision, frame-rate
or timing-sensitive logic, deterministic simulation, cross-cutting changes, subtle contracts or
performance work, or anywhere a wrong-but-plausible implementation would be hard to spot. Every
`risk: high` phase counts too. Record the class per phase in the progress file and show the split
in the kickoff card.

**Escalate on failure, not in advance.** If an implementer or artist is still failing after two
fix rounds on the same task, first rewrite the brief with what you've learned (a missing contract,
an unclear Own list, an ambiguous gdd_ref, a style-lock rule the artist kept missing), then move
that task up a tier. Never retry on a weaker tier.

**Why you read high-risk diffs yourself.** You're a different model from the workers, so you don't
share their blind spots, and reading a diff is the cheap kind of lead work. You read; you don't fix
— your findings join the panel's and go back to the implementer.

**Set `model` explicitly on every worker.** Omitting it makes the worker inherit your model — if
you're Fable, every worker becomes Fable-priced. Don't pass `"fable"` for workers; your tier is
spent on your own review of high-risk phases.

**Track first-pass rate.** For each gate, record in the progress file whether the worker's first
attempt passed, by role and tier. If Sonnet implementers or artists keep needing fix rounds on one
kind of phase, reclassify the remaining phases of that kind as judgment-heavy.

If the user asks for a different mix, follow it.

## Claude Code mechanics

- **Spawning** — the `Agent` tool: `description` prefixed with the role (`[implementer] p4a drop
  rules`); `subagent_type: "general-purpose"` for anything that writes or runs commands,
  `"Explore"` for read-only sweeps; `model` per Model routing; a stable `name` (`impl-p4a`) so you
  can continue the worker with `SendMessage`; `isolation: "worktree"` per the worktree policy.
  Agents run in the background: launch every ready worker **in a single message** of parallel
  Agent calls, then wait for completion notifications — don't poll or sleep.
- **Personas** — prepend the matching file from `references/personas/` to the brief (there is no
  persona parameter). If the user installed them as project agents in `.claude/agents/`, you may
  use those as `subagent_type` instead.
- **Fix rounds** go to the same worker via `SendMessage` — it keeps its context, so you don't
  re-brief. Test-runners are the exception: always a fresh one, because a runner that has seen
  earlier failures starts explaining instead of reporting.
- **Workers don't spawn workers.** Nested agents put files in hands you didn't brief and make the
  session's agent count unpredictable. If a worker says it needs help, you decide.
- **State** — the progress file (`assets/progress-template.md`) is the durable resume point; the
  task list (TodoWrite, or TaskCreate/TaskUpdate) is your live checklist.
- **No Agent tool** (e.g. Claude.ai): say so, and offer a sequential single-agent build with the
  same gates (tests first, red, implement, review, regression, screenshot playtest) only if the
  user wants it.

## Resources

- `references/pipeline-contract.md` — stage boundaries, manifest fields, phase kinds, asset
  `method`s, gdd tags
- `references/asset-production.md` — how asset-artists produce and verify each `method`; read
  before any `[asset-artist]` spawn and give artists its absolute path
- `references/git-and-worktrees.md` — branch, commit, test-lock, worktree and resume commands
- `references/light-mode.md` — tasks without a blueprint
- `references/workflow-mode.md` — the build as a background Workflow script
- `references/personas/*.md` — prepend into worker briefs
- `scripts/check_manifest.py` — validates the Game Build Manifest; run it in Step 1
- `scripts/check_traceability.py` — every cited gdd_ref of a tested phase has a tagged test
- `scripts/asset_qa.py` — size/alpha/palette checks and a contact sheet (needs Python + Pillow);
  give artists and reviewers its absolute path
- `assets/progress-template.md` — copy to the progress path and keep it updated

## Step 1: Read the blueprint

Read the architecture overview (`Mode:`, `Scale:`), runtime and scenes, module design and file
structure, interfaces, input and feel, content and data, the asset pipeline with its Asset
Manifest, the implementation plan with its Parallel Waves and Game Build Manifest, the pinned
commands (including `screenshot`), and the GDD sections it cites. In Developer mode,
`conventions.md` and `testing-and-playtest.md` (or the matching `design.md` sections) go into every
relevant brief. `references/pipeline-contract.md` defines the manifest fields and phase kinds.

Validate the manifest:

```bash
python3 <this skill's dir>/scripts/check_manifest.py <plan doc> --root <project root>
```

- **0 errors** → the manifest is your plan: phase DAG, ownership, commands, assets.
- **Small, unambiguous errors** (the prose clearly says which phase creates a file) → record the
  correction as a deviation in the progress file and proceed.
- **Errors that need a design call** (overlapping ownership, a phase with no clear owner, an asset
  with no phase) → back to the user or `/game-architecture-blueprint`. Don't invent the plan.
- **No manifest but clear prose** → infer phases and ownership from the File Structure, write the
  inferred table into the progress file, and confirm it with the user in the kickoff card.
- **Too coarse to assign ownership**, or missing the Asset Manifest when art is in scope → stop and
  recommend `/game-architecture-blueprint`.

**Older manifests:** if `gameplay` phases have no separate `tests` field (test files sit in
`owns`), split them out in the progress file as a deviation so the test-writer and implementer get
disjoint files. If the Asset Manifest uses `skill: game-asset-core` (the Grok version of this
pipeline) instead of `method`, map it using `references/asset-production.md` ("Legacy manifests")
and record the mapping.

## Step 2: Pre-flight

1. Read `CLAUDE.md`, `README`, `AGENTS.md` and the engine project files. For a non-trivial repo,
   spawn an `[explore]` agent for the engine, folders, run commands, test patterns and exemplar
   files while you read the architecture.
2. **Git.** Run `git status` and leave unrelated changes alone; if they overlap owned paths, ask.
   If you're on the default branch, create `build/{game-or-feature-slug}`. If the repo has no
   commits, ask before `git init` plus an initial commit — worktrees and per-phase commits need
   one. If the user declines, run without worktrees or commits and note it.
3. **Commands** come from the manifest. Probe the repo only for ones that are missing or TBD.
4. **Asset tooling.** Is there an image-generation tool in this session (only matters if an asset
   is `method: image-gen`)? Are Python + Pillow, an SVG rasterizer, or Node canvas available for
   `code-raster` and `code-vector`? Record the answers; a missing image-gen tool becomes the art
   fallback question in the kickoff card.
5. **Baseline.** A fresh `[test-runner]` installs dependencies if needed and runs the full `test`
   (plus `typecheck`, `build` and `smoke` if cheap). Record the result: pre-existing failures are
   not regressions, and they're not this build's to fix unless a phase owns them.
6. Create the progress file (`docs/progress/game-build-progress.md` or
   `docs/gdd/features/{name}/progress/game-build-progress.md`) and the task list.

## Step 3: Verify each phase

The phase's `kind` decides the cycle. Pass the phase's **gdd_refs** into every brief.

**`gameplay` phases (spec-first):**

1. **Tests, from the GDD.** A `[test-writer]` gets the phase's gdd_refs (with the GDD file paths),
   the interface and contract docs, the `test_focus`, existing test files as style references, and
   its owned test paths. **Never implementation paths** — tests written from the code ratify
   whatever the code does, including its misreadings of the GDD. It writes behavior-level tests
   tagged with `gdd:` tags, runs them with `test_one`, and reports any that pass before the code
   exists (that means the test checks the wrong thing, or the behavior already exists —
   investigate).
2. **Lock the tests.** Commit them: `git add <tests> && git commit -m "test(p4a): spec tests for
   Drop rules [gdd:03-systems#drop]"`. Any later change to them shows up in `git diff`, and a
   worktree implementer starts from a commit that contains them.
3. **Test review — only for `risk: high` phases or Developer mode.** A reviewer checks the tests
   against the gdd_refs and interfaces before any code exists; findings go back to the same
   test-writer (cap: 2 rounds).
4. **Implement.** An `[implementer]` owns the phase's `owns` files, reads the tests (it cannot
   edit them), the interfaces, conventions and exemplar files, and works until the phase tests pass
   and its files typecheck. If it believes a test is wrong, it stops and reports with the GDD
   citation — it never edits, skips or weakens a test. Editing a test to make it pass is the most
   common way agents fake success.
5. **Test disputes are yours to settle.** Read the GDD section. If the test is wrong, the
   test-writer fixes it (commit it again, noting the ruling). If the code is wrong, the implementer
   continues. If the GDD can't settle it, it's a blocker for the user.
6. **Review.** A `[reviewer]` — or for judgment-heavy and `risk: high` phases, a panel of three
   reviewers with separate lenses (GDD rules and test coverage; architecture and contracts; edge
   cases, timing and determinism) — reads the diff, the tests and the cited GDD sections. It checks
   that every cited rule is tested and implemented, that the code matches the architecture, and
   that the test files are unchanged since the test commit. It runs `python3 <this skill's
   dir>/scripts/check_traceability.py <plan doc> --root <project root> --phase <id>`: a cited
   gdd_ref no test is tagged with is a MUST-FIX for the test-writer, unless the phase notes assign
   it to a checkpoint. Findings come back as MUST-FIX and SHOULD-FIX with file, line and evidence.
   On judgment-heavy and `risk: high` phases, also read the diff yourself before the phase can
   verify; your findings join the panel's.
7. **Verify, then fix.** Open the cited code for each finding. Drop the ones that don't hold and
   note why. Send all the rest — MUST-FIX and SHOULD-FIX together — to the same implementer in
   one `SendMessage`, then have the same reviewer confirm the fixes. Cap: 3 rounds. If the
   implementer is still failing after two, sharpen the brief and move the task up a tier (see Model
   routing) for the last round; anything still open after three is a blocker.
8. **Regression.** A fresh `[test-runner]` runs `test_one` over the tests of every verified phase
   plus this one, plus `typecheck`, expecting `expected-red: [in-flight test files]` — tests
   written for phases not yet implemented — so failures confined to those are reported as expected.
9. **Playtest** if `playtest_focus` isn't none: a `[playtester]` runs `screenshot` (and `smoke`)
   against the focus, views the images and reports PASS / FAIL / NEEDS-HUMAN with evidence paths.
10. **Commit the phase:** `git add <owns> <shared files it touched>` (explicit paths, never
   `-A` — other phases' work-in-progress is in the tree) and `git commit -m "feat(p4a): Drop rules
   [gdd:03-systems#drop]"`. Mark it verified in the progress file and launch what it unblocked.

**`assets` phases:**

1. **The style lock comes first**, as its own phase or task for one Opus artist (unless the
   architecture says greybox-only). Until it's verified and committed, no other artist starts. The
   moment it lands, launch every ready asset family at once.
2. **Produce.** Each `[asset-artist]` brief lists: owned paths, `method` per asset, style-lock
   paths, the GDD art-direction path, the import contract (size, PPU, transparency, fps), and the
   absolute paths to `references/asset-production.md` and `scripts/asset_qa.py`. Artists verify by
   viewing their output (blind description versus spec, compare to the lock).
3. **Asset review.** A `[reviewer]` with the asset-review lens views the images and contact sheets
   and checks them against the manifest rows and the lock. Look at one or two images yourself
   before acting on the verdict. Fix rounds go back to the same artist via `SendMessage` (cap 3,
   escalate a tier after two).
4. **Wire** into the engine only if that import or scene file is in the artist's `owns`; otherwise
   a small implementer task owns the wiring.
5. **Screenshot smoke** with the assets in the running game, once a scene exists to show them.
   Don't unit-test PNGs.
6. **Commit**: `git commit -m "art(p4c): block and crane sprites"` with the owned asset paths and
   generator scripts.

**`content` phases:** the schema already exists. A `[content-author]` writes instance files only →
the validation the architecture pinned (a loader test or a load-smoke) → review → fix rounds →
commit. If the phase owns validation `tests`, a test-writer writes them first, as in a gameplay
phase.

**`scaffold`, `contracts`, `wiring`, `ui`, `juice`, `audio`, `docs` phases:** implementer → review
(panel if `risk: high`) → fresh runner for the checks the kind calls for (build + smoke + screenshot
for scaffold and wiring, typecheck for contracts, behavior tests where a `ui` phase owns them) →
playtest where `playtest_focus` is set (juice is judged from screenshots captured at the moment it
fires) → fix rounds as above → commit. Scaffold must leave `test`, `smoke` and `screenshot`
working; later playtests depend on them. Audio: produce `procedural` sounds or wire `external`
files if the manifest says so; otherwise stub files plus a gap in the progress file. Never invent
audio that wasn't produced, and mark "sounds right" as `needs-human`.

## Step 4: Run the waves

**No fixed cap.** Launch every phase whose dependencies are verified and whose files don't overlap
a running writer — all in one message. Phases are pipelined: each one flows through its own
cycle, and nothing waits for a sibling unless there's a dependency. What bounds the width:

1. **Ready, disjoint work.** Count the unblocked phases with pairwise-disjoint ownership — code,
   content, tests and assets together — and launch that many writers. `shared` files (style lock,
   autoloads, scene roots, atlases, import config) have one writer at a time.
2. **Claude Code's concurrent-subagent limit** (20 by default; `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`
   in `settings.json` `env` raises it). At the limit a spawn fails rather than queueing. Keep 2–3
   slots free for runners, reviewers and playtesters so verification never waits. If a spawn fails
   at the limit, record the work under "Deferred spawns" and launch it when a completion frees a
   slot — never retry in a loop, never drop it. On rate-limit or overload errors, re-spawn when the
   error clears and narrow the next wave until errors stop.
3. **Your integration bandwidth.** Every report and every merge lands on you. If reports pile up
   unread or merges wait, finish integrating before widening.

**What not to parallelize:** writers on the same `shared` file, scene or atlas; a test-writer and an
implementer on the same rules; a playtest of a scene that's still being written; and review gates
skipped to move faster — a bug found three phases later costs more time than the review. If
ownership is unclear, run it sequentially or send the plan back to architecture.

**Worktree policy.** When two or more implementers run at once with non-trivial writes, give each
`isolation: "worktree"`. Worktrees start from the last commit, which is why tests are committed
before implementation and every dependency is already committed when a phase starts. Asset-artists
with disjoint outputs, test-writers, reviewers, runners and playtesters work in the main tree. With
worktrees, a phase runs: implement in the worktree → review the branch diff (fix rounds happen in
the same worktree via `SendMessage`) → commit any uncommitted changes on that branch → `git merge
--no-ff` into the build branch → regression in the main tree. Disjoint ownership makes conflicts
rare; a trivial one is tiny glue, anything else goes back to the owning implementer.
`references/git-and-worktrees.md` has the command details.

## Step 5: Playtest and integration checkpoints

When all phases a `playtest_checkpoints` entry lists are verified, launch two workers together:

- An `[integration-tester]` with the checkpoint's `verifies` text, the gdd_refs it covers, and the
  interface docs. Unlike the test-writer, it reads the implementation — it has to know what was
  built to test how the pieces meet. It writes seam tests in a folder no phase owns
  (`tests/integration/{checkpoint}/`), runs them plus `smoke` and `screenshot`, and looks at the
  screenshots. Skip it for a checkpoint whose phases are all assets.
- A `[playtester]` with the exact `smoke` / `screenshot` command, the observable criteria from the
  checkpoint and the phases' `playtest_focus`, and where to save evidence
  (`tmp/playtest/{checkpoint}/`). If the session has browser tools (Playwright MCP, Claude in
  Chrome, the desktop app's browser) or the iOS simulator tool, the playtester may use them for
  exploratory checks, but pass/fail comes from the pinned, reproducible commands.

Failures usually mean two phases read a contract differently. Decide which side is wrong against
the architecture, send the fix to that phase's implementer (`SendMessage` if it's alive, a fresh
brief if not), then re-run the checkpoint and the regression. A checkpoint is a barrier only for
phases that depend on the phases it covers. Commit the integration tests when it's green.

Some criteria can't be judged from screenshots ("the swing feels weighty", audio, haptics). Mark
them `needs-human` in the progress file and list them in the final report as things for the user
to try — that's honest, not a failure.

## Step 6: Docs

For builds of about 5+ phases, spawn a `[docs-writer]` near the end — in parallel with the last
phases if it doesn't overlap — for README setup/run/test/export instructions, how to play, and how
to add content or re-run the art scripts. It never changes code. A reviewer spot-checks the docs
against the game: documentation that contradicts the game is worse than none. Skip for jams and
small builds.

## Step 7: Final verification and report

1. A fresh runner runs the full `test`, `typecheck`, `build`/`export`, `smoke` and `screenshot`,
   compared against the baseline. Failures go to the owning implementer and get re-verified.
   Nothing is reported green that isn't.
2. Run the traceability check over the whole build, integration tests included:
   `python3 <this skill's dir>/scripts/check_traceability.py <plan doc> --root <project root>
   --extra-tests "tests/integration/**"`. Its output is small, so run it yourself. Every gdd_ref a
   tested phase cites must be proven by a tagged test; an untested one goes back to the phase's
   test-writer (or the checkpoint's integration-tester) and is re-verified like any other finding.
3. The slice playtest: a `[playtester]` over the full slice, with screenshot evidence recorded in
   the progress file.
4. `git diff --stat <build start>..HEAD` shows no unintended files, and the working tree holds
   nothing but the user's pre-existing changes.
5. Mark the progress file COMPLETE and close the task list.
6. Report: what was built, phase by phase; gdd_refs covered (proven by tests, by playtest, or
   deferred); final verification with the exact commands; findings fixed; asset defects and
   audio/art stubs as they are; `needs-human` items for the user to try; lead-local fixes; anything
   still open; the routing — which phases ran on which tier, any escalations, and first-pass rate
   per role, so the user sees where the money went and whether the routing held up; the branch and
   its commits; how to run and play it. Don't push or open a PR unless the user asks — offer it.

## When to stop and ask

The build runs straight through except for these. When one happens, record it in the progress
file, keep every unaffected phase running, and ask the user with one AskUserQuestion card that lays
out the realistic options. Only the blocked phase and its dependents wait.

- A GDD gap or contradiction: a missing rule or number, or a test dispute the GDD can't settle.
- An architecture gap that needs a design decision, or the architecture and the codebase disagree.
- An asset `method` that can't reach the spec (the artist proposes another method).
- A finding still open after 3 fix rounds (2 for test review).
- An environment failure that survives one fix attempt: dependencies won't install, the engine
  won't run headlessly, the screenshot command produces nothing.
- A worker needs to edit outside its ownership in a way that affects another phase.

## Worker brief template

```
{persona file contents}

Role: {role}   Phase: {id} {name}   Project root: {absolute path}

You are not alone in the codebase: other agents are editing other files right now. Don't revert
edits you didn't make. Don't run git commands that change state (commit, stash, reset, checkout,
rebase) — the lead handles git.

Read (paths, not pasted content):
- {GDD — the files and sections the gdd_refs cite}
- {architecture — interfaces, module design, conventions/testing-and-playtest if Developer mode}
- {exemplar files for patterns}
- {for implementers: the phase's test files — read-only}
- {for asset-artists: <skill dir>/references/asset-production.md, <skill dir>/scripts/asset_qa.py,
  style-lock paths, the GDD art-direction section, the Asset Manifest rows}

gdd_refs: {docs/gdd/03-systems.md#drop, …} — build and test exactly these; invent no player verbs,
numbers or feel beyond them and the architecture.

Own (edit nothing outside this list): {files / globs / asset paths}
Do not edit: {the phase's tests, for implementers; the style lock, for family artists}

Task: {concrete work}
Commands: {test_one with this phase's files, typecheck, smoke/screenshot, asset_qa — whatever the
role needs}

Done when: {tests pass / checks green / assets pass QA / playtest criteria judged / findings
addressed}

Stop and report instead of improvising if: the code doesn't match these docs, you'd need to edit a
file outside Own, a rule or number you need is missing from the GDD or architecture, the assigned
asset method can't reach the spec, or a command keeps failing after one reasonable fix.

Final response (under ~300 words): status, files changed, commands run with results, gdd_refs
covered, anything uncertain. Put long logs in a file under tmp/ and give the path — the lead
reads many reports, and its context is the build's bottleneck.
```

---
name: game-architecture-blueprint
description: >
  Turn a Game Design Document into a game technical architecture and a phased,
  ownership-mapped build blueprint: engine/runtime choice, scenes/entities, input and feel,
  content-as-data, asset pipeline with an Asset Manifest, file ownership, pinned
  run/test/smoke commands, and slice-first phases with gdd_refs plus a machine-readable Game
  Build Manifest. Writes architecture docs only — no game code or art. Use this skill whenever
  the user has a GDD, slice definition, or game idea and asks to "architect this game", "how
  should we build this game", "plan the vertical slice", choose between Godot/Unity/Unreal/
  Phaser/web canvas, lay out scenes/entities, design an asset pipeline, or move from game
  design toward coding and art. Prefer it over solution-architect whenever the deliverable is
  a game. Run game-design-document first if the GDD is missing or thin; hand off to
  game-dev-orchestrator after.
---

# Game Architecture Blueprint

Act as a senior game-tech architect. Convert an approved GDD into an implementation-ready technical design. `game-dev-orchestrator` (and human builders) must be able to follow your docs without inventing structure, player verbs, or asset specs — its workers are autonomous subagents that can't stop mid-task to ask you what you meant.

## Core Rules

- **Start from the GDD.** The GDD describes what the player does and feels; this skill decides how the project is structured.
- **Respect an existing project.** Fit its engine, folder layout, scene model, and test harness unless the user explicitly wants a migration.
- **Consequential decisions go through `AskUserQuestion`.** Present 2–4 realistic options with implications; batch related decisions (up to 4 questions per call). Headers are ≤12-character chips ("Engine", "Physics", "Scene model"). Put the option you recommend first, suffixed "(Recommended)".
- **Ask only what changes architecture.** Infer ordinary engine details in PM mode; surface them in Developer mode.
- **Right-size the docs.** A small feature/mode uses one design file. A new game or multi-system slice uses `assets/large-game-docs/`.
- **Design for execution.** Every code and asset file has an owner and a purpose. Every phase has dependencies, outputs, parallel opportunities, test focus, playtest focus, and **gdd_refs**.
- **Docs only.** Only `game-dev-orchestrator` implements game code or produces assets.
- **Cite the GDD by file + section or system name.** Don't mint `US-*` / `AC-*` / `BR-*` IDs.

If `AskUserQuestion` isn't available (e.g. Claude.ai), ask in chat as a numbered list of options with tradeoffs. If the user says not to ask ("make reasonable calls", "I'm not around"), take the option you'd have recommended, and record each such choice under **Unresolved From GDD / Assumptions** so it's easy to overturn.

## Plan Mode

When the design has genuine architectural ambiguity with high reversal cost (engine, scene model, physics vs kinematic), you may call `EnterPlanMode` so the user reviews the approach before files are written. If you're already in plan mode, the same applies. The plan you submit with `ExitPlanMode` must be a **documentation plan only**:

- Describe only which architecture docs you'll create or update, and the key decisions in them.
- State explicitly that no game source, scaffolding, assets, tests, or engine project files will be created.
- Implementation phases may appear as *content inside* the architecture docs; you don't execute them.

## Resources

- `assets/design-template.md` — small/focused feature or mode
- `assets/large-game-docs/` — new game or multi-phase slice (copy, then fill; delete files that don't apply)
- `references/pipeline-contract.md` — stage boundaries, asset production `method`s, what the orchestrator expects
- `references/ownership-checklist.md` — run before finalizing file structure and phases
- `references/developer-mode.md` — when the user chooses Developer mode
- `references/engine-notes.md` — load **after** the engine is chosen; typical folders, commands, and how an agent can see the game
- `scripts/check_manifest.py` — lints the Game Build Manifest (ownership partition, shared-file creators, deps, gdd_refs, commands, asset methods); run it before presenting

## Before Designing

1. Read the GDD. Prefer a user-specified path; otherwise `docs/gdd/` or `docs/gdd/features/{name}/`.
2. Read every GDD file you find. Note pillars, non-goals, loop, systems (status + in-slice), content volume, juice, art production notes, slice definition, constraints, open questions.
3. Scan an existing codebase if present (timeboxed): engine, folder structure, scene/entity model, input, asset import, test tools, run commands, CLAUDE.md conventions. For a non-trivial repo, delegate the sweep to an `Explore` subagent (Agent tool, `subagent_type: "Explore"`, `model: "opus"`) and read only the decisive files yourself.
4. If the GDD is missing or too thin (no loop, no system rules, no slice), gather the minimum via `AskUserQuestion` or suggest running `game-design-document` first.
5. Treat GDD engine lines as **constraints**, not architecture. Choose or confirm the engine here.

## Skip Path

For a trivial one-file change the user wants coded immediately with no structural ambiguity, say so and hand off to implementation — don't force a full blueprint. For anything with multi-file ownership, new scenes, persistence, or an asset set, produce architecture docs first.

## Design Conversation

### 1. Confirm Mode And Scale (first `AskUserQuestion`)

Summarize your understanding in plain text, then batch mode + scale (and any early architecture-changing forks) into the first call:

- **PM mode** (default): solo builders and `game-dev-orchestrator` handoff. Infer ordinary engine details. Batch aggressively.
- **Developer mode**: human game team. Surface scene/physics/input/test-harness/package choices. Read `references/developer-mode.md`.

Production scale is a hard constraint on ceremony:

- **jam** — smallest docs that still have ownership + a slice phase
- **vertical-slice** — prove the fantasy; ship content can be stubbed
- **shippable-indie** — slice plus ship systems (live services only if the GDD actually has them)

**Tiny-feature shortcut:** one confirmation call (mode + scale + the single ambiguity), then write `design.md`.

Record:

```
Mode: PM | Developer
Scale: jam | vertical-slice | shippable-indie
```

### 2. Resolve Architecture-Changing Ambiguities

Ask when the answer changes structure: engine, 2D vs 3D vs 2.5D, physics vs authored/kinematic motion, scene-tree vs ECS vs hybrid, save/persistence, netcode, target FPS/resolution, how the slice is run and tested, how art will be produced.

Recommend from GDD constraints (platform, haptics, session, art bar). Don't pad with engines that can't meet those constraints. If GDD constraints conflict, stop and ask how to resolve.

### 3. Choose Engine Or Fit Existing

Existing project: keep the engine; ask only about meaningful additions.

Greenfield: recommend an engine, explain why it fits the GDD constraints, confirm when consequential. Then read `references/engine-notes.md` for that engine's folders, commands, and screenshot path.

One factor matters more for this pipeline than for a human team: **the build is done by Claude Code agents working from a terminal.** They can only verify what they can run headlessly and see as a screenshot or log. Web stacks (Phaser, PixiJS, Three.js, plain canvas) with a Playwright smoke script are the easiest for agents to build *and* playtest. Godot, Unity, and Unreal work, but only when headless test and screenshot commands can be pinned — say so in the tradeoff description when you recommend.

In PM mode, leave ordinary add-on choices to the builder. In Developer mode, surface them.

### 4. Make The Scope Call

- Small/focused → `assets/design-template.md`
- New game or multi-phase slice → `assets/large-game-docs/`

Lean small when in doubt. A jam still needs a slice-first phase list, not a live-ops topology.

### 5. Design The System

Cover what applies. Don't invent GDD rules; map them to modules.

**Runtime and scenes:** Engine, language, main loop / tick, pause, time scale, scene graph, autoloads/singletons, camera rig. Every scene or autoload has one owner.

**Systems as modules:** One module per in-slice GDD system (plus a shared kernel: input, time, audio bus, RNG). For each: what it owns, what it exposes, what it depends on, where it lives. Interfaces at seams (overlap/resolve, scoring, state machine, save) get signatures, types, and error cases — autonomous workers can't ask mid-build, so ambiguity here turns into two incompatible guesses.

**Input and feel:** Device map from GDD controls. Which juice is code (squash, hitstop, camera, tween), which is an asset (VFX sprite, SFX), which is platform (haptics). Pin how to trigger each in a playtest.

**Content as data:** What is code vs data (levels, curves, spawn tables, localization). File formats. The schema lives in a dedicated file so content-authors and gameplay workers don't dual-own it.

**Asset pipeline:** Naming, resolution, pixels-per-unit / import settings, atlas vs discrete, animation packing, background/transparency. Produce an **Asset Manifest** for slice assets (and ship assets if scale is shippable-indie). Each entry: id, path, kind, **method** (see `references/pipeline-contract.md` — `code-vector`, `code-raster`, `procedural`, `image-gen`, `greybox`, `external`), slice vs ship, `depends_on` (style-lock first), owning phase. Pick methods honestly: Claude agents can draw excellent flat/vector/pixel/geometric art with code, but can't paint; only choose `image-gen` if the user confirms a generation tool is available in their Claude Code setup.

**Style lock:** For any non-greybox art, the first asset is a style lock — a palette file (hex values), a reference sheet image, and a short rules note (outline weight, shading style, proportions, pixel density). Every other visual asset depends on it so parallel artists stay consistent.

**Numbers:** GDD TBD-tunable values stay tunable — put defaults in a data file the slice can retune. Don't freeze unproven feel as code constants unless the GDD locked them.

**Run / test / smoke / see:** Pin commands so the orchestrator doesn't re-guess. Include a smoke/playtest command and a **screenshot command** (e.g. a Playwright script that loads the game, performs the core verb, and saves `tmp/playtest/*.png`) — the orchestrator's playtesters verify by looking at those images.

### 6. Produce The Build Blueprint

- Complete file structure with a purpose for every code **and** asset file. Run `references/ownership-checklist.md`.
- Granular phases, **vertical-slice-first**, split into parallel slices (see below). Each phase: What gets built, Depends on, Produces, Parallel opportunities (fully disjoint write sets with globs), Test focus, Playtest focus, **gdd_refs**. Developer mode also Success criteria and Review checklist.
- Typical dependency shape (adapt; don't cargo-cult software auth→API→UI). Items on the same line can run at the same time:
  1. Scaffold (engine project, folders, pinned commands, screenshot harness) **‖** style lock **‖** contracts (shared types/interfaces, data schema)
  2. One slice per in-slice rules module (overlap, scoring, lives, state machine…), each with its own tests **‖** every asset family **‖** content data against the schema
  3. Greybox scene + wiring that puts the modules on screen (the one phase that owns the hub files)
  4. Juice / feel **‖** HUD / flow **‖** audio (procedural, external, or stubs + explicit gaps) — each owning its own module, wired through registration points
  5. Slice playtest gate
- Explicit playtest / integration checkpoints (loop playable, rules vs GDD, assets on greybox, juice readable, full slice).
- **Game Build Manifest** for multi-phase work (required). It's derived from the prose; prose wins on conflict.

**Parallel opportunities:** Mark parallel only when write sets are fully disjoint (no shared scene, autoload, atlas, or types file). List each slice with file globs. Collision paths go in manifest `shared`. Style-lock and import config are `shared` until produced; later asset workers depend on them and must not edit them.

### 7. Design For A Wide Build

`game-dev-orchestrator` has no fixed worker cap: it launches every ready slice whose `owns` don't overlap, all at once, up to Claude Code's session limit (20 concurrent subagents by default). So **the shape of this blueprint decides how fast the game gets built.** A plan where every phase touches `PlayScene` builds one worker at a time no matter how capable the orchestrator is. In the Skyline Stack example, a single scene file shared by five phases meant only one pair of phases could ever run in parallel. Aim for the widest honest plan — slices that are genuinely independent, not ones that will collide at merge time.

Techniques, roughly in order of payoff:

1. **One slice per in-slice GDD system.** Give each rules module its own phase (or sub-phase `p3a`, `p3b`, …) with its own source file, its own test file, and its own gdd_refs. Keep rules modules pure (no engine/renderer imports) so they never touch scene files and can be tested headlessly.
2. **Contracts first.** Put shared types, interfaces, event names, and the data schema in an early *contracts* phase (small, owned once). Every later slice codes and writes tests against those contracts in parallel, instead of waiting for the module it calls to exist.
3. **No hub files shared by many phases.** Scene roots, the main game loop, autoload registries, and `main.ts`-style entry points are where plans serialize. Use registration/plug-in points instead: each feature module exports a `register(game)` / `install(scene)` function in its own file, and a single *wiring* phase owns the hub and calls them. If a file would appear in `shared` for three or more phases, restructure — `check_manifest.py` warns about exactly this.
4. **Start the style lock at the beginning** (`depends_on: []`), alongside scaffold and contracts, so art is never on the critical path. Then give each asset family (player, enemies, tiles, UI, FX, backdrops) its own phase and glob so they all start the moment the lock lands.
5. **Tests are their own owned files.** Each slice's tests live in files only that slice's test-author writes, so test-authoring for all slices can run at once.
6. **Content data splits by file.** One file per level/wave/table when volume allows, so several content-authors can work together once the schema exists.
7. **Keep playtest gates few and meaningful.** They're barriers; place them where they catch real integration risk (loop playable, assets on greybox, full slice), not after every phase.

Don't manufacture independence that isn't there: if two modules genuinely share mutable state or a single file, they're one slice. A merge conflict or an integration bug costs more time than the parallelism saved.

In `implementation-plan.md`, add a short **Parallel Waves** table (wave → phases that can run together) and name the critical path. Run `scripts/check_manifest.py` — it prints the waves it computes from `depends_on`; if the widest wave is much narrower than the number of in-slice systems plus asset families, look for a hub file or an unnecessary dependency edge.

## Design Completeness Gate

Don't write final docs until:

- [ ] Mode and Scale are decided and will be recorded
- [ ] Engine and platform are clear
- [ ] Architecture-changing questions are resolved or explicitly deferred with user OK (or recorded as assumptions in no-questions mode)
- [ ] Modules map to in-slice GDD systems without rewriting the GDD
- [ ] File ownership map is complete (code + assets)
- [ ] Asset Manifest covers slice assets with a realistic `method`; style-lock is a dependency of character/tile/UI sets
- [ ] Interfaces at multi-worker and high-risk seams are specified at autonomous-builder depth
- [ ] Every phase has depends/produces/parallel/test focus/playtest focus/**gdd_refs**
- [ ] Playtest checkpoints are named, and a screenshot/smoke path exists for them
- [ ] Run/test/smoke commands are pinned (or TBD for scaffold only)
- [ ] Ownership checklist passes
- [ ] Hub files (scene roots, entry point, registries) are owned by one wiring phase, not shared across many; every in-slice system and asset family is its own slice where honestly independent
- [ ] The Parallel Waves table exists and names the critical path
- [ ] Multi-phase work has a Game Build Manifest consistent with prose, and `scripts/check_manifest.py` reports 0 errors

## Output

Write docs (paths relative to the project root; create directories as needed):

- New game: `docs/game-architecture/`
- Feature/mode: `docs/gdd/features/{feature-name}/architecture/`

### Small Feature

Copy `assets/design-template.md` to `design.md` and fill it. Delete sections that don't apply. In PM mode, delete Developer-only sections. For multi-phase small features, include the Game Build Manifest; for a trivial single-phase feature, inline `owns` / `depends_on` / `gdd_refs` / `test_focus` into the phase prose.

### New Game / Multi-Phase Slice

Copy `assets/large-game-docs/` into the architecture output directory (`cp -r` is fine), fill the relevant files, and delete files that don't apply (delete `conventions.md` and `testing-and-playtest.md` in PM mode). Always include the Game Build Manifest and Asset Manifest in `implementation-plan.md` for multi-phase work.

## Quality Bar

The docs pass only if:

- Every needed code and asset file is listed with a purpose and owner.
- No two parallel phases write the same file; shared files are `shared`, not dual-owned.
- In-slice GDD systems have a module home; out-of-slice systems are named as deferred.
- Seams workers could get wrong have contracts.
- Hard-to-reverse choices have rationale, alternatives, and tradeoffs.
- Phase order is slice-first; gdd_refs point at real GDD sections/systems.
- Every asset has a production method an agent can actually execute.
- The manifest matches the prose (names, owns, depends_on, gdd_refs, commands, assets).
- The plan is as wide as the design honestly allows: no avoidable hub-file serialization, style lock and contracts early, one slice per system and asset family.
- A competent `game-dev-orchestrator` team could execute without asking structural questions or inventing player-facing behavior.

Avoid "the gameplay layer handles mechanics." Say which module owns which GDD system, what it exposes, and who depends on it.

Before presenting, run `python3 <this skill dir>/scripts/check_manifest.py <implementation-plan.md or design.md> --root <project root>` (needs PyYAML; if it's missing, walk `references/ownership-checklist.md` by hand and say so). Fix every error in the prose first, then the manifest, and re-run. The most common miss is a file that later phases list under `shared` but no phase `owns` — someone has to create it, usually the scaffold or the phase that introduces the module. Eyeballing a long YAML block misses this; the script doesn't.

After writing, list the files as clickable links, summarize key decisions, and ask for review via `AskUserQuestion` (approve / request changes). Update in place on changes. Once approved, hand off.

## Handoff

"Architecture complete. The next step is coordinated implementation — run `game-dev-orchestrator` (`/game-dev-orchestrator`). Point it at the architecture docs or let it auto-discover them."

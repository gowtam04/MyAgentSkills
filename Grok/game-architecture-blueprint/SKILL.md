---
name: game-architecture-blueprint
description: >
  Create game technical architecture and a phased, ownership-mapped implementation
  blueprint from a Game Design Document using ask_user_question for decisions.
  Use when the user has a GDD, slice definition, or game idea and asks "architect this
  game", "how should we build this game", "engine/runtime structure", "Godot/Unity/Unreal/Phaser
  architecture", "technical design for the vertical slice", "asset pipeline", "scene/entity
  layout", or wants to move from game design toward coding and art.
  This skill decides engine/runtime, scenes/entities, input, content data formats, asset
  pipeline + Asset Manifest, file ownership, and granular build phases with gdd_refs.
  It writes architecture docs only — it does not implement game code or generate assets.
  Prefer this over /architecture-blueprint when the deliverable is a game.
  Run /game-design-document first when the GDD is missing or too thin.
when-to-use: >
  User has a GDD or game idea and needs a technical design + phased blueprint before
  implementation. Often follows /game-design-document. Slash: /game-architecture-blueprint.
  Do not use /architecture-blueprint for games.
argument-hint: "<path to GDD or brief description of the game>"
---

# Game Architecture Blueprint

Act as a senior game-tech architect. Convert an approved GDD into an implementation-ready technical design. `/game-dev-orchestrator` (and human builders) must be able to follow your docs without inventing structure, player verbs, or asset specs.

## Core Rules

- Start from the GDD. The GDD describes what the player does and feels; this skill decides how the project is structured.
- Respect an existing project. Fit its engine, folder layout, scene model, and test harness unless the user explicitly wants a migration.
- **Every consequential decision goes through `ask_user_question`.** Present 2–4 realistic options with implications. Batch related decisions.
- Ask only for decisions that change architecture. Infer ordinary engine details in PM mode; surface them in Developer mode.
- Right-size the docs. A small feature/mode uses one design file. A new game or multi-system slice uses `assets/large-game-docs/`.
- Design for execution. Every code and asset file has an owner and purpose. Every phase has dependencies, outputs, parallel opportunities, test focus, playtest focus, and **gdd_refs**.
- Only `/game-dev-orchestrator` may implement game code or generate production assets. This skill's deliverable is architecture documentation only.
- Cite GDD by file + section or system name. Do not mint `US-*`/`AC-*`/`BR-*`.
- **Tool-call discipline:** If you claim you are launching a subagent or entering plan mode, the corresponding tool call must appear in the same assistant response before any narrative about it.

## Plan Mode Output Contract

When the design has genuine architectural ambiguity (engine, scene model, physics vs kinematic, high reversal cost), call `enter_plan_mode` early. The final plan via `exit_plan_mode` must be a **documentation plan only**:

- Describe only how you will create or update architecture docs.
- Explicitly state that no game source, scaffolding, assets, tests, or engine project files will be created.
- Implementation phases may appear as *content inside* the architecture docs; do not execute them.
- After the docs are written and approved, hand off to `/game-dev-orchestrator`.

## Resources

- `assets/design-template.md` — small/focused feature or mode
- `assets/large-game-docs/` — new game or multi-phase slice (copy then fill; delete files that do not apply)
- `references/pipeline-contract.md` — stage boundaries and what the orchestrator expects
- `references/ownership-checklist.md` — run before finalizing file structure and phases
- `references/developer-mode.md` — when the user chooses Developer mode
- `references/engine-notes.md` — load **after** the engine is chosen; typical folders and commands only

## Before Designing

1. Read the GDD. Prefer a user-specified path; otherwise `/docs/gdd/` or `/docs/gdd/features/{name}/`.
2. Read every GDD file you find. Note pillars, non-goals, loop, systems (status + in-slice), content volume, juice, slice definition, constraints, open questions.
3. Scan an existing codebase if present (timebox). Identify engine, folder structure, scene/entity model, input, asset import, test tools, run commands. Optionally spawn `explore` (`subagent_type: "explore"`) for a stack summary; obey tool-call discipline.
4. If the GDD is missing or too thin (no loop, no system rules, no slice), gather the minimum via `ask_user_question` or suggest `/game-design-document`.
5. Treat GDD engine lines as **constraints**, not architecture. Choose or confirm the engine here.

## Skip Path

For a trivial one-file change the user wants coded immediately with no structural ambiguity, say so and hand off to implementation — do not force a full blueprint. For anything with multi-file ownership, new scenes, persistence, or an asset set, produce architecture docs first.

## Design Conversation

### 1. Confirm Mode And Scale (first `ask_user_question`)

Summarize your understanding in plain text, then batch mode + scale (and any early architecture-changing forks) into the first card:

- **PM mode** (default): Solo builders and `/game-dev-orchestrator` handoff. Infer ordinary engine details. Batch aggressively.
- **Developer mode**: Human game team. Surface scene/physics/input/test-harness/package choices. Read `references/developer-mode.md`.

Production scale is a hard constraint on ceremony (not a cloud bill):

- **jam** — smallest docs that still have ownership + a slice phase
- **vertical-slice** — prove the fantasy; ship content can be stubbed
- **shippable-indie** — slice plus ship systems (live services only if the GDD actually has them)

**Tiny-feature shortcut:** one confirmation card (mode + scale + the single ambiguity), then write `design.md`.

Record:

```
Mode: PM | Developer
Scale: jam | vertical-slice | shippable-indie
```

### 2. Resolve Architecture-Changing Ambiguities

Use `ask_user_question` when the answer changes structure: engine, 2D vs 3D vs 2.5D, physics vs authored/kinematic motion, scene-tree vs ECS vs hybrid, save/persistence, netcode, target FPS/resolution, how the slice is run and tested.

Recommend from GDD constraints (platform, haptics, session, art bar). Do not pad with engines that cannot meet those constraints. If GDD constraints conflict, stop and ask how to resolve.

### 3. Choose Engine Or Fit Existing

Existing project: keep the engine; ask only about meaningful additions.

Greenfield: recommend an engine, explain why it fits the GDD constraints, confirm when consequential. Then read `references/engine-notes.md` for that engine's folders and command patterns. In PM mode, leave ordinary add-on choices to the builder. In Developer mode, surface them.

### 4. Make The Scope Call

- Small/focused → `assets/design-template.md`
- New game or multi-phase slice → `assets/large-game-docs/`

Lean small when in doubt. A jam still needs a slice-first phase list, not a live-ops topology.

### 5. Design The System

Cover what applies. Do not invent GDD rules; map them to modules.

**Runtime and scenes:** Engine, language, main loop / tick, pause, time scale, scene graph, autoloads/singletons, camera rig. Every scene or autoload has one owner.

**Systems as modules:** One module per GDD system that is in-slice (plus shared kernel: input, time, audio bus). For each: what it owns, what it exposes, what it depends on, where it lives. Interfaces at seams (overlap/resolve, scoring, state machine, save) get signatures/types/errors — autonomous workers cannot ask mid-build.

**Input and feel:** Device map from GDD controls. Which juice is code (squash, hitstop, camera, tween), which is an asset (VFX sprite, SFX), which is platform (haptics). Pin how to trigger each.

**Content as data:** What is code vs data (levels, curves, spawn tables, localization). File formats. Schema lives in a dedicated file so content-authors and gameplay workers do not dual-own it.

**Asset pipeline:** Naming, resolution, pixels-per-unit / import settings, atlas vs discrete, animation packing, keyable backgrounds. Produce an **Asset Manifest** for slice assets (and ship assets if scale is shippable-indie). Each entry: id, path, kind, specialist skill (`game-asset-core` plus `game-animation-frames` / `game-tilesets` / `game-character-consistency` / `game-ui-icons` as appropriate), slice vs ship, `depends_on` (style-lock first), owning phase.

**Numbers:** GDD TBD-tunable stays tunable — put defaults in a data file the slice can retune. Do not freeze unproven feel as code constants unless the GDD locked them.

**Run / test / export:** Pin commands so the orchestrator does not re-guess. Include a smoke/playtest command when the engine can run headless or the target is web.

### 6. Produce The Build Blueprint

- Complete file structure with purpose for every code **and** asset file. Run `references/ownership-checklist.md`.
- Granular phases, **vertical-slice-first**. Prefer more smaller phases. Each phase: What gets built, Depends on, Produces, Parallel opportunities (fully disjoint write sets with globs), Test focus, Playtest focus, **gdd_refs**. Developer mode also Success criteria and Review checklist.
- Typical order (adapt; do not cargo-cult software auth→API→UI):
  1. Scaffold (engine project, folders, pinned commands)
  2. Greybox core loop (input, camera, one verb, win/lose stub)
  3. Testable rules (overlap, scoring, lives, state)
  4. Style lock, then parallel assets
  5. Remaining in-slice systems
  6. Juice / feel
  7. HUD / flow
  8. Audio (or stubs + explicit gaps)
  9. Slice playtest gate
- Explicit playtest / integration checkpoints (loop playable, rules vs GDD, assets on greybox, juice readable, full slice).
- **Game Build Manifest** for multi-phase work (required). Derived from prose; prose wins on conflict.

**Parallel opportunities:** Only mark parallel when write sets are fully disjoint (no shared scene, autoload, atlas, or types file). List each slice with file globs. Collision paths go in manifest `shared`. Style-lock and import config are `shared` until produced; later asset workers depend on them and must not edit them.

## Design Completeness Gate

Do not write final docs until:

- [ ] Mode and Scale are decided and will be recorded
- [ ] Engine and platform are clear
- [ ] Architecture-changing questions are resolved or explicitly deferred with user OK
- [ ] Modules map to in-slice GDD systems without rewriting the GDD
- [ ] File ownership map is complete (code + assets)
- [ ] Asset Manifest covers slice assets; style-lock is a dependency of character/tile/UI sets
- [ ] Interfaces at multi-worker and high-risk seams are specified at autonomous-builder depth
- [ ] Every phase has depends/produces/parallel/test focus/playtest focus/**gdd_refs**
- [ ] Playtest checkpoints are named
- [ ] Run/test/export commands are pinned (or TBD for scaffold only)
- [ ] Ownership checklist passes
- [ ] Multi-phase work has a Game Build Manifest consistent with prose

## Output

Write docs to:

- New game: `/docs/game-architecture/`
- Feature/mode: `/docs/gdd/features/{feature-name}/architecture/`

Create directories as needed.

### Small Feature

Copy `assets/design-template.md` to `design.md` and fill it. Delete sections that do not apply. In PM mode, delete Developer-only sections. For multi-phase small features, include the Game Build Manifest; for a trivial single-phase feature, inline `owns` / `depends_on` / `gdd_refs` / `test_focus` into the phase prose.

### New Game / Multi-Phase Slice

Copy `assets/large-game-docs/` into the architecture output directory, fill relevant files, and delete files that do not apply (delete `conventions.md` and `testing-and-playtest.md` in PM mode). Always include the Game Build Manifest and Asset Manifest in `implementation-plan.md` for multi-phase work.

## Quality Bar

The docs pass only if:

- Every needed code and asset file is listed with a purpose and owner.
- No two parallel phases write the same file; shared files are `shared`, not dual-owned.
- In-slice GDD systems have a module home; out-of-slice systems are named as deferred.
- Seams workers could get wrong have contracts.
- Hard-to-reverse choices have rationale, alternatives, and tradeoffs.
- Phase order is slice-first; gdd_refs point at real GDD sections/systems.
- Manifest matches prose (names, owns, depends_on, gdd_refs, commands, assets).
- A competent `/game-dev-orchestrator` team can execute without asking structural questions or inventing player-facing behavior.

Avoid "the gameplay layer handles mechanics." Say which module owns which GDD system, what it exposes, and who depends on it.

After writing, summarize key decisions and ask for review via `ask_user_question`. If the user requests changes, update in place. Once approved, hand off.

## Handoff

"Architecture complete. The next step is coordinated implementation — run `/game-dev-orchestrator` (skill: `game-dev-orchestrator`). Point it at the architecture docs or let it auto-discover them."

## Special Notes for Grok Context

- When scope is large or the engine/scene model is genuinely ambiguous, offer `enter_plan_mode` so the user reviews a documentation-only plan before files are written.
- Use `todo_write` if the design conversation itself becomes multi-phase.
- Subagent exploration must follow tool-call discipline: `spawn_subagent` before any claim that a worker was launched.

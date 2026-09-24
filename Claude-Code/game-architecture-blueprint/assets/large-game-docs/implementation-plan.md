# Implementation Plan

Granular, slice-first phases. Prefer more phases with smaller scope. This file is the primary task graph for `game-dev-orchestrator`.

## File Structure (Ownership Map)

Complete tree of files to create or modify. Each file: purpose + owning module. No two parallel phases write the same file.

```text
# code/
# assets/
# data/
# tests/
```

## Phase N: {Name}

- **What gets built:** specific files/components
- **Depends on:** prior phase(s)
- **Produces:** interfaces/files available after
- **Parallel opportunities:** fully disjoint write sets with globs, or "none — sequential"
- **Test focus:** what automated tests verify, or why TDD does not apply
- **Playtest focus:** observable check, or "none — not playable yet"
- **gdd_refs:** GDD file + section or system name
- **Success criteria** *(Developer mode)*
- **Review checklist / test split** *(Developer mode)*

(Repeat.)

## Parallel Waves

The orchestrator launches every phase in a wave at once (no fixed worker cap), so this table is effectively the build schedule. Derive it from `depends_on`; `scripts/check_manifest.py` prints the computed waves to cross-check.

| Wave | Phases that can run together | Notes |
|---|---|---|
| 1 | scaffold, style-lock, contracts | nothing depends on anything yet |
| 2 | one slice per rules module, each asset family, content data | |
| … | | |

**Critical path:** p? → p? → … (the longest dependency chain; shorten it before widening anything else)

**Hub files and their single owner:** e.g. `src/scenes/PlayScene.ts` → wiring phase only; feature modules plug in via `register()` in their own files.

## Typical Slice Shape (adapt; `‖` = runs in parallel)

1. Scaffold ‖ style lock ‖ contracts (shared types, interfaces, data schema)
2. Rules slices (one per module, each with its own tests) ‖ asset families ‖ content data
3. Greybox scene + wiring (owns the hub files; calls each module's registration point)
4. Juice ‖ HUD / flow ‖ audio (each its own module)
5. Slice playtest gate

## Playtest / Integration Checkpoints

- Loop first playable
- Rules vs GDD numbers/insets
- Assets replacing greybox without breaking alignment
- Juice/haptics readable
- Full slice (onboarding through retry)

## Game Build Manifest

Machine-readable appendix. **Prose phases and File Structure above are the source of truth.** Generate last; on conflict, fix the prose first. Required for multi-phase builds.

```yaml
commands:
  run: "..."
  test: "..."
  test_one: "..."
  export: "..."
  smoke: "..."
  screenshot: "..."        # saves PNGs an agent can view, e.g. node scripts/screenshot.mjs
phases:
  - id: p1
    name: Scaffolding
    depends_on: []
    owns: ["..."]
    shared: []
    gdd_refs: []
    kind: scaffold
    test_focus: "tooling smoke if any"
    playtest_focus: "none"
    flags: [scaffold]
  - id: p2
    name: Greybox Core Loop
    depends_on: [p1]
    owns: ["..."]
    shared: ["..."]
    gdd_refs: ["docs/gdd/02-core-loop-and-structure.md"]
    kind: gameplay
    test_focus: "input registers; drop spawns a floor"
    playtest_focus: "tap drops; retry from results"
    flags: []
playtest_checkpoints:
  - after: [p2]
    name: loop-playable
    verifies: "one full drop cycle on device or simulator"
assets:
  - id: style-lock
    path: assets/style/style-lock.png
    kind: style-lock
    method: code-vector      # code-vector|code-raster|procedural|image-gen|greybox|external
    slice: true
    depends_on: []
    phase: p4
```

Field rules:

- `owns` partitions the File Structure; no two phases overlap. Multi-touch files go in `shared`.
- `commands` matches Run/Test/Export; TBD only in scaffold.
- `gdd_refs` cite real GDD paths/sections; do not fabricate US/AC/BR.
- `kind` drives orchestrator rigor: `gameplay` with rules → tests-first; `assets` → produce + view-and-compare visual QA; `playtest` → playtester worker.
- Asset `method` tells the asset-artist how to produce it (`code-vector` | `code-raster` | `procedural` | `image-gen` | `greybox` | `external` — defined in the game pipeline contract). Two assets that share a sheet/atlas must not be parallel.

## Orchestrator Notes

- **Mode** and **Scale** from `overview.md` control rigor (`jam` / small PM → light cycle; Developer / shippable → full tests + review + playtest).
- Prefer this manifest for DAG, ownership, commands, gdd_refs, and assets when present.
- Each phase becomes worker tasks with strict file ownership; serialize `shared`.
- Parallelism: the orchestrator has no fixed worker cap — it launches every ready phase/slice whose `owns` are disjoint. Width comes from this plan: finer disjoint slices and fewer shared hub files mean more simultaneous workers. Soft ownership forces sequential work.

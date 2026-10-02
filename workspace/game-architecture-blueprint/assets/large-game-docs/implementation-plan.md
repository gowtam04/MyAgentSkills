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
  test_one: "... {files}"  # {files} = space-separated test paths
  typecheck: "..."         # or "none" for untyped stacks
  build: "..."             # optional
  export: "..."            # optional
  smoke: "..."
  screenshot: "..."        # saves PNGs an agent can view, e.g. node scripts/screenshot.mjs
phases:
  - id: p1
    name: Scaffolding
    kind: scaffold
    depends_on: []
    owns: ["...", "src/scenes/PlayScene.ts"]   # scaffold creates the scene; wiring fills it
    tests: []
    gdd_refs: []
    test_focus: "build, smoke and screenshot work on an empty scene"
    playtest_focus: "none — not playable yet"
  - id: p2
    name: Contracts
    kind: contracts
    depends_on: [p1]
    owns: ["src/contracts/**"]
    gdd_refs: ["docs/gdd/03-systems.md"]
    test_focus: "typecheck"
    playtest_focus: "none — not playable yet"
  - id: p3
    name: Style lock
    kind: assets
    depends_on: []
    owns: ["assets/style/**", "tools/art/style.py"]
    gdd_refs: ["docs/gdd/06-art-audio-juice.md#art-direction"]
    test_focus: "none — asset QA"
    playtest_focus: "none — not playable yet"
  - id: p4a
    name: Drop rules
    kind: gameplay
    risk: high               # optional: normal (default) | high
    depends_on: [p2]
    owns: ["src/rules/drop.ts"]
    tests: ["tests/rules/drop.test.ts"]
    shared: []
    gdd_refs: ["docs/gdd/03-systems.md#drop"]
    test_focus: "overlap and trim, miss threshold, perfect drop, boundaries"
    playtest_focus: "none — covered at loop-playable"
  - id: p5
    name: Greybox wiring
    kind: wiring
    depends_on: [p4a]
    owns: ["src/scenes/register.ts"]
    shared: ["src/scenes/PlayScene.ts"]
    gdd_refs: ["docs/gdd/02-core-loop-and-structure.md"]
    test_focus: "smoke: boot, tap, a block lands"
    playtest_focus: "tap drops; retry from results"
playtest_checkpoints:
  - name: loop-playable
    after: [p5]
    verifies: "one full drop cycle on device or simulator"
assets:
  - id: style-lock
    path: assets/style/style-lock.png
    kind: style-lock
    method: code-raster      # code-vector|code-raster|procedural|image-gen|greybox|external|stub
    slice: true
    depends_on: []
    phase: p3
```

Field rules (full schema and the kind → verification table: `references/pipeline-contract.md`):

- `owns` (production files and assets) and `tests` (test files) partition the File Structure; no path is in two phases or in both fields of one phase. Test files are owned separately because the build gives them to a different worker (the test-writer) than the code. Multi-touch files go in `shared`.
- `gameplay` phases have at least one `tests` entry.
- `commands` matches Run/Test/Export; `run`, `test`, `smoke`, `screenshot` are required; TBD only in scaffold.
- `gdd_refs` cite real GDD paths/sections; do not fabricate US/AC/BR. Tests will carry the matching `gdd:<file stem>#<anchor>` tags, so keep cited headings stable.
- `kind` drives orchestrator verification: `gameplay` → spec-first tests; `contracts` → typecheck; `wiring` → the one phase that owns a hub; `content` → schema validation; `assets` → produce + view-and-compare QA + asset review; `playtest` → playtester worker.
- `risk: high` marks phases where a subtle mistake is expensive (physics and collision, save/load, economy math, netcode, deterministic simulation, input timing). The build reviews their tests before implementation and the code with a panel.
- Each Asset Manifest row's `phase` must own its `path`. Asset `method` tells the asset-artist how to produce it (defined in the game pipeline contract). Two assets that share a sheet/atlas must not be parallel.
- Write the YAML subset the contract defines (one-line flow lists, no anchors or multi-line strings), so `check_manifest.py` runs without PyYAML.

## Orchestrator Notes

- **Mode** from `overview.md` and each phase's `kind` and `risk` decide the verification cycle (Developer mode and `risk: high` add a test review before implementation; `risk: high` adds a review panel). **Scale** sets ceremony (jams skip the docs pass).
- Prefer this manifest for DAG, ownership, tests, commands, gdd_refs, and assets when present.
- Each phase becomes worker tasks with strict file ownership; serialize `shared`.
- Parallelism: the orchestrator has no fixed worker cap — it launches every ready phase/slice whose `owns` are disjoint. Width comes from this plan: finer disjoint slices and fewer shared hub files mean more simultaneous workers. Soft ownership forces sequential work.

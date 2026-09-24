# Implementation Plan

Granular, slice-first phases. Prefer more phases with smaller scope. This file is the primary task graph for `/game-dev-orchestrator`.

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

## Typical Slice Shape (adapt)

1. Scaffolding / project setup
2. Greybox core loop (input, camera, one verb, win/lose stub)
3. Testable rules (overlap, score, lives, state)
4. Style lock + parallel assets
5. Remaining in-slice systems
6. Juice / feel
7. HUD / flow
8. Audio or stubs
9. Slice playtest gate

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
    skill: game-asset-core
    slice: true
    depends_on: []
    phase: p4
```

Field rules:

- `owns` partitions the File Structure; no two phases overlap. Multi-touch files go in `shared`.
- `commands` matches Run/Test/Export; TBD only in scaffold.
- `gdd_refs` cite real GDD paths/sections; do not fabricate US/AC/BR.
- `kind` drives orchestrator rigor: `gameplay` with rules → tests-first; `assets` → generate + visual QA; `playtest` → playtester worker.
- Asset `skill` is the specialist to load with `game-asset-core`. Two assets that share a sheet/atlas must not be parallel.

## Orchestrator Notes

- **Mode** and **Scale** from `overview.md` control rigor (`jam` / small PM → light cycle; Developer / shippable → full tests + review + playtest).
- Prefer this manifest for DAG, ownership, commands, gdd_refs, and assets when present.
- Each phase becomes worker tasks with strict file ownership; serialize `shared`.
- Parallelism: disjoint `owns` bind each track. Code and asset-artist caps are **separate** in `/game-dev-orchestrator` (artists do not consume implementer slots). Soft ownership forces sequential work.

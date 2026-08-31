# {Feature or Game Name} - Technical Design

## Overview
Mode: PM | Developer
Scale: jam | vertical-slice | shippable-indie
Brief summary of what is being built and the technical approach.

## GDD Reference
Path: `[actual path used]`
Slice criterion this design serves:

## Engine And Platform
Engine, language, target devices, orientation, frame budget.
(Omit engine section for a feature that adds no new runtime.)

## Runtime And Scenes
Scene/entity model, main loop/tick, pause, autoloads, camera rig.
Each scene or autoload: owner + purpose.

## Module Design
Each module: GDD system it implements, responsibility (one sentence), interface, dependencies, file location.
If a module needs a paragraph to explain its purpose, split it or clarify the boundary.

## Input And Feel
Device map. Which juice is code vs asset vs platform (haptics). How to trigger each.

## Content And Data
What is code vs data. Formats. Schema file owner.

## Asset Pipeline
Naming, resolution, import settings, atlas vs discrete.
Greybox-only? If yes, state it. If no, Asset Manifest below.

## File Structure
Complete tree with descriptions — code **and** assets. Ownership map: one purpose per file; no two builders edit the same file in the same phase.

## Interface Definitions
Contracts at seams (overlap, scoring, state, save, signals). Scale detail to risk. Bias high detail at multi-worker seams.

## Implementation Phases
Ordered, slice-first. For each phase:
- What gets built (specific files)
- Depends on
- Produces
- Parallel opportunities (disjoint globs or "none — sequential")
- Test focus (or why TDD does not apply)
- Playtest focus (or "none — not playable yet")
- **gdd_refs** — GDD file + section or system name
- (Developer mode) Success criteria
- (Developer mode) Review checklist / test split

Call out playtest checkpoints: loop playable, rules vs GDD, assets on greybox, juice readable, full slice.

## Game Build Manifest  *(required for multi-phase; optional/inline for trivial single-phase)*
Derived from File Structure and Implementation Phases. Prose is the source of truth; generate last.

```yaml
commands: { run: "...", test: "...", test_one: "...", export: "...", smoke: "..." }
phases:
  - id: p1
    name: ...               # MUST match the prose phase name
    depends_on: []
    owns:   ["..."]
    shared: ["..."]
    gdd_refs: ["docs/gdd/03-systems.md#crane-pendulum"]
    kind: scaffold          # scaffold|gameplay|content|assets|audio|juice|ui|playtest
    test_focus: "..."
    playtest_focus: "none"
    flags: []
playtest_checkpoints:
  - { after: [p2], name: loop-playable, verifies: "..." }
assets:
  - id: style-lock
    path: assets/style/style-lock.png
    kind: style-lock
    skill: game-asset-core
    slice: true
    depends_on: []
    phase: p4
```

For a trivial single-phase feature, inline `owns` / `depends_on` / `gdd_refs` / `test_focus` into the prose and omit this block.

## Technical Decisions
Hard-to-reverse choices, alternatives, rationale, tradeoffs.

## Run Test Export
Restate Scale on the first line.

- run:
- test:
- test_one:
- export:
- smoke / playtest:

## Code Conventions  *(Developer mode only — delete in PM mode)*
Naming, module boundaries, time/pause, logging/debug overlay, lint/format.

## Testing Strategy  *(Developer mode only — delete in PM mode)*
Test runner, unit vs playtest vs visual, RNG/time mocking, fixture conventions.

## Unresolved From GDD
Open questions resolved here, and any that still need the user. TBD-tunable numbers stay data-driven unless the GDD locked them.

# Tower Drop — Technical Design

## Overview
Mode: PM
Scale: vertical-slice
Phaser 3 + TypeScript + Vite in the browser. Rules live in pure modules under `src/rules/` (no
Phaser imports) so they test headlessly in Vitest. One wiring phase owns the scene and plugs the
modules in through `register(scene)` functions. Art is code-drawn pixel art from Python + Pillow
scripts.

## GDD Reference
Path: `docs/gdd/`
Slice criterion: three levels, score and lives on the HUD, retry from results.

## Runtime And Scenes
- `src/main.ts` — boots Phaser with `PlayScene` (scaffold creates it; wiring owns its contents).
- `src/scenes/PlayScene.ts` — the one scene; calls each module's `register(scene)`.

## Module Design
- `src/rules/drop.ts` — Drop system: overlap, trim, miss, perfect drop.
- `src/rules/score.ts` — Scoring and Lives systems: points, combo, lives, run end.
- `src/levels/loader.ts` — loads and validates `data/levels/*.json` against the schema.
- `src/fx/*.ts` — juice: hit-stop, sparks, flash, combo label, miss tumble.
- `src/audio/*.ts` — procedural WebAudio blips; music stub.

## Content And Data
`data/levels/level-1.json` … `level-3.json`, validated by `src/contracts/level-schema.ts`.

## Asset Pipeline
`code-raster` for every slice sprite (pixel art), drawn by owned scripts under `tools/art/`. The
style lock comes first; every other family depends on it. Sparks are `procedural`.

## File Structure
```
package.json, tsconfig.json, vite.config.ts, index.html          [p1]
scripts/screenshot.mjs, smoke/run.mjs, smoke/checks/boot.mjs      [p1]
src/main.ts, src/scenes/PlayScene.ts (placeholder)                [p1]
src/contracts/types.ts         — Block, DropResult, RunState            [p2]
src/contracts/level-schema.ts  — Level type + validateLevel()           [p2]
assets/style/palette.json, style-rules.md, style-lock.png         [p3]
tools/art/style.py                                                [p3]
src/rules/drop.ts              — resolveDrop()                          [p4a]
tests/rules/drop.test.ts                                          [p4a tests]
src/rules/score.ts             — applyDrop(), initialRun()              [p4b]
tests/rules/score.test.ts                                         [p4b tests]
assets/sprites/blocks/*.png, assets/sprites/crane/*.png           [p4c]
tools/art/blocks.py, tools/art/crane.py                           [p4c]
assets/ui/*.png, tools/art/ui.py                                  [p4d]
data/levels/level-1.json … level-3.json                           [p5]
src/levels/loader.ts           — loadLevels()                           [p5]
tests/levels/loader.test.ts                                       [p5 tests]
src/scenes/PlayScene.ts        — scene contents (shared from p1)        [p6]
src/scenes/register.ts         — calls each module's register()         [p6]
smoke/checks/drop.mjs          — boots, taps, expects a landed block    [p6]
src/fx/hitstop.ts, src/fx/sparks.ts, src/fx/combo-label.ts        [p7a]
src/audio/blips.ts, src/audio/music-stub.ts                       [p7b]
```

## Interface Definitions
- `resolveDrop(top: Block, falling: Block): DropResult` — `DropResult = { kind: "miss" } |
  { kind: "land", block: Block, perfect: boolean }`. Overlap under 4 px is a miss; within 3 px of
  aligned is perfect and keeps the full width.
- `initialRun(): RunState` — `{ score: 0, combo: 0, lives: 3, over: false }`.
- `applyDrop(run: RunState, result: DropResult): RunState` — pure; never mutates `run`.
- `validateLevel(raw: unknown): Level | { error: string }`.
- Every feature module exports `register(scene: PlayScene): void`.

## Implementation Phases
- **p1 Scaffold** (scaffold) — config, Vite, screenshot and smoke harness, placeholder scene.
- **p2 Contracts** (contracts) — shared types and level schema. Depends on: p1.
- **p3 Style lock** (assets) — palette, rules note, reference sheet. Depends on: none.
- **p4a Drop rules** (gameplay, high risk) — overlap math. Depends on: p2. gdd_refs: Drop.
- **p4b Score and lives** (gameplay) — Depends on: p2. gdd_refs: Scoring, Lives.
- **p4c Block and crane art** (assets) — Depends on: p3.
- **p4d HUD art** (assets) — Depends on: p3.
- **p5 Levels** (content) — level files and loader. Depends on: p2. gdd_refs: Levels.
- **p6 Greybox wiring** (wiring) — scene and registration. Depends on: p4a, p4b, p4c, p4d, p5.
- **p7a Juice** (juice) — Depends on: p6. gdd_refs: Juice.
- **p7b Audio** (audio) — Depends on: p6. gdd_refs: Audio.

## Parallel Waves
| Wave | Phases |
|---|---|
| 1 | p1, p3 |
| 2 | p2, p4c, p4d |
| 3 | p4a, p4b, p5 |
| 4 | p6 |
| 5 | p7a, p7b |

**Critical path:** p1 → p2 → p4a → p6 → p7a

## Game Build Manifest
```yaml
commands:
  install: "npm ci"
  run: "npm run dev"
  test: "npx vitest run"
  test_one: "npx vitest run {files}"
  typecheck: "npx tsc --noEmit"
  build: "npx vite build"
  export: "npx vite build"
  smoke: "node smoke/run.mjs"
  screenshot: "node scripts/screenshot.mjs"
phases:
  - id: p1
    name: Scaffold
    kind: scaffold
    depends_on: []
    owns: ["package.json", "tsconfig.json", "vite.config.ts", "index.html", "scripts/**", "smoke/run.mjs", "smoke/checks/boot.mjs", "src/main.ts", "src/scenes/PlayScene.ts"]
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
    test_focus: "none — verified by asset QA"
    playtest_focus: "none — not playable yet"
  - id: p4a
    name: Drop rules
    kind: gameplay
    risk: high
    depends_on: [p2]
    owns: ["src/rules/drop.ts"]
    tests: ["tests/rules/drop.test.ts"]
    gdd_refs: ["docs/gdd/03-systems.md#drop"]
    test_focus: "overlap and trim, miss under 4 px, perfect within 3 px, boundary values"
    playtest_focus: "none — covered at loop-playable"
  - id: p4b
    name: Score and lives
    kind: gameplay
    depends_on: [p2]
    owns: ["src/rules/score.ts"]
    tests: ["tests/rules/score.test.ts"]
    gdd_refs: ["docs/gdd/03-systems.md#scoring", "docs/gdd/03-systems.md#lives"]
    test_focus: "points, combo growth and reset, lives, run end at 0"
    playtest_focus: "none — covered at loop-playable"
  - id: p4c
    name: Block and crane art
    kind: assets
    depends_on: [p3]
    owns: ["assets/sprites/**", "tools/art/blocks.py", "tools/art/crane.py"]
    gdd_refs: ["docs/gdd/06-art-audio-juice.md#asset-list-slice"]
    test_focus: "none — verified by asset QA"
    playtest_focus: "blocks and crane readable at 1x on the navy background"
  - id: p4d
    name: HUD art
    kind: assets
    depends_on: [p3]
    owns: ["assets/ui/**", "tools/art/ui.py"]
    gdd_refs: ["docs/gdd/06-art-audio-juice.md#asset-list-slice"]
    test_focus: "none — verified by asset QA"
    playtest_focus: "digits and hearts readable at 1x"
  - id: p5
    name: Levels
    kind: content
    depends_on: [p2]
    owns: ["data/levels/*.json", "src/levels/loader.ts"]
    tests: ["tests/levels/loader.test.ts"]
    gdd_refs: ["docs/gdd/03-systems.md#levels"]
    test_focus: "all three levels validate; invalid level is rejected"
    playtest_focus: "none — covered at slice"
  - id: p6
    name: Greybox wiring
    kind: wiring
    depends_on: [p4a, p4b, p4c, p4d, p5]
    owns: ["src/scenes/register.ts", "smoke/checks/drop.mjs"]
    shared: ["src/scenes/PlayScene.ts"]
    gdd_refs: ["docs/gdd/01-vision.md#vertical-slice"]
    test_focus: "smoke: boot, tap, a block lands"
    playtest_focus: "tap drops a block; score and lives update; retry works"
  - id: p7a
    name: Juice
    kind: juice
    depends_on: [p6]
    owns: ["src/fx/**"]
    gdd_refs: ["docs/gdd/06-art-audio-juice.md#juice"]
    test_focus: "none — playtest"
    playtest_focus: "hit-stop and sparks visible on landing; flash and +N on perfect"
  - id: p7b
    name: Audio
    kind: audio
    depends_on: [p6]
    owns: ["src/audio/**"]
    gdd_refs: ["docs/gdd/06-art-audio-juice.md#audio"]
    test_focus: "none — playtest"
    playtest_focus: "needs-human: land and perfect blips audible"
playtest_checkpoints:
  - name: loop-playable
    after: [p6]
    verifies: "one full run: drops land and trim, a miss costs a life, results screen and retry"
  - name: slice
    after: [p7a, p7b]
    verifies: "three levels clear in order; juice readable on landing and perfect drops"
assets:
  - { id: style-lock, path: assets/style/style-lock.png, kind: style-lock, method: code-raster, slice: true, depends_on: [], phase: p3 }
  - { id: blocks, path: assets/sprites/blocks/blocks.png, kind: sprite, method: code-raster, slice: true, depends_on: [style-lock], phase: p4c }
  - { id: crane, path: assets/sprites/crane/crane.png, kind: animation, method: code-raster, slice: true, depends_on: [style-lock], phase: p4c }
  - { id: hud, path: assets/ui/hud.png, kind: ui, method: code-raster, slice: true, depends_on: [style-lock], phase: p4d }
  - { id: sparks, path: src/fx/sparks.ts, kind: vfx, method: procedural, slice: true, depends_on: [style-lock], phase: p7a }
```

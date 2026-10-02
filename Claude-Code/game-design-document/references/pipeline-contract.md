# Game Pipeline Contract

The shared agreement between `game-design-document` → `game-architecture-blueprint` →
`game-dev-orchestrator`. The same file ships in all three skills — keep the copies identical, so
every stage agrees on what the others produce and expect.

Don't use `claude-spec`, `claude-architect` or `claude-build` for a game. Those skills assume
software products (user stories, APIs, data models, deployment) and have no concept of feel,
content volume, playtests, or an asset pipeline.

## Stage boundaries

| Stage | Skill | Owns | Does not own |
|---|---|---|---|
| Design | `game-design-document` | WHAT / WHY / feel: pillars, loops, systems, content volume, juice intent, slice, non-goals | Engine choice as "the answer", file layout, code, produced assets |
| Architecture | `game-architecture-blueprint` | HOW: engine/runtime, scenes/entities, input, data formats, asset pipeline, Asset Manifest, phases, ownership, Game Build Manifest, pinned commands | Inventing GDD intent; game code; producing art |
| Build | `game-dev-orchestrator` | Implementation by a team of Claude Code subagents: spec-first tests, gameplay, content, assets, review, integration, playtests, docs | Redesigning the GDD or the architecture |

Each stage stops at its boundary. When a later stage finds a gap that belongs to an earlier one
(a missing rule, a contract nobody defined), it goes back to the user rather than filling the gap
itself — a silent guess made downstream is invisible to everyone upstream.

## Doc paths (relative to the project root)

| Kind | GDD | Architecture | Build progress |
|---|---|---|---|
| New game | `docs/gdd/` | `docs/game-architecture/` | `docs/progress/game-build-progress.md` |
| Feature / mode in an existing game | `docs/gdd/features/{name}/` | `docs/gdd/features/{name}/architecture/` | `docs/gdd/features/{name}/progress/game-build-progress.md` |
| Ad-hoc task (`game-dev-orchestrator` light mode) | — | — | `docs/plans/{slug}.md` (only when worth keeping) |

A user-named location always wins; keep the same internal file names inside it.

## GDD references

Cite the GDD by **file + section or system name** (`gdd_refs`), e.g.
`docs/gdd/03-systems.md#combat`. Don't mint `US-*` / `AC-*` / `BR-*` IDs for games.

Anchors are the heading slug: lowercase, spaces to hyphens, punctuation dropped (`## Asset list
(slice)` → `#asset-list-slice`). Keep headings stable once the architecture cites them, because
renaming one silently breaks every reference to it.

Tests carry **gdd tags** so the build can machine-check coverage: a ref normalizes to
`gdd:<file stem>#<anchor>` (`docs/gdd/03-systems.md#combat` → `gdd:03-systems#combat`), and the
test-writer puts that tag in the test name or a comment on the test.

## What the GDD leaves for architecture

- Pillars, non-goals, core loop, camera/control intent.
- Systems with verbs, rules, failure states and connections (`hypothesis` / `prototyped` /
  `locked`). Rules that will be tested state real numbers or name the data file that holds them.
- Content volume (counts or procedural constraints).
- Art/audio/juice direction, planning asset lists, and how art will realistically be produced.
- Vertical slice definition and cut-first list.
- Constraints (platform, session, engine *preferences* only).
- Open questions that are still real gaps.

## What architecture leaves for build

- Header lines: `Mode: PM | Developer` and `Scale: jam | vertical-slice | shippable-indie`.
- Engine, platform, runtime/scene model.
- A complete File Structure (code **and** assets **and** tests) with purpose and owner — this is
  the ownership map.
- Interface contracts at every seam where two workers meet, at the depth an agent that can't ask
  back needs.
- Granular phases with depends-on, produces, parallel opportunities, test focus, playtest focus,
  **gdd_refs**.
- Playtest checkpoints, each naming what a check there must prove.
- Pinned `run` / `test` / `test_one` / `smoke` / `screenshot` commands (TBD only when a scaffold
  phase sets them), plus `typecheck`, `build` and `export` where the stack has them.
- A way for a headless agent to *see* the game: a screenshot or browser/simulator smoke path.
- A Parallel Waves table naming the critical path.
- The **Game Build Manifest** and **Asset Manifest** (below) for any multi-phase build, passing
  `check_manifest.py` with 0 errors.
- GDD reference path(s).

## What build honors

- The manifest (when present and consistent with the prose) is the plan: phase DAG, ownership,
  commands, assets. On a prose↔manifest conflict the prose wins; the conflict is noted and, if it
  blocks assignment, taken to the user.
- `gdd_refs` go into every test-writer, implementer, content-author, asset-artist, reviewer,
  integration-tester and playtester brief.
- No invented player verbs, scoring or feel, and no redesign. Gaps stop the affected phase and go
  to the user.
- Disjoint file **and** asset ownership: no two concurrent workers edit the same file; `shared`
  files (style lock, autoloads, scene roots, atlases, import config) have one writer at a time.
- Spec-first verification for `gameplay` phases: tests are written from the GDD by a worker that
  never sees the implementation, committed before implementation starts, and the implementer can't
  edit them. Tests carry gdd tags, and `check_traceability.py` confirms every cited ref of a tested
  phase is covered before the build is called done.
- Only the build lead runs git: a commit locks each phase's tests, and another lands each verified
  phase.
- MUST-FIX and SHOULD-FIX review findings both block a phase.
- Parallelism has no fixed cap: the build launches every ready phase with disjoint `owns` at once,
  bounded only by Claude Code's concurrent-subagent limit. So **the blueprint's shape sets the
  build speed** — architecture should split work into as many independent, disjoint slices as the
  design honestly allows.
- Asset workers follow `game-dev-orchestrator/references/asset-production.md` for the row's
  `method`, and verify by viewing the produced image.

## Game Build Manifest

A machine-readable projection of the architecture's File Structure and phases, written **last**,
after the prose is final. The prose stays the source of truth: if a field can't be filled without
inventing something the prose doesn't say, the prose is incomplete — fix the prose first.

It lives in a fenced ```` ```yaml ```` block under a `## Game Build Manifest` heading in
`implementation-plan.md` (new games) or `design.md` (small features). A trivial single-phase
feature may skip the block and state `owns` / `tests` / `gdd_refs` in the phase prose.

Write it in a simple YAML subset — block mappings, block lists, or one-line `[a, b]` / `{k: v}`
flow collections, plain or quoted scalars, `#` comments. No anchors, tags, multi-line strings, or
flow collections that wrap onto a second line. That keeps `check_manifest.py` working without
PyYAML.

```yaml
commands:
  install: "npm ci"                          # optional
  run: "npm run dev"
  test: "npx vitest run"                     # full suite
  test_one: "npx vitest run {files}"         # {files} = space-separated test paths
  typecheck: "npx tsc --noEmit"              # or "none" for untyped stacks
  build: "npx vite build"                    # optional
  export: "npx vite build"                   # optional: the shippable build
  smoke: "node smoke/run.mjs"                # agent-checkable proof the game boots and plays
  screenshot: "node scripts/screenshot.mjs"  # saves PNGs an agent can view
phases:
  - id: p1
    name: Scaffold                           # MUST match the prose phase name
    kind: scaffold
    depends_on: []
    owns: ["package.json", "vite.config.ts", "scripts/screenshot.mjs", "smoke/run.mjs"]
    tests: []
    gdd_refs: []
    test_focus: "build, smoke and screenshot work on an empty scene"
    playtest_focus: "none — not playable yet"
  - id: p3a
    name: Drop rules
    kind: gameplay
    depends_on: [p2]
    owns: ["src/rules/drop.ts"]
    tests: ["tests/rules/drop.test.ts"]
    shared: []
    gdd_refs: ["docs/gdd/03-systems.md#drop"]
    test_focus: "overlap and trim, miss threshold, perfect drop, boundaries"
    playtest_focus: "none — covered at loop-playable"
    risk: high                               # optional: normal (default) | high
    flags: []                                # optional
playtest_checkpoints:
  - name: loop-playable
    after: [p5]
    verifies: "one full run: drops land and trim, a miss costs a life, retry works"
assets:
  - { id: style-lock, path: assets/style/style-lock.png, kind: style-lock, method: code-raster, slice: true, depends_on: [], phase: p2b }
```

**Phase `kind`** decides how the build verifies the phase:

| kind | What it is | How build verifies it |
|---|---|---|
| `scaffold` | Engine project, config, tooling, the smoke and screenshot harness | build + smoke + screenshot; review |
| `contracts` | Shared types, interfaces, event names, data schema | typecheck; review |
| `gameplay` | Rules modules and systems with deterministic behavior | spec-first tests → implement → review; playtest if `playtest_focus` is set |
| `content` | Level, wave, table and curve instance files against an existing schema | schema validation (tests or load-smoke); review |
| `assets` | Art per the Asset Manifest, the style lock first | produce → view-and-compare QA → asset review; screenshot smoke once wired |
| `audio` | Procedural SFX, wired external files, or stubs | format/duration checks; review; "sounds right" is `needs-human` |
| `juice` | Hit-stop, shake, particles, tweens, haptics | review; playtest with screenshots captured at the moment |
| `ui` | HUD, menus, flow screens | behavior tests where there are rules; review; screenshot playtest |
| `wiring` | The one phase that owns a hub (scene root, entry point, registry) and plugs modules in | build + smoke + screenshot; review |
| `playtest` | A dedicated playtest gate with no production files | playtester against the checkpoint criteria |
| `docs` | Documentation only | review against the game |

**Field rules**

- `id` unique; `depends_on` references existing ids; no cycles.
- `owns` (production files and assets) and `tests` (test files) are globs that trace to the File
  Structure. No path appears in two phases, and no path is in both `owns` and `tests`. Test files
  are owned separately because the build gives them to a different worker than the code.
- `gameplay` phases have at least one `tests` entry.
- A file touched by more than one phase goes in `shared` for every phase except the one that
  creates it (which lists it in `owns`). That creator must be an upstream dependency of every
  sharer. A file shared by three or more phases is a hub — restructure around a `wiring` phase.
- `gdd_refs` cite real GDD files and sections; the validator checks that the files exist.
- **Cross-phase calls.** If a phase's code calls a module another phase implements, either list
  that phase in `depends_on`, or state in the phase notes that its tests fake the callee against
  its contract and that it's wired up for real at the wiring phase or a checkpoint.
- `risk: high` marks phases where a subtle mistake is expensive: physics and collision, save/load,
  economy and progression math, netcode, deterministic simulation or procedural generation, input
  timing. The build reviews these with a panel and reviews their tests before implementation.
- `commands.run`, `test`, `smoke` and `screenshot` are required. `"TBD — set in scaffold"` is
  allowed only when a `scaffold` phase exists to set them.

**Asset Manifest** (`assets:`): one row per slice asset with `id`, `path`, `kind`, `method`,
`slice`, `depends_on` (asset ids; the style lock first) and `phase` (the owning phase, whose
`owns` covers the path). Two assets that share a sheet or atlas must not be in parallel phases.

**The `smoke` and `screenshot` commands** prove the game actually runs, not just that unit tests
pass. They boot the game, perform the core verb, exit non-zero on failure, and save screenshots to
a known path (`tmp/playtest/`). Agents lean on them at playtest checkpoints, because unit tests
can all pass while the assembled game shows a blank canvas. The smoke runner discovers check files
from a folder, so each phase adds its own check instead of editing a shared script.

## Asset production methods

Claude Code has no built-in image generator, so every asset row declares how it will be produced.
The build routes on this field.

| `method` | Meaning | Good for |
|---|---|---|
| `code-vector` | Hand-authored SVG (or engine vector shapes) written as text | Flat/geometric characters, UI, icons, logos, clean backgrounds |
| `code-raster` | A script (Python + Pillow, Node canvas, etc.) draws PNGs/sprite sheets pixel by pixel | Pixel art, tiles, sprite sheets, animation frames, palette-swapped variants |
| `procedural` | Drawn at runtime by game code (shapes, particles, shaders, tweens) — no file on disk | VFX, particles, trails, screen flashes, simple geometric actors |
| `image-gen` | An image-generation MCP server or API available in the session | Painterly/illustrated/photoreal art — only if such a tool actually exists |
| `greybox` | Deliberate placeholder (flat colored shapes + labels) | Early phases, jams, anything the slice doesn't need polished |
| `external` | Supplied by the user or a human artist/asset pack; build only wires it | Art the team already has or will buy |

Architecture chooses the method from the GDD art direction and what's realistic. If the GDD style
needs `image-gen` but no generator is known to exist, record it as a risk and plan a `code-*` or
`greybox` fallback rather than pretending the art will appear.

Audio follows the same idea: `procedural` (e.g. jsfxr-style synthesized SFX, WebAudio tones),
`external`, or `stub` (silent placeholder files + a flagged gap). Never claim audio exists that
wasn't produced.

## Skip paths

- **GDD optional** when the user already has architecture-ready design docs (pillars, loop,
  systems with rules, volume, slice). Polish or hand off; don't re-interview for sport.
- **Architecture optional** for work small enough that `game-dev-orchestrator` light mode can plan
  it in a few lines: a bug, a tuning pass, a refactor, an asset tweak, a feature that touches a
  handful of files with no new scenes, persistence or asset families. Anything bigger gets a
  blueprint first.
- Art direction lives in GDD `06-art-audio-juice.md` (or the lean equivalent). Architecture turns
  it into an Asset Manifest. Don't use `design-system` or `frontend-design` for in-game art
  (they're for app UIs) — though a web game's menus may borrow from `frontend-design` if the user
  wants.

## Handoffs

- After the GDD: "Next is technical design — run `/game-architecture-blueprint`."
- After the architecture: "Next is the build — run `/game-dev-orchestrator`."

# Game Pipeline Contract

Shared expectations across `game-design-document` → `game-architecture-blueprint` → `game-dev-orchestrator`. The same file ships in all three skills; keep the copies identical.

Don't use `requirement-gathering`, `solution-architect`, `dev-team`, or `fable-dev-team` for a game. Those skills assume software products (user stories, APIs, data models, deployment) and have no concept of feel, content volume, playtests, or an asset pipeline.

## Stage boundaries

| Stage | Skill | Owns | Does not own |
|-------|-------|------|--------------|
| Design | `game-design-document` | WHAT / WHY / feel: pillars, loops, systems, content volume, juice intent, slice, non-goals | Engine choice as "the answer", file layout, code, produced assets |
| Architecture | `game-architecture-blueprint` | HOW: engine/runtime, scenes/entities, input, data formats, asset pipeline, Asset Manifest, phases, ownership, Game Build Manifest, run/test/export commands | Inventing GDD intent; game code; producing art |
| Build | `game-dev-orchestrator` | Coordinated implementation by Claude Code subagents: gameplay, content, assets, tests, playtests | Redesigning GDD or architecture |

## Doc paths (relative to the project root)

| Kind | GDD | Architecture | Progress |
|------|-----|--------------|----------|
| New game | `docs/gdd/` | `docs/game-architecture/` | `docs/progress/game-build-progress.md` |
| Feature / mode in an existing game | `docs/gdd/features/{name}/` | `docs/gdd/features/{name}/architecture/` | `docs/gdd/features/{name}/progress/game-build-progress.md` |

Honor a user-named root; keep the same internal filenames.

## What the GDD must leave for architecture

- Pillars, non-goals, core loop, camera/control intent
- Systems with verbs, rules, failure states, connections (`hypothesis` / `prototyped` / `locked`)
- Content volume (counts or procedural constraints)
- Art/audio/juice direction, planning asset lists, and how art will realistically be produced
- Vertical slice definition and cut-first list
- Constraints (platform, session, engine *preferences* only)
- Open questions that are still real gaps

Cite the GDD by **file + section or system name** (`gdd_refs`), e.g. `docs/gdd/03-systems.md#combat`. Don't mint `US-*` / `AC-*` / `BR-*` IDs for games.

## What architecture must leave for build

- Mode line: `Mode: PM | Developer`
- Production scale: `Scale: jam | vertical-slice | shippable-indie`
- Engine, platform, runtime/scene model
- Complete file structure (code **and** assets) with purpose + owner
- Implementation phases with depends-on, produces, parallel opportunities, test focus, playtest focus, **gdd_refs**
- Interface contracts at multi-worker and high-risk seams
- **Game Build Manifest** for multi-phase work (`commands`, `owns`, `shared`, `depends_on`, `gdd_refs`, `kind`, `playtest_checkpoints`)
- **Asset Manifest** (`assets:`): id, path, kind, production `method`, slice vs ship, `depends_on`, owning phase
- Pinned `run` / `test` / `test_one` / `export` / `smoke` (TBD only for the scaffold phase)
- A way for a headless agent to *see* the game: a screenshot or browser/simulator smoke path
- GDD reference path(s)

## Asset production methods

Claude Code has no built-in image generator, so every asset row declares how it will be produced. The build stage routes on this field.

| `method` | Meaning | Good for |
|---|---|---|
| `code-vector` | Hand-authored SVG (or engine vector shapes) written as text | Flat/geometric characters, UI, icons, logos, clean backgrounds |
| `code-raster` | A script (Python + Pillow, Node canvas, etc.) draws PNGs/sprite sheets pixel by pixel | Pixel art, tiles, sprite sheets, animation frames, palette-swapped variants |
| `procedural` | Drawn at runtime by game code (shapes, particles, shaders, tweens) — no file on disk | VFX, particles, trails, screen flashes, simple geometric actors |
| `image-gen` | An image-generation MCP server or API available in the session | Painterly/illustrated/photoreal art — only if such a tool actually exists |
| `greybox` | Deliberate placeholder (flat colored shapes + labels) | Early phases, jams, anything the slice doesn't need polished |
| `external` | Supplied by the user or a human artist/asset pack; build only wires it | Art the team already has or will buy |

Architecture chooses the method from the GDD art direction and what's realistic. If the GDD style needs `image-gen` but no generator is known to exist, record it as a risk and plan a `code-*` or `greybox` fallback rather than pretending the art will appear.

Audio follows the same idea: `procedural` (e.g. jsfxr-style synthesized SFX, WebAudio tones), `external`, or `stub` (silent placeholder files + a flagged gap). Never claim audio exists that wasn't produced.

## What build must honor

- Prefer the Game Build Manifest + Asset Manifest for DAG, ownership, and commands when present and consistent with prose. On prose↔manifest conflict, trust prose, note it, ask if it blocks assignment.
- Pass `gdd_refs` into test-author, implementer, content-author, asset-artist, reviewer, and playtester prompts.
- Don't invent player verbs, scoring, or feel. Stop and ask when blocked.
- Disjoint file **and** asset ownership; serialize `shared` files (style-lock, autoloads, atlases, import config).
- Parallelism has no fixed cap: the orchestrator launches every ready slice with disjoint `owns` at once, bounded only by Claude Code's concurrent-subagent limit. So **the blueprint's shape sets the build speed** — architecture should split work into as many independent, disjoint slices as the design honestly allows. Rules-TDD is sequential within a slice, pipelined across slices. Playtest only a stable snapshot.
- Asset workers follow `game-dev-orchestrator/references/asset-production.md` for the row's `method`, and verify by viewing the produced image.

## Skip paths

- GDD optional when the user already has architecture-ready design docs (pillars, loop, systems with rules, volume, slice). Polish or hand off; don't re-interview for sport.
- Architecture optional only for a trivial one-file tweak the user wants coded immediately. The orchestrator still stops if multi-file or asset ownership is unclear.
- Art direction lives in GDD `06-art-audio-juice.md` (or the lean equivalent). Architecture turns it into an Asset Manifest. Don't use `design-system` or `frontend-design` for in-game art (they're for app UIs) — though a web game's menus may borrow from `frontend-design` if the user wants.

## Handoff phrases

- After GDD: next is `game-architecture-blueprint` (`/game-architecture-blueprint`).
- After architecture: next is `game-dev-orchestrator` (`/game-dev-orchestrator`).

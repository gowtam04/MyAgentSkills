# Game Pipeline Contract

Shared expectations across `game-design-document` → `game-architecture-blueprint` → `game-dev-orchestrator`.

Do not use `product-discovery`, `architecture-blueprint`, or `build-orchestrator` for a game. Those skills assume software products (US/AC/BR IDs, APIs, deployment budget tiers).

## Stage boundaries

| Stage | Skill | Owns | Does not own |
|-------|--------|------|----------------|
| Design | `game-design-document` / `/game-design-document` | WHAT / WHY / feel: pillars, loops, systems, content volume, juice intent, slice, non-goals | Engine choice as "the answer", file layout, code, generated assets |
| Architecture | `game-architecture-blueprint` / `/game-architecture-blueprint` | HOW: engine/runtime, scenes/entities, input, data formats, asset pipeline, Asset Manifest, phases, ownership, Game Build Manifest, run/test/export commands | Inventing GDD intent; game code; generating art |
| Build | `game-dev-orchestrator` / `/game-dev-orchestrator` | Coordinated implementation from approved game architecture: gameplay, content, assets, tests, playtests | Redesigning GDD or architecture |

## Doc paths

| Kind | GDD | Architecture | Progress |
|------|-----|--------------|----------|
| New game | `/docs/gdd/` | `/docs/game-architecture/` | `/docs/progress/game-build-progress.md` |
| Feature / mode in an existing game | `/docs/gdd/features/{name}/` | `/docs/gdd/features/{name}/architecture/` | `/docs/gdd/features/{name}/progress/game-build-progress.md` |

Honor a user-named root; keep the same internal filenames.

## What the GDD must leave for architecture

- Pillars, non-goals, core loop, camera/control intent
- Systems with verbs, rules, failure states, connections (hypothesis vs prototyped vs locked)
- Content volume (counts or procedural constraints)
- Art/audio/juice direction and planning asset lists
- Vertical slice definition and cut-first list
- Constraints (platform, session, engine *preferences* only)
- Open questions that are still real gaps

Cite GDD by **file + section or system name** (`gdd_refs`). Do not mint `US-*`/`AC-*`/`BR-*` for games.

## What architecture must leave for build

- Mode line: `Mode: PM | Developer`
- Production scale: `Scale: jam | vertical-slice | shippable-indie`
- Engine, platform, runtime/scene model
- Complete file structure (code **and** assets) with purpose + owner
- Implementation phases with depends-on, produces, parallel opportunities, test focus, playtest focus, **gdd_refs**
- Interface contracts at multi-worker and high-risk seams
- **Game Build Manifest** for multi-phase work (`commands`, `owns`, `shared`, `depends_on`, `gdd_refs`, `kind`, `integration_checkpoints` / playtest checkpoints)
- **Asset Manifest** (`assets:`): id, path, kind, specialist skill, slice vs ship, `depends_on`, owning phase
- Pinned `run` / `test` / `test_one` / `export` (or TBD only for scaffold)
- GDD reference path(s)

## What build must honor

- Prefer Game Build Manifest + Asset Manifest for DAG, ownership, and commands when present and consistent with prose. On prose↔manifest conflict, trust prose, note it, ask if it blocks assignment.
- Pass `gdd_refs` into test-author, implementer, content-author, asset-artist, reviewer, and playtester prompts.
- Do not invent player verbs, scoring, or feel. Stop and ask when blocked.
- Disjoint file **and** asset ownership; serialize `shared` (style-lock, autoloads, atlases, import config).
- Parallelism: **split caps** — code track vs asset-artists (numbers live in `/game-dev-orchestrator` Concurrency). Disjoint `owns` still bind each track; artists do not consume implementer slots. Rule TDD sequential per slice. Playtest only on a stable snapshot of that scene/scope.
- Asset workers load `game-asset-core` plus the specialist named in the Asset Manifest. Do not copy those skills into this contract.

## Skip paths

- GDD optional when the user already has architecture-ready design docs (pillars, loop, systems with rules, volume, slice). Polish or hand off; do not re-interview for sport.
- Architecture optional only for a trivial one-file tweak the user wants coded immediately. Orchestrator still stops if multi-file or asset ownership is unclear.
- Art-direction docs live in GDD `06-art-audio-juice.md` (or lean equivalent). Architecture turns that into an Asset Manifest. Do not invoke `/design-system` or `/frontend-design` for game art.

## Handoff phrases

- After GDD: next is `/game-architecture-blueprint` (skill: `game-architecture-blueprint`).
- After architecture: next is `/game-dev-orchestrator` (skill: `game-dev-orchestrator`).

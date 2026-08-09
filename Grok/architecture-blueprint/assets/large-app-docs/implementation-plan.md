# Implementation Plan

Granular, build-order phases. Prefer more phases with smaller scope over fewer with larger scope — a phase should touch one layer or one functional domain.

This file is the primary task graph for `/build-orchestrator`.

## File Structure (Ownership Map)

Complete tree of files to create or modify. Each file: purpose + owning component. No two parallel phases should write the same file.

```text
src/
  ...
tests/
  ...
```

## Phase N: {Name}

- **What gets built:** specific files/components
- **Depends on:** which prior phase(s) must be complete
- **Produces:** what interfaces/files are available after this phase
- **Parallel opportunities:** only fully disjoint write sets. List each parallel slice with explicit file globs (or point at manifest `owns`). Collision paths go in `shared`, never under two parallel slices. If nothing is truly independent, write "none — sequential."
- **Test focus:** what the phase's tests verify
- **Requirement refs:** US-/AC-/BR- IDs this phase satisfies (cite by section/quote and note the gap if the requirements lack stable IDs — do not fabricate)
- **Success criteria** *(Developer mode)*: concrete, reviewable outcomes beyond "tests pass"
- **Review checklist / test split** *(Developer mode)*: unit vs integration, mocked vs real, review gates

(Repeat for each phase.)

## Typical Full-App Shape (adapt)

1. Scaffolding / project setup
2. Data model / migrations
3. Auth / permissions
4. Core business logic
5. API layer
6. Frontend foundation
7. Feature UI screens
8. Integration & polish

## Integration Seams (call out as phases or explicit sub-steps)

- When an API first connects to services and data
- When a UI first consumes real API contracts
- When auth or permissions cross multiple layers
- Final E2E / main workflow verification

## Build Manifest

Machine-readable appendix for `/build-orchestrator`. **Prose phases and File Structure above are the source of truth.** Generate this last; on conflict, fix the prose first. Required for multi-phase builds.

```yaml
commands:                     # mirror Build & Test Commands in deployment.md (keep identical)
  test: "..."
  test_one: "..."
  typecheck: "..."
  build: "..."
phases:
  - id: p1
    name: Scaffolding         # MUST match the prose phase name exactly
    depends_on: []
    owns:   ["..."]           # globs from the File Structure; no two phases overlap
    shared: []                # files touched by >1 phase — collision points for parallel builds
    requirement_refs: []      # often empty for scaffold
    test_focus: "tooling smoke if any"
    flags: [scaffold]
  - id: p2
    name: Data Model
    depends_on: [p1]
    owns:   ["src/models/**", "migrations/**"]
    shared: ["src/db/index.ts"]
    requirement_refs: [US-3, AC-3.1, BR-2]
    test_focus: "entity validation, relationship constraints"
    flags: []
integration_checkpoints:
  - after: [p5]
    name: backend-stack-e2e
    verifies: "auth + core API end-to-end against a real DB"
```

Field rules:

- `owns` is the ownership partition: every glob traces to the File Structure; no two phases' `owns` overlap. Multi-phase files go in `shared`.
- `commands` mirrors `deployment.md`; if unknown until scaffolding, write the intended command and mark `TBD — set in scaffold phase`.
- `requirement_refs` cite IDs from requirements docs; flag the gap rather than fabricating refs.

## Orchestrator Notes

- **Mode** and **Budget Tier** from `overview.md` control TDD rigor in `/build-orchestrator` (PM/small → lighter cycle; Developer/large → full red→review→impl→review→regression).
- Prefer this Build Manifest for phase DAG, ownership, commands, and requirement refs when present.
- Each phase becomes worker tasks with strict file ownership; serialize or isolate work on `shared` files.
- Parallelism is capped by disjoint `owns` sets (not by wishful concurrency). Clear partitions enable 3–5 worktree implementers on large builds; soft ownership forces sequential work.
- Use `todo_write` for orchestrator state and a human-readable progress file for the user.

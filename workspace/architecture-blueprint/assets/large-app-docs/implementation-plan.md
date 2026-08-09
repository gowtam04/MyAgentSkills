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
- **Parallel opportunities:** what within this phase can be built simultaneously (disjoint write sets only)
- **Test focus:** what the phase's tests verify
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

## Orchestrator Notes

- **Mode** and **Budget Tier** from `overview.md` control TDD rigor in `/build-orchestrator` (PM/small → lighter cycle; Developer/large → full red→review→impl→review→regression).
- Each phase becomes worker tasks with strict file ownership.
- Use `todo_write` for orchestrator state and a human-readable progress file for the user.

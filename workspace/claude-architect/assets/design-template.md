# {Feature Name} — Technical Design

Mode: PM | Developer  ← pick one; claude-build reads this line
Budget Tier: hobby | startup | scaling | enterprise

## Overview
What's being built and the key technical approach, in a few sentences.

## Requirements Reference
Path to the requirements this design is based on.

## Tech Stack
Languages, frameworks, key libraries; for an existing project, only what's new.
(Omit if nothing new.)

## Data Model
Entities, fields, relationships, constraints, indexes; migration/backfill notes.

## Component Design
Each component: responsibility (one sentence), interface, dependencies, location.

## API Design
Endpoints, request/response shapes, auth, errors. (Omit for non-API work.)

## File Structure
Every file to create or modify, with purpose, owning phase, and new/modified. Test files listed
next to the code they cover and owned separately. This is the ownership map.

## Interface Definitions
Contracts at every seam between phases — signatures, I/O types with field detail, error types,
behavior notes — at the depth an agent that can't ask back needs. Conventional internals can stay
light; Developer mode defaults to high detail everywhere.

## Implementation Phases
For each phase: kind, what gets built, tests, depends on, produces, test focus (citing AC IDs),
requirement refs, risk. Developer mode adds success criteria and a review/test split.
For a single-phase feature, state `owns` / `tests` / `requirement_refs` here and skip the manifest.

## Integration Checkpoints
Where independently built pieces first meet, and what each check proves.

## Parallel Waves
Wave → phases that can run together; name the critical path. (Omit for a single phase.)

## Build Manifest
Required for multi-phase work; schema in `references/pipeline-contract.md`; generated last;
validated with `scripts/check_manifest.py`.

```yaml
commands: { test: "...", test_one: "... {files}", typecheck: "...", build: "...", smoke: "..." }
phases:
  - id: p1
    name: ...
    kind: logic
    depends_on: []
    owns: ["..."]
    tests: ["..."]
    requirement_refs: [US-1, AC-1.1]
    test_focus: "..."
integration_checkpoints:
  - { name: ..., after: [p1], verifies: "..." }
```

## Technical Decisions
Significant choices: decision, alternatives, why, tradeoffs accepted.

**Defaults chosen on the user's behalf** (most expensive to change first):
| # | Default | Why | Affects | Change cost (expensive / moderate / cheap) |
|---|---|---|---|---|

## Deployment & Infrastructure
Restate the budget tier. Each concern with its choice and a one-line "why this fits the tier".
Pinned commands table (install, test, test_one, typecheck, build, smoke, and eval for AI features)
— the manifest mirrors it. End with a monthly cost bucket ($0 / ~$50 / ~$500 / ~$5k / $50k+).

## Code Conventions  *(Developer mode only — delete in PM mode)*
Naming, module boundaries, error handling and envelope shape, logging schema, lint stance,
transactions/concurrency, frontend state management.

## Testing Strategy  *(Developer mode only — delete in PM mode)*
Test levels per layer, framework, mocking policy, coverage bar, fixtures, eval harness wiring.

## Unresolved from Requirements
Requirement questions resolved here, ones still open, and (Developer mode, architect solo) choices
marked "Proposed — confirm with dev team".

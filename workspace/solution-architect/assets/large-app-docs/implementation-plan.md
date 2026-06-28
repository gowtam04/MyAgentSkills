# Implementation Plan

Granular, build-order phases. Prefer more phases with smaller scope over fewer with larger scope —
a phase should touch one layer or one functional domain.

## Phase N: {Name}
- **What gets built:** specific files/components
- **Depends on:** which prior phase(s) must be complete
- **Produces:** what interfaces/files are available after this phase
- **Parallel opportunities:** what within this phase can be built simultaneously
- **Test focus:** what the phase's tests verify
- **Requirement refs:** the requirement IDs (US-/AC-/BR-) this phase satisfies (cite by section/quote and note the gap if the requirements lack stable IDs)
- **Success criteria** *(Developer mode)*: concrete, reviewable outcomes beyond "tests pass"
- **Review checklist / test split** *(Developer mode)*: unit vs integration, mocked vs real, review gates

(Repeat for each phase. Typical full-app shape: scaffolding → data model → auth → core business
logic → API → frontend foundation → frontend screens → integration & polish. Adapt the count to
the actual work.)

## Integration Checkpoints
Name the seams where independently-built phases first meet, and what an end-to-end check there
verifies (e.g., after the backend stack is built, after the frontend connects to the API, final
E2E). These are where a builder needs an integration test rather than another unit test, and an
autonomous builder can't infer them reliably. They become the `integration_checkpoints` entries in
the Build Manifest below.

## Build Manifest
A machine-readable appendix that makes the phase DAG, file ownership, and runnable commands explicit
and parseable, for a consumer that can't ask back (an autonomous/agentic implementer reads it
directly instead of inferring the plan from prose).

**The prose above is the source of truth; this is a derived projection.** Ownership traces to the
File Structure (`component-design.md`); the DAG and requirement refs trace to the phases above.
Generate it last, after both are final, and keep it consistent — if a field can't be filled without
inventing something not in the prose, the prose is incomplete: fix it first. On conflict, the prose
wins. It's orthogonal to PM/Developer mode (both emit it for multi-phase builds). Required for
multi-phase builds; for a trivial single-phase design, inline the fields into the prose instead.

```yaml
commands:                     # mirror of deployment.md's Build & Test Commands (keep identical)
  test: "..."                 # full suite
  test_one: "..."             # run a single test file/glob (placeholder ok if templated)
  typecheck: "..."
  build: "..."
phases:
  - id: p2
    name: Data Model          # MUST match the prose phase name exactly
    depends_on: [p1]          # MUST match the prose "Depends on"
    owns:   ["src/models/**", "migrations/**"]   # globs from the File Structure; no two phases overlap
    shared: ["src/db/index.ts"]                  # files touched by >1 phase — collision points
    requirement_refs: [US-3, AC-3.1, BR-2]       # IDs this phase satisfies
    test_focus: "entity validation, relationship constraints"
    flags: [scaffold, ui, ai] # optional; presence signals scaffold / UI / AI-integration phases
integration_checkpoints:
  - after: [p5]               # phase ids that must complete first
    name: backend-stack-e2e
    verifies: "auth + core API end-to-end against a real DB"
```

Field rules:
- `owns` is the ownership partition: every glob traces to a file in the File Structure, no two
  phases overlap. Any file touched by more than one phase goes in `shared`, never in two `owns` —
  `shared` is the collision map a parallel build uses to serialize or isolate those files.
- `commands` mirrors `deployment.md`'s Build & Test Commands (the source of truth); keep identical.
  If a command isn't known yet (greenfield), write the intended command and mark it, e.g.
  `build: "TBD — set in scaffold phase"`.
- `requirement_refs` cite IDs from the requirements docs; flag the gap rather than fabricating refs
  if the requirements lack IDs.

# {Feature Name} — Technical Design

## Overview
Mode: PM | Developer  ← pick one; this line is how `dev-team` detects the mode
Budget Tier: hobby | startup | scaling | enterprise  ← from Phase 1; the deployment section must respect this
Brief summary of what's being built and the key technical approach.

## Requirements Reference
Path to the business requirements this design is based on: `[actual path used]`
(If an `agent-design/` directory informed this design, list its path here too.)

## Tech Stack
Languages, frameworks, and key libraries. For existing projects, note any additions.
(Omit for features that don't introduce new technology.)

## Data Model
Entities, fields, relationships, constraints. Include a simple ERD description or table.

## Component Design
Each component: responsibility, interface, dependencies.

## API Design
Endpoints, request/response shapes, auth patterns.
(Omit for non-API work.)

## File Structure
Complete file tree with descriptions. This is the ownership map — each file has one purpose,
no two builders should need to edit the same file.

## Interface Definitions
Key contracts between components — function signatures, types, error types.
Scale detail to complexity (high detail where a builder could plausibly get it wrong;
light detail for conventional patterns). In Developer mode, default to high detail.
If the consumer is an autonomous/agentic implementer that can't ask back, bias to high detail at
the seams regardless of mode — a silent guess at a seam is the most expensive kind.

## Implementation Phases
Ordered, granular, build-order phases. For each phase:
- What gets built (specific files/components)
- What it depends on (which prior phase)
- What it produces (interfaces/files available after)
- Parallel opportunities (what can be built simultaneously)
- Test focus (what the phase's tests verify)
- Requirement refs — the requirement IDs (US-/AC-/BR-) this phase satisfies
- (Developer mode) Success criteria — concrete reviewable outcomes beyond "tests pass"
- (Developer mode) Review checklist / test split — unit vs integration, mocked vs real, review gates

## Build Manifest  *(machine-readable appendix — required for multi-phase builds, optional/inline for a trivial single-phase feature)*
A derived projection of the File Structure (ownership) and Implementation Phases (DAG, refs); the
prose above stays the source of truth. It exists for an autonomous/agentic consumer that reads the
plan without asking back. Generate it last and keep it consistent with the prose. The `commands`
block mirrors the commands recorded in the Deployment section below — keep the two identical.

```yaml
commands: { test: "...", test_one: "...", typecheck: "...", build: "..." }
phases:
  - id: p1
    name: ...               # MUST match the prose phase name
    depends_on: []          # MUST match the prose "depends on"
    owns:   ["..."]         # globs from the File Structure; no two phases overlap
    shared: ["..."]         # files touched by >1 phase — collision points
    requirement_refs: [US-1, AC-1.1]
    test_focus: "..."
    flags: []               # optional: scaffold | ui | ai
integration_checkpoints:
  - { after: [...], name: ..., verifies: "..." }
```

For a trivial single-phase feature, inline `owns`/`depends_on`/`requirement_refs` into the prose
phase and omit this block.

## Technical Decisions
Significant choices, alternatives considered, rationale, tradeoffs accepted.

## Deployment & Infrastructure
Restate the budget tier on the first line so the reader has it in context.

Record the exact runnable commands here — `test`, `test_one` (single file/glob), `typecheck`,
`build` (and `lint` if relevant) — so they're available to builders and to the Build Manifest above.
This is the source of truth; keep the manifest's `commands` block identical.

For each concern, state the choice and a one-line "why this fits the tier":
- **Hosting / runtime** — where the app runs (VM, PaaS, container platform, K8s, serverless)
- **Database hosting** — managed tier vs self-hosted vs embedded
- **Background jobs** (if any) — in-process / DB-backed / managed queue / event bus
- **Object storage** (if any) — local / S3-equivalent / CDN-fronted
- **Caching** (only if needed) — in-process / Redis / managed cache
- **Observability** — stdout logs / logs-as-a-service / full APM
- **Secrets** — env vars / platform secrets / dedicated secrets manager
- **Environments** — just-prod / prod+staging / full dev/staging/prod

End with a **rough monthly cost estimate** in the order-of-magnitude buckets ($0, $50, $500, $5k, $50k+). If the estimate doesn't match the budget tier, the design needs to be revisited.

## Code Conventions  *(Developer mode only — delete this section in PM mode)*
Naming patterns, module boundaries, error-handling style + envelope shape,
logging library + required structured fields, lint/format stance,
cross-cutting patterns (transactions, concurrency, frontend state management).
Record answers to any code-level questions that were surfaced, with brief rationale.

## Testing Strategy  *(Developer mode only — delete this section in PM mode)*
Test framework, unit vs integration split, mocking policy (what's real, what's faked),
coverage target, fixture conventions, how eval harnesses (if any) are wired.

## Unresolved from Requirements
Any open questions from the requirements docs that were resolved here, and any that still
need the user's input. In Developer mode, also list any code-level decisions marked
"Proposed — confirm with dev team" when the architect ran solo.

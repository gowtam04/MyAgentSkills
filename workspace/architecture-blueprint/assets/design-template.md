# {Feature Name} - Technical Design

## Overview
Mode: PM | Developer  - pick one; this line helps `/build-orchestrator` tune subagent prompts and todo scaffolding
Budget Tier: hobby | startup | scaling | enterprise  - from Phase 1; deployment must respect this
Brief summary of what's being built and the key technical approach.

## Requirements Reference
Path to the business requirements this design is based on: `[actual path used]`

## Tech Stack
Languages, frameworks, and key libraries. For existing projects, note any additions.
(Omit for features that don't introduce new technology.)

## Data Model
Entities, fields, relationships, constraints. Every entity should trace to a requirement. Include a simple ERD description or table. Note migrations/backfills if brownfield.

## Component Design
Each component: responsibility (one sentence), interface, dependencies, file location.
If a component needs a paragraph to explain its purpose, split it or clarify the boundary.

## API Design
Endpoints, request/response shapes, auth patterns, error envelope.
(Omit for non-API work.)
Scale detail to risk: high for security-sensitive/nonstandard seams; light for conventional CRUD.

## File Structure
Complete file tree with descriptions. This is the ownership map — each file has one purpose;
no two builders (or parallel subagents) should need to edit the same file in the same phase.

## Interface Definitions
Key contracts between components — function signatures, types, error types.
Scale detail to complexity (high detail where a builder or subagent could plausibly get it wrong;
light detail for conventional CRUD). In Developer mode, default to high detail.

## Implementation Phases
Ordered, granular, build-order phases. For each phase:
- What gets built (specific files/components)
- What it depends on (which prior phase)
- What it produces (interfaces/files available after)
- Parallel opportunities (disjoint write sets only)
- Test focus (what the phase's tests verify)
- (Developer mode) Success criteria — concrete reviewable outcomes beyond "tests pass"
- (Developer mode) Review checklist / test split — unit vs integration, mocked vs real, review gates

Call out integration seams: API↔data, UI↔API, auth cross-layer, final workflow verification.

## Technical Decisions
Significant choices, alternatives considered, rationale, tradeoffs accepted.
Use ADR-style bullets for hard-to-reverse choices.

## Deployment & Infrastructure
Restate the budget tier on the first line so the reader has it in context.

For each concern, state the choice and a one-line "why this fits the tier":
- **Hosting / runtime** - where the app runs (VM, PaaS, container platform, K8s, serverless)
- **Database hosting** - managed tier vs self-hosted vs embedded
- **Background jobs** (if any) - in-process / DB-backed / managed queue / event bus
- **Object storage** (if any) - local / S3-equivalent / CDN-fronted
- **Caching** (only if needed) - in-process / Redis / managed cache
- **Observability** - stdout logs / logs-as-a-service / full APM
- **Secrets** - env vars / platform secrets / dedicated secrets manager
- **Environments** - just-prod / prod+staging / full dev/staging/prod

End with a **rough monthly cost estimate** in the order-of-magnitude buckets ($0, $50, $500, $5k, $50k+). If the estimate doesn't match the budget tier, the design needs to be revisited.

## UI Reference *(if UI work)*
Path to design system if present (`/docs/design-system/...`), else "follow existing app patterns + requirements UI notes." Do not invoke a separate frontend-design skill.

## Code Conventions  *(Developer mode only - delete this section in PM mode)*
Naming patterns, module boundaries, error-handling style + envelope shape,
logging library + required structured fields, lint/format stance,
cross-cutting patterns (transactions, concurrency, frontend state management).
Record answers to any code-level questions that were surfaced, with brief rationale.

## Testing Strategy  *(Developer mode only - delete this section in PM mode)*
Test framework, unit vs integration split, mocking policy (what's real, what's faked),
coverage target, and fixture conventions.

## Unresolved from Requirements
Any open questions from the requirements docs that were resolved here, and any that still
need the user's input. In Developer mode, also list any code-level decisions marked
"Proposed - confirm with dev team" when the architect ran solo.

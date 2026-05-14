# {Feature Name} — Technical Design

## Overview
Mode: PM | Developer  ← pick one; this line is how `dev-team` detects the mode
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

## Implementation Phases
Ordered, granular, build-order phases. For each phase:
- What gets built (specific files/components)
- What it depends on (which prior phase)
- What it produces (interfaces/files available after)
- Parallel opportunities (what can be built simultaneously)
- Test focus (what the phase's tests verify)
- (Developer mode) Success criteria — concrete reviewable outcomes beyond "tests pass"
- (Developer mode) Review checklist / test split — unit vs integration, mocked vs real, review gates

## Technical Decisions
Significant choices, alternatives considered, rationale, tradeoffs accepted.

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

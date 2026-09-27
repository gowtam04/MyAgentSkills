# {Feature or Product Name} — Requirements

## Overview
What this is, who it serves, and why it matters — a few sentences. For a change to an existing
product: current behavior, desired behavior, and the delta.

**Success looks like:** measurable outcomes where possible.

## Users and Roles
| Role | Goals | Context | Can | Cannot |
|---|---|---|---|---|
| | | | | |

## Workflows
Group by functional area. Each area opens with a cross-link line:
> **Serves:** {roles} · **Touches:** {entities} · **Depends on:** {other areas}

### {Workflow name} ({role})
1. Step-by-step happy path — what they see, what they do, what the system does.
2. …

**When things go wrong:** failure, empty, conflict and permission-denied states that matter.

## User Stories and Acceptance Criteria
Stable IDs: append, never renumber. Criteria are Given/When/Then or a checkable assertion with
real values — a test-writer agent turns each one into a test without asking anyone.

- **US-1** — As a {role}, I want to {action} so that {benefit}.
  - **AC-1.1** — Given {context}, when {action}, then {observable result}.
  - **AC-1.2** — {concrete checkable assertion}

## Business Rules
- **BR-1** — {exact rule: validation, permission, state transition, calculation, or notification trigger}

## Data (business level)
Key entities, what belongs to what, who owns each, lifecycle and retention. No schemas.

## Non-Functional Requirements
Speed, reliability, scale, accessibility, platforms, compliance/privacy — in user terms, with
numbers where they matter.

## UI/UX Vision
Key screens and what's prominent on each, interaction patterns, responsive needs, references.
(Delete for backend-only work.)

## Constraints and Preferences
Timeline, budget, existing systems, technical preferences — inputs for the architect, not
decisions made here.

## Assumptions
Speed-path guesses, most expensive to change first. Delete the section if there are none.

| # | Assumption | Why it's the sensible default | Affects | Change cost |
|---|---|---|---|---|
| A-1 | | | US-…, BR-… | expensive — reshapes data or workflows |
| A-2 | | | | moderate — touches a few features |
| A-3 | | | | cheap — copy or config change |

## Open Questions
Real unknowns only.

## Out of Scope
A hard boundary: autonomous builders won't cross it or invent around it. Name the adjacent things
a builder might otherwise assume.

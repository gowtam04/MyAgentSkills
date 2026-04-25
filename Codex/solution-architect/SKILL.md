---
name: solution-architect
description: >
  Design a technical solution from business requirements. Use this skill when the user has
  requirements docs, a product brief, or a defined feature idea and needs a technical design
  before implementation. Trigger on requests like "design the architecture", "plan how to build
  this", "create a technical design", or "turn these requirements into an implementation plan."
  This Codex version reads requirements and the existing codebase first, asks only questions that
  materially change the architecture, uses the Codex structured question UI for those decisions
  when available, and produces decision-complete design docs plus an implementation blueprint.
---

# Solution Architect

Translate requirements into a technical design that builders can execute without making structural decisions on the fly.

## Core Role

- Own the HOW, not the WHAT.
- Respect existing repository patterns unless there is a documented reason to diverge.
- Resolve technical tradeoffs that materially affect boundaries, data flow, interfaces, rollout, or operations.
- Produce an implementation blueprint detailed enough for another engineer or Codex agent to build from directly.
- Right-size the output. A small feature may need one focused `design.md`; a product build needs split architecture docs.

## Workflow

### 1. Start With Requirements And Repo Truth

Before asking the user anything:

- Read requirements under `/docs/requirements/` or `/docs/features/{feature-name}/requirements/`, or the user-provided brief.
- Inspect repo structure, manifests, configs, scripts, test setup, and representative files.
- Identify languages, frameworks, package managers, ORMs, routing patterns, state management, auth, data models, build tools, and deployment assumptions.
- Study existing file organization, naming conventions, error handling, testing patterns, and public interfaces.
- Check existing APIs, schemas, migrations, models, services, components, and integration boundaries.
- Note out-of-scope requirements and unresolved questions.

If requirements are missing and the product problem is still fuzzy, do minimal discovery only if the architecture can still be bounded. Otherwise hand off to `requirement-gathering`.

### 2. Confirm Understanding

Briefly summarize what the requirements call for and what the repo already establishes. Then decide whether any ambiguity changes the architecture.

Ask only when the answer changes:

- System boundaries
- Data model or persistence strategy
- Auth, permissions, privacy, or compliance posture
- External providers or integration contracts
- Realtime, async, or batch processing model
- Platform support or deployment model
- Rollout, migration, or backward compatibility strategy

If a builder can safely decide later, make a reasonable assumption and document it.

### 3. Ask Architecture-Changing Questions

When user input is necessary:

- Exhaust repo and docs discovery first.
- If `request_user_input` is available, use it for material architecture decisions instead of ending with a plain-text question.
- Ask 1 focused question per round by default. Batch up to 3 only when tightly related.
- Provide 2-3 viable options, with the recommended option first when justified.
- Explain architectural implications in option descriptions.
- If the tool is unavailable, ask concise direct questions with concrete options and a recommended default.
- Keep the total architecture-question loop short, usually 1-3 rounds.

Do not ask about implementation trivia such as minor library choices, file naming, or conventional helper structure unless those choices materially affect the design.

### 4. Make The Technical Design

Cover the areas that apply.

#### Tech Stack

- For existing projects, use the established stack unless a documented requirement forces a change.
- For greenfield work, recommend a stack that fits requirements, team constraints, scale, and operational needs.
- Document additions to the stack and why they are needed.
- Do not over-specify routine packages that builders can choose safely.

#### Data Model

Define:

- Entities and attributes
- Relationships and ownership rules
- Validation, uniqueness, lifecycle, retention, and permission constraints
- Index or query-pattern needs when they affect architecture
- Migration or backfill needs for existing systems

Every entity should trace back to a requirement.

#### Component Architecture

For each component or module:

- State what it owns
- State what it exposes
- State what it depends on
- State where it lives in the file structure
- Note which existing patterns it follows

Prefer components with clear responsibilities. If a component needs a paragraph to explain its purpose, split it or clarify its boundary.

#### API And Interfaces

For APIs or cross-module contracts, define:

- Routes, methods, request shapes, response shapes, auth rules, and error shapes
- Internal service interfaces, function signatures, types, events, or messages where ambiguity would be costly
- Pagination, filtering, sorting, idempotency, and retry behavior when relevant
- External provider boundaries and failure handling

Scale interface detail to risk:

- High detail for security-sensitive, complex, nonstandard, or integration-heavy areas.
- Light detail for conventional CRUD, simple transforms, or patterns a competent builder will implement consistently.

Test: would a builder plausibly get this wrong without guidance? If yes, specify it.

#### Technical Decisions

Document significant choices with:

- Decision
- Alternatives considered
- Rationale
- Tradeoffs accepted
- Reversal or migration considerations when relevant

### 5. Build The Implementation Blueprint

The blueprint is the handoff contract for implementation.

#### File Structure

List every file or module that needs to exist, grouped by component. Include:

- Purpose
- Owner component
- New vs modified
- Important exported interfaces or responsibilities

This file list is also the ownership map for a parallel build. Avoid designs that require multiple implementers to edit the same file at the same time.

#### Implementation Phases

Break work into granular, build-order phases. Prefer more small, verifiable phases over a few broad ones.

Each phase must state:

- What gets built: specific files, modules, migrations, tests, or docs
- Dependencies: prior phases or existing systems required first
- Outputs: interfaces, files, data structures, or behavior available after the phase
- Parallel opportunities: independent files or components that can be built at the same time
- Test focus: what unit, integration, type, build, or E2E checks should verify

Typical ordering:

- Greenfield app: scaffolding -> data model -> auth/permissions -> core services -> API/interface layer -> UI foundation -> feature screens -> integration/polish.
- Existing feature: data/model changes -> business logic -> API/interface changes -> UI changes -> integration/edge cases.
- Backend service: scaffolding -> data model -> auth -> services -> interface layer -> integration tests.
- CLI/tooling: scaffolding -> core types/library -> commands -> integration tests.

Adapt this to the actual dependency graph. Merge phases that are too small to test meaningfully; split phases that cross too many layers to review confidently.

## Output

Write design docs to:

- Existing-project feature work: `/docs/features/{feature-name}/architecture/`
- New applications or project-wide work: `/docs/architecture/`

Create directories if they do not exist.

### Smaller Feature Template

Create one `design.md`:

```markdown
# {Feature Name} - Technical Design

## Overview
Summary of the technical approach and how it satisfies the requirements.

## Requirements Reference
Path to the requirements used.

## Tech Stack
Established stack and any additions.

## Data Model
Entities, fields, relationships, constraints, migrations.

## Component Design
Components, responsibilities, dependencies, and locations.

## API And Interface Design
Endpoints, contracts, request/response shapes, internal interfaces, events, or messages.

## File Structure
Complete ownership map of files to create or modify.

## Implementation Phases
Ordered phases with dependencies, outputs, parallel opportunities, and test focus.

## Technical Decisions
Decisions, alternatives, rationale, and tradeoffs.

## Unresolved Questions
Only issues that still materially affect architecture or implementation.
```

Omit sections that truly do not apply.

### Larger Project Structure

Split into focused docs such as:

- `overview.md` - high-level architecture, stack, requirements reference
- `data-model.md` - entities, relationships, migrations, constraints
- `component-design.md` - modules, responsibilities, dependencies
- `api-design.md` - API and integration contracts
- `implementation-plan.md` - file ownership and phased build plan
- `decisions.md` - architecture decision records

## Quality Standard

The design should let a competent builder implement without messaging the architect for structural decisions.

Check that:

- Every required file is listed with purpose and component ownership.
- Every costly interface ambiguity is resolved.
- Every significant technical decision includes rationale.
- Phase ordering and dependencies are explicit.
- Parallel opportunities are called out.
- Testing expectations are clear per phase.
- Existing repo patterns are followed or deviations are justified.

Avoid vague statements like "the service layer handles business logic." Say what the service owns, what it exposes, what rules it enforces, and which callers depend on it.

## Handoff Rules

- If the work includes meaningful UI and no visual language exists, hand off next to `design-system` before UI implementation starts.
- If a design system already exists, reference it in the architecture and implementation phases.
- If the work is backend-only or the visual language is already established, hand off directly to implementation.
- If the user explicitly wants delegated execution, `dev-team` consumes these docs rather than re-deriving the plan.

## Special Scenarios

- Existing codebase: design how the new work fits. Do not redesign stable patterns unless required.
- Strong user technical preferences: incorporate them when viable; if risky, explain the tradeoff and document the final choice.
- Greenfield with no requirements docs: ask only the minimum architecture-shaping questions; suggest `requirement-gathering` if product scope is still broad or unclear.
- Ambiguous requirement: ask only if the interpretation changes architecture; otherwise document an assumption.
- Very small feature: write a concise `design.md` with component design, file list, interfaces, and phases; omit irrelevant sections.

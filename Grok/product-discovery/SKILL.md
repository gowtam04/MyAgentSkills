---
name: product-discovery
description: >
  Conduct a structured product discovery interview using ask_user_question and write business/product requirements documentation before any design or implementation.
  Use when the user says "interview me", "gather requirements", "scope this app", "help me spec this out", "write a PRD", "requirements doc", "document this feature", or otherwise wants to define what should be built and why before deciding how to build it.
  This skill discovers personas, workflows, business rules, acceptance criteria, UX expectations, constraints, and open questions; it does not make technical architecture decisions or implement application code.
when-to-use: Use when the user wants a requirements interview or PRD before architecture (/architecture-blueprint) or implementation (/build-orchestrator). Slash command: /product-discovery
argument-hint: "<brief idea, feature name, or 'interview me for a ...'>"
---

# Product Discovery

Act as a senior product analyst. Interview the user to understand what the product or feature must do, why it matters, who it serves, and what rules govern it. Produce requirements documentation that an architect can use without guessing.

## Core Rules

- Ask before assuming. Every requirement should trace to the user, existing docs, or the current product surface. Put unresolved gaps in Open Questions.
- Stay at the product level. Capture technical preferences as constraints, but do not pick frameworks, databases, APIs, schemas, or infrastructure.
- Right-size the interview. A small change may need only a few focused questions; a new app needs personas, workflows, data, rules, UX, and operational expectations.
- **Every user input or decision must go through `ask_user_question`.** No bare prose questions. The user interacts exclusively via structured option cards (with an automatic "Other" escape hatch). If your turn contains an explicit or implied question that expects an answer, it must be preceded by (or be) an `ask_user_question` tool call in the same response.
- End each interview turn either with a structured `ask_user_question` request or by writing/updating the requirements docs. Do not leave the user with an implied question hidden in prose.
- Only `/build-orchestrator` may implement application code. This skill's deliverable is requirements documentation only.

## Plan Mode Output Contract

When the overall task is run in Plan Mode (or when you decide the requirements work itself has enough ambiguity to warrant it), call `enter_plan_mode` first. The final `<proposed_plan>` (via `exit_plan_mode`) must be a **documentation plan only**:

- The proposed plan must describe only how you will create or update requirements docs.
- The plan must explicitly state that no application source files, scaffolding, dependencies, tests, build configs, or implementation artifacts will be created.
- The plan can include the requirement areas to document, open questions to capture, and the output path(s) for the docs.
- The plan must **not** include app build steps such as creating pages, components, API routes, services, styles, tests, or running a dev server.
- When the user accepts the plan, write the requirements documentation only.
- After the docs are written and approved, hand off to `/architecture-blueprint`; do not start architecture or implementation from this skill.

## Before Asking

Scan for context first:

1. Check for existing requirements in `/docs/features/{feature-name}/requirements/` and `/docs/requirements/`.
2. If there is an existing project, skim enough of the app to understand its product surface (README, routes/pages, screenshots, or docs that reveal what users can currently do). Do not dive into internals.
3. If the user supplied a brief, treat it as input, not final output. Identify gaps and ask only the questions needed to remove ambiguity via `ask_user_question`.

## Interview Flow (All Questions via ask_user_question)

### 1. Big Picture

Clarify via one or more `ask_user_question` calls:

- What is being built: new product, new feature, or change to existing behavior.
- Who it is for: user roles, goals, context, technical comfort, usage frequency.
- Why it should exist: problem, cost of the status quo, business/user value.
- What success looks like: measurable outcomes, acceptance signals, launch bar.

Use 1-3 focused questions per call. Provide 2-4 realistic options + descriptions that help the user think, plus the automatic Other path.

### 2. Users And Workflows

For each user role, capture:

- Primary goals and pain points.
- Happy-path workflows step by step.
- First-run or onboarding experience.
- Edge cases, failure states, conflicts, empty states, and permission boundaries.

Batch related role/workflow questions. Use `multiSelect: true` where the user may pick several roles or patterns.

### 3. Functional Requirements

Document precise capabilities via targeted questions:

- Features and actions users can perform.
- Business rules: validation, permissions, state transitions, calculations, notifications.
- Data concepts from a business perspective: entities, relationships, ownership, lifecycle.
- Content, reports, imports/exports, integrations, and communication triggers.

Prefer specific wording in follow-ups.

### 4. Non-Functional Requirements

Capture expectations:

- Performance, reliability, security/access, accessibility, platform, scale, budget, timeline, existing systems, operational constraints.

### 5. UI/UX Vision (if applicable)

If there is a user interface, ask about:

- Experience tone, key screens, interaction patterns, responsive needs.

Skip for backend-only/API work unless the user raises it.

### 6. Confirm And Close

After major sections, summarize what you heard in plain text, then immediately follow with an `ask_user_question` confirmation card (Yes / Mostly right / Needs rework). Stop asking when requirements are specific enough for architecture. If the user wants speed, compress, make conservative assumptions (explicitly marked), and confirm.

## Writing The Documentation

Write docs to:

- Feature in existing project: `/docs/features/{feature-name}/requirements/`
- New application: `/docs/requirements/`

Create directories as needed using `run_terminal_command` if necessary (e.g. `mkdir -p ...`).

### Small Feature

Create `requirements.md`:

```markdown
# {Feature Name} - Business Requirements

## Overview
## Users and Personas
## User Stories
## Functional Requirements
## Business Rules
## Non-Functional Requirements
## UI/UX Vision
## Constraints and Preferences
## Open Questions
## Out of Scope
```

Include acceptance criteria under user stories. Omit UI/UX for non-UI work.

### Large Application

Use multiple files grouped by functional domain (see original product-discovery for example groupings). Keep organized by domain so `/architecture-blueprint` can produce granular implementation phases.

## Quality Bar

The final docs should be:

- Specific enough that an architect can design from them without inventing intent.
- Organized by feature/domain, not interview chronology.
- Free of technical decisions, except user-stated preferences recorded as constraints.
- Honest about unknowns, assumptions, out-of-scope items, and unresolved conflicts.

After writing, present the docs briefly and ask for review via `ask_user_question`. If approved, tell the user the next step is technical architecture with `/architecture-blueprint`.

## Handoff

Once approved: "These requirements are ready. The next step is technical architecture — run `/architecture-blueprint` (point it at the docs you just created or let it auto-discover them)."

---
name: product-discovery
description: >
  Conduct a structured product discovery interview and write business/product requirements
  documentation before design or implementation. Use when the user says "interview me",
  "gather requirements", "scope this app", "help me spec this out", "write a PRD",
  "requirements doc", "plan this feature", or otherwise wants to define what should be
  built and why before deciding how to build it. This skill discovers personas, workflows,
  business rules, acceptance criteria, UX expectations, constraints, and open questions;
  it does not make technical architecture decisions.
---

# Product Discovery

Act as a senior product analyst. Interview the user to understand what the product or
feature must do, why it matters, who it serves, and what rules govern it. Produce
requirements documentation that an architect can use without guessing.

## Core Rules

- Ask before assuming. Every requirement should trace to the user, existing docs, or the
  current product surface. Put unresolved gaps in Open Questions.
- Stay at the product level. Capture technical preferences as constraints, but do not pick
  frameworks, databases, APIs, schemas, or infrastructure.
- Right-size the interview. A small change may need only a few focused questions; a new app
  needs personas, workflows, data, rules, UX, and operational expectations.
- Use `request_user_input` for structured questions when it is available. This interview is
  best run in Plan mode so choices can be presented as cards with predefined options and an
  Other path. If the tool is unavailable, ask concise grouped questions in normal prose and
  continue from the user's answers.
- End each interview turn either with a structured user-input request or by writing/updating
  the requirements docs. Do not leave the user with an implied question hidden in prose.

## Before Asking

Scan for context first:

1. Check for existing requirements in `/docs/features/{feature-name}/requirements/` and
   `/docs/requirements/`.
2. If there is an existing project, skim enough of the app to understand its product surface,
   not its internals. Look for README, routes/pages, screenshots, or docs that reveal what
   users can currently do.
3. If the user supplied a brief, treat it as input, not final output. Identify gaps and ask
   only the questions needed to remove ambiguity.

## Interview Flow

### 1. Big Picture

Clarify:

- What is being built: new product, new feature, or change to existing behavior.
- Who it is for: user roles, goals, context, technical comfort, usage frequency.
- Why it should exist: problem, cost of the status quo, business/user value.
- What success looks like: measurable outcomes, acceptance signals, launch bar.

### 2. Users And Workflows

For each user role, capture:

- Primary goals and pain points.
- Happy-path workflows step by step.
- First-run or onboarding experience.
- Edge cases, failure states, conflicts, empty states, and permission boundaries.

Use options to help the user think. For example, ask whether the project is a new product,
new feature, or behavior change; ask which roles apply using a multi-select-style prompt
when available.

### 3. Functional Requirements

Document precise capabilities:

- Features and actions users can perform.
- Business rules: validation, permissions, state transitions, calculations, notifications.
- Data concepts from a business perspective: entities, relationships, ownership, lifecycle.
- Content, reports, imports/exports, integrations, and communication triggers.

Prefer specific wording: "Users can update display name up to 50 characters and must
re-verify email after changing it" instead of "Users manage profile."

### 4. Non-Functional Requirements

Capture expectations from the user's perspective:

- Performance: instant, seconds, batch/overnight, concurrent users.
- Reliability: nice-to-have vs business-critical, downtime tolerance.
- Security and access: roles, sensitive data, compliance constraints.
- Accessibility and platform: desktop, mobile, offline, browser/native.
- Scale, budget, timeline, existing systems, and operational constraints.

### 5. UI/UX Vision

If there is a user interface, ask about:

- Experience tone: utilitarian, data-dense, polished, playful, reference products.
- Key screens and what users see first.
- Interaction patterns: forms, search/filter, drag/drop, collaboration, dashboards.
- Responsive needs and device expectations.

Skip UI questions for backend-only/API work unless the user raises them.

### 6. Confirm And Close

After major sections, summarize what you heard and ask for confirmation or corrections.
Stop asking when requirements are specific enough for architecture. If the user wants speed,
compress questions, make conservative assumptions, and mark those assumptions explicitly.

## Writing The Documentation

Write docs to:

- Feature in existing project: `/docs/features/{feature-name}/requirements/`
- New application: `/docs/requirements/`

Create directories as needed.

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

Use multiple files grouped by functional domain, not priority tiers. Example:

```text
/docs/requirements/
- overview.md
- data-and-entities.md
- auth-and-permissions.md
- core-workflows.md
- api-and-integrations.md
- ui-and-experience.md
- operational.md
```

Choose names that fit the product. Group requirements that share entities, business rules,
or user context. Capture priority notes in `overview.md`, but keep the docs organized by
domain so architecture can produce granular implementation phases.

## Quality Bar

The final docs should be:

- Specific enough that an architect can design from them without inventing intent.
- Organized by feature/domain, not interview chronology.
- Free of technical decisions, except user-stated preferences recorded as constraints.
- Honest about unknowns, assumptions, out-of-scope items, and unresolved conflicts.

After writing, present the docs briefly and ask for review. If approved, tell the user the
next step is technical architecture with `$architecture-blueprint`.

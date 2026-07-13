---
name: product-discovery
description: >
  Conduct a structured product discovery interview using ask_user_question and write business/product
  requirements documentation before any design or implementation.
  Use when the user says "interview me", "gather requirements", "scope this app", "help me spec this out",
  "write a PRD", "requirements doc", "document this feature", "MVP", "user stories", "what should we build",
  "before we code", "scope the product", or otherwise wants to define what should be built and why before
  deciding how to build it.
  This skill discovers personas, workflows, business rules, acceptance criteria, UX expectations, constraints,
  and open questions; it does not make technical architecture decisions or implement application code.
  Prefer this skill over jumping straight into coding when product intent is still fuzzy.
when-to-use: Use when the user wants a requirements interview or PRD before architecture (/architecture-blueprint) or implementation (/build-orchestrator). Slash command: /product-discovery
argument-hint: "<brief idea, feature name, or 'interview me for a ...'>"
---

# Product Discovery

Act as a senior product analyst. Interview the user to understand what the product or feature must do, why it matters, who it serves, and what rules govern it. Produce requirements documentation that an architect can use without guessing.

## Core Rules

- Ask before assuming. Every requirement should trace to the user, existing docs, or the current product surface. Put unresolved gaps in Open Questions.
- Stay at the product level. Capture technical preferences as constraints, but do not pick frameworks, databases, APIs, schemas, or infrastructure.
- Right-size the interview. A small change may need only a few focused questions; a new app needs personas, workflows, data, rules, UX, and operational expectations.
- **Decisions that need a user answer go through `ask_user_question`.** Use structured option cards (2–4 realistic options with helpful descriptions; the UI always offers "Other"). Plain-text recaps and short summaries between cards are fine and encouraged — do not bury a question that expects an answer only in prose.
- End each interview turn either with an `ask_user_question` call or by writing/updating the requirements docs.
- Only `/build-orchestrator` may implement application code. This skill's deliverable is requirements documentation only.

## Non-Negotiable Flow

**Interview first, then write final docs.**

- Do not create `requirements.md` (or multi-file requirements) as a scratchpad mid-interview.
- Use conversation recaps for interim notes. Write final docs only after key product choices, workflows, rules, and constraints are clear enough for architecture.
- If the user provides a complete brief up front, read it, identify material gaps, ask only about those gaps, then write docs.

## Plan Mode Output Contract

When the overall task is run in Plan Mode (or when requirements work itself has enough ambiguity to warrant it), call `enter_plan_mode` first. The final plan via `exit_plan_mode` must be a **documentation plan only**:

- Describe only how you will create or update requirements docs.
- Explicitly state that no application source files, scaffolding, dependencies, tests, build configs, or implementation artifacts will be created.
- Include requirement areas to document, open questions to capture, and output path(s).
- Do **not** include app build steps (pages, components, API routes, services, styles, tests, dev servers).
- When the user accepts the plan, write the requirements documentation only.
- After docs are approved, hand off to `/architecture-blueprint`; do not start architecture or implementation from this skill.

## Resources

- Read `references/large-app-structure.md` when the work is a new product or multi-domain app (multi-file requirements layout).
- Read `references/pipeline-contract.md` for what architecture and build expect from these docs.
- Read `references/question-examples.md` if you need a model for good `ask_user_question` batches.

## Before Asking

Scan for context first:

1. Check for existing requirements in `/docs/features/{feature-name}/requirements/` and `/docs/requirements/`.
2. If there is an existing project, skim enough of the app to understand its product surface (README, routes/pages, screenshots, or docs). Do not dive into internals.
3. If the user supplied a brief, treat it as input, not final output. Identify gaps and ask only what removes ambiguity.

## Skip Path

If the user already has specific, architecture-ready requirements (clear personas, workflows, rules, acceptance criteria, constraints), confirm via `ask_user_question` and either polish the existing docs or hand off immediately to `/architecture-blueprint`. Do not re-interview for sport.

## Interview Flow

### 1. Big Picture

Clarify via one or more `ask_user_question` calls:

- What is being built: new product, new feature, or change to existing behavior.
- Who it is for: user roles, goals, context, technical comfort, usage frequency.
- Why it should exist: problem, cost of the status quo, business/user value.
- What success looks like: measurable outcomes, acceptance signals, launch bar.

Use 1–3 focused questions per call. Provide 2–4 realistic options with descriptions that help the user think.

### 2. Users And Workflows

For each user role, capture:

- Primary goals and pain points.
- Happy-path workflows step by step.
- First-run or onboarding experience.
- Edge cases, failure states, conflicts, empty states, and permission boundaries.

Batch related role/workflow questions. Use `multi_select: true` where the user may pick several roles or patterns.

### 3. Functional Requirements

Document precise capabilities:

- Features and actions users can perform.
- Business rules: validation, permissions, state transitions, calculations, notifications.
- Data concepts from a business perspective: entities, relationships, ownership, lifecycle.
- Content, reports, imports/exports, integrations, and communication triggers.

Prefer specific wording in follow-ups.

### 4. Non-Functional Requirements

Capture expectations in user terms:

- Performance, reliability, security/access, accessibility, platform, scale, budget, timeline, existing systems, operational constraints, compliance/privacy.

### 5. UI/UX Vision (if applicable)

If there is a user interface, ask about:

- Experience tone, key screens, interaction patterns, responsive needs, reference products if any.

Skip for backend-only/API work unless the user raises it.

### 6. Constraints And Scope Boundaries

Capture:

- Timeline, budget, launch, or migration constraints.
- Technical preferences as constraints only.
- Existing systems that must be kept, integrated, or replaced.
- Explicit out-of-scope items.
- Priority guidance without vague MVP tier theater.

### 7. Confirm And Close

After major sections, summarize what you heard in plain text, then follow with an `ask_user_question` confirmation card (Yes / Mostly right / Needs rework). Stop asking when requirements are specific enough for architecture. If the user wants speed, compress, make conservative assumptions (explicitly marked), and confirm.

## Keep The Boundary Clean

If the user starts choosing frameworks, databases, APIs, or detailed implementation patterns:

- Note them as preferences or constraints.
- Do not expand them into architecture decisions.
- Redirect back to product-level requirements.
- Technical decision space belongs to `/architecture-blueprint`.

## Writing The Documentation

Write docs only after discovery is complete enough.

Paths:

- Feature in existing project: `/docs/features/{feature-name}/requirements/`
- New application: `/docs/requirements/`

Create directories as needed.

### Small Feature

Create `requirements.md`:

```markdown
# {Feature Name} - Business Requirements

## Overview
What this feature does, who it serves, and why it matters.

## Users and Personas
User types, goals, and relevant context.

## User Stories
- As a [user type], I want to [action] so that [benefit].
  Acceptance criteria:
  - [Specific observable outcome]

## Functional Requirements
### [Area]
- [Specific behavior, rule, or capability]

## Business Rules
Validation, permissions, status transitions, calculations, notifications.

## Non-Functional Requirements
Performance, reliability, accessibility, platform, scale, compliance, privacy.

## UI/UX Vision
Screens, interaction patterns, responsive expectations, references. Omit for non-UI work.

## Constraints and Preferences
Timeline, budget, technical preferences, existing systems.

## Open Questions
Only unresolved items that genuinely remain.

## Out of Scope
Explicit exclusions.
```

### Large Application

Split by functional domain, not interview order. See `references/large-app-structure.md` for the standard multi-file layout. Group requirements that share users, entities, rules, or workflows so `/architecture-blueprint` can produce granular phases.

## Writing Standard

Finished requirements should be:

- Specific enough for architecture without inventing intent.
- Organized by feature/domain, not interview chronology.
- Free of technical decisions except user-stated preferences recorded as constraints.
- Honest about unknowns, assumptions, out-of-scope items, and unresolved conflicts.

**Bad:** "Users can manage their profile."

**Good:** "Users can update display name, email address, and profile photo. Email changes require re-verification before the new address is used for notifications."

## Quality Bar

The final docs should be:

- Specific enough that an architect can design from them without inventing intent.
- Organized by feature/domain, not interview chronology.
- Free of technical decisions, except user-stated preferences recorded as constraints.
- Honest about unknowns, assumptions, out-of-scope items, and unresolved conflicts.

After writing, present the docs briefly and ask for review via `ask_user_question`. If approved, tell the user the next step is technical architecture with `/architecture-blueprint`.

## Special Scenarios

- **Existing product change:** focus on current behavior, desired behavior, and the delta.
- **User is unsure:** start from the problem, users, and success criteria; offer concrete product directions.
- **User wants speed:** ask only the highest-impact questions, make reasonable assumptions, and label them.
- **User provides a brief:** use it as input, identify gaps, ask only about those gaps, then write docs.
- **Technical-heavy user:** capture preferences as constraints and keep requirements at the WHAT and WHY layer.

## Handoff

Once approved: "These requirements are ready. The next step is technical architecture — run `/architecture-blueprint` (skill: `architecture-blueprint`). Point it at the docs you just created or let it auto-discover them."

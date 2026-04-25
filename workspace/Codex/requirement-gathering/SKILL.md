---
name: requirement-gathering
description: >
  Conduct a structured requirements conversation and produce product or business requirements
  documentation. Use this skill when the user wants to define what should be built before
  implementation begins, including prompts like "gather requirements", "spec this out",
  "interview me", "write a PRD", or "help me plan this feature." This Codex version explores
  existing docs and code first, conducts the interview before writing final docs, asks only
  unresolved product questions, routes material questions through the Codex structured question UI
  when available, and otherwise falls back to short direct questions with concrete options. It
  focuses on WHAT and WHY, not technical architecture.
---

# Requirement Gathering

Turn a rough idea into business and product requirements that a solution architect can design from.

## Core Role

- Stay at the product and business layer: what the system should do, who it serves, why it matters, and how success is recognized.
- Treat technical preferences as constraints to pass forward, not architecture decisions to make now.
- Scale depth to the scope. A small feature may need a short interview; a new product needs phased discovery.
- Ask before documenting unresolved requirements. Do not silently invent product facts.

## Non-Negotiable Flow

Conduct the interview first, then write the requirements docs.

- Do not create `requirements.md`, `overview.md`, or final requirement files as a scratchpad before the interview is complete enough to support them.
- Do not generate a thin initial requirements file and then repeatedly modify it during discovery.
- Use the conversation for interim notes and recaps. Only write final docs after the key product choices, workflows, rules, and constraints are clear.
- If the user provides a complete brief upfront, read it, identify material gaps, ask about those gaps, then write docs.

## Workflow

### 1. Ground In Existing Context

Before asking the user anything, inspect the current workspace for:

- Existing requirements under `/docs/requirements/` or `/docs/features/{feature-name}/requirements/`
- Product context in `README`, planning docs, issue notes, app copy, or existing specs
- Current user-facing behavior when the user is changing an existing product
- Existing design or business constraints that should shape the interview

Ask only for information that cannot be discovered locally.

### 2. Interview By Product Area

Use these phases as a guide, adapting depth to the work. Skip areas that clearly do not apply.

#### Phase 1: Big Picture

Establish:

- What is being built: new product, new feature, or change to existing behavior
- Who it is for: user types, goals, context, sophistication, usage frequency
- Why it matters: problem solved, cost of current state, business value
- What success looks like: qualitative outcomes and measurable targets

#### Phase 2: Users And Workflows

Clarify:

- User roles and personas
- Core happy-path workflows for each main user type
- New-user or onboarding flow when relevant
- Edge cases, exceptions, and failure states
- Approval, collaboration, or handoff steps between users

#### Phase 3: Functional Requirements

Get specific about:

- Capabilities and actions users can perform
- Business rules, validation rules, permissions, and status transitions
- Data and entities from a business perspective, not database design
- Content, emails, notifications, reports, and generated outputs
- Integrations as business data flows, not technical implementation choices

#### Phase 4: Business-Level Nonfunctional Needs

Capture:

- Performance expectations in user terms
- Reliability and downtime tolerance
- Accessibility expectations
- Platform targets: desktop web, mobile web, native app, API-only, offline
- Scale expectations that affect product scope
- Compliance, security, privacy, or audit requirements

#### Phase 5: UI/UX Vision

For user-facing work, clarify:

- Desired feel: utilitarian, data-dense, polished, playful, consumer-grade, internal-tool focused
- Key screens and what each screen must help users do
- Interaction patterns such as forms, filters, search, drag-and-drop, collaboration, or realtime feedback
- Responsive expectations across desktop and mobile
- Reference products, if the user already has examples

Do not ask UI questions for backend-only or API-only work unless the user raises them.

#### Phase 6: Constraints And Scope Boundaries

Capture:

- Timeline, budget, launch, or migration constraints
- Technical preferences as user constraints only
- Existing systems that must be kept, integrated, or replaced
- Explicit out-of-scope items
- Priority guidance without reorganizing requirements into vague MVP tiers

### 3. Ask Material Questions Well

When you need user input:

- If `request_user_input` is available, use it for material decisions, clarifications, and confirmations instead of ending with a plain-text question.
- Ask 1 focused question per round by default. Batch up to 3 only when tightly related.
- In each structured question, provide 2-3 mutually exclusive options and put the recommended option first when a recommendation is justified.
- Use option descriptions to explain the tradeoff in product terms.
- If the user gives a vague answer, follow up once with more specific options.
- If `request_user_input` is unavailable, ask concise direct questions with concrete options and a recommended default.
- Summarize assumptions explicitly instead of asking about low-impact details.

Self-check before ending a turn:

- If the next step depends on a user answer and `request_user_input` is available, use the structured question tool.
- Do not write final docs until the interview has enough information to make the requirements specific.
- When enough is known, stop interviewing and write the docs.

### 4. Keep The Boundary Clean

If the user starts choosing frameworks, databases, APIs, or detailed implementation patterns:

- Note them as preferences or constraints.
- Do not expand them into architecture decisions.
- Redirect back to product-level requirements for the current phase.
- Hand off technical decision space to `solution-architect`.

## Output

Write the requirements docs only after discovery is complete enough.

Use standard paths:

- Existing-project feature work: `/docs/features/{feature-name}/requirements/`
- New applications or project-wide planning: `/docs/requirements/`

Create directories if they do not exist.

### Smaller Feature Template

Create a single `requirements.md`:

```markdown
# {Feature Name} - Business Requirements

## Overview
What this feature does, who it serves, and why it matters.

## Users And Personas
User types, goals, and relevant context.

## User Stories
- As a [user type], I want to [action] so that [benefit].
  Acceptance criteria:
  - [Specific observable outcome]

## Functional Requirements
### [Area]
- [Specific behavior, rule, or capability]

## Business Rules
Validation rules, permission rules, status transitions, calculations, and other logic.

## Nonfunctional Requirements
Performance, reliability, accessibility, platform targets, scale, compliance, and privacy.

## UI/UX Vision
Screens, interaction patterns, responsive expectations, and references. Omit for non-UI work.

## Constraints And Preferences
Timeline, budget, technical preferences, existing systems, and other constraints for architecture.

## Out Of Scope
Explicit exclusions.

## Open Questions
Only unresolved items that genuinely remain.
```

### Larger Application Structure

For larger work, split by functional area, not by interview order or MVP/enhancement/polish tiers. Common files:

- `overview.md` - vision, goals, personas, success criteria, priorities
- `core-workflows.md` - primary workflows, edge cases, business logic
- `data-and-entities.md` - business entities, relationships, lifecycle rules
- `auth-and-permissions.md` - roles, access rules, approval flows
- `api-and-integrations.md` - business-level integration needs and data flows
- `ui-and-experience.md` - screens, interaction patterns, responsive behavior
- `operational.md` - nonfunctional needs, compliance, constraints

Group requirements that share the same users, entities, business rules, or workflow context. Note dependencies between areas when one area must be designed or built before another.

## Writing Standard

Finished requirements should be:

- Specific enough for architecture work without guessing
- Organized by functional area, not interview order
- Free of implementation details beyond high-level constraints
- Honest about assumptions and unknowns
- Clear about out-of-scope boundaries

Bad: "Users can manage their profile."

Good: "Users can update display name, email address, and profile photo. Email changes require re-verification before the new address is used for notifications."

## After Writing

After docs are written:

- Summarize the file paths created.
- Briefly call out major assumptions and open questions.
- If `request_user_input` is available, ask whether the requirements are ready for architecture, need adjustments, or need open questions resolved.
- If approved or no response is needed, hand off to `solution-architect` as the next step.

## Special Scenarios

- Existing product change: focus on current behavior, desired behavior, and the delta.
- User is unsure: start from the problem, users, and success criteria; offer concrete product directions.
- User wants speed: ask only the highest-impact questions, make reasonable assumptions, and label them.
- User provides a brief: use it as input, identify gaps, ask only about those gaps, then write docs.
- Technical-heavy user: capture preferences as constraints and keep the requirements at the WHAT and WHY layer.

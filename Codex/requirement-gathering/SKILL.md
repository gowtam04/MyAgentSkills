---
name: requirement-gathering
description: >
  Conduct a structured requirements conversation and produce product or business requirements
  documentation. Use this skill when the user wants to define what should be built before
  implementation begins, including prompts like "gather requirements", "spec this out",
  "interview me", "write a PRD", or "help me plan this feature." This Codex version explores
  existing docs and code first, asks only unresolved product questions, prefers structured user
  prompts when available, and otherwise falls back to short direct questions with concrete
  options. It focuses on WHAT and WHY, not technical architecture.
---

# Requirement Gathering

Turn a rough idea into business and product requirements that a solution architect can design from.

## Core Role

- Stay at the product and business layer.
- Document what the system should do, who it serves, why it matters, and what success looks like.
- Treat technical preferences as constraints to pass forward, not architecture decisions to make now.

## Workflow

### 1. Ground In Existing Context

Before asking the user anything, inspect the current workspace for:

- Existing requirement docs under `/docs/requirements/` or `/docs/features/{feature-name}/requirements/`
- Product context in `README`, planning docs, issue notes, or app copy
- Existing UI or feature behavior when the user is changing an existing product

Ask only for information that cannot be discovered locally.

### 2. Ask Only Material Product Questions

When you need user input:

- Prefer `request_user_input` when that tool is available in the current environment.
- If it is unavailable, ask concise direct questions in plain text.
- Keep each round focused on 1-2 unresolved questions.
- Offer 2-3 concrete options and recommend a default when that helps the user respond quickly.
- Summarize assumptions explicitly instead of dragging the user through low-impact questions.

Good question areas:

- The user and audience
- Core workflows and success criteria
- Business rules, permissions, and content needs
- Platform expectations, constraints, and out-of-scope boundaries

Do not ask architecture questions here unless you are clarifying whether something belongs in scope.

### 3. Keep The Boundary Clean

If the user starts choosing frameworks, databases, or detailed technical patterns:

- Note them as preferences or constraints.
- Do not expand them into design decisions.
- Hand off that decision space to `solution-architect`.

## Output

Write the requirements docs to the standard paths:

- Existing-project feature work: `/docs/features/{feature-name}/requirements/`
- New applications or project-wide planning: `/docs/requirements/`

For a smaller feature, a single `requirements.md` is enough.

For a larger application, split by functional area. Common files include:

- `overview.md`
- `core-workflows.md`
- `data-and-entities.md`
- `auth-and-permissions.md`
- `ui-and-experience.md`
- `operational.md`

## Writing Standard

The finished requirements should be:

- Specific enough for architecture work
- Organized by functional area, not by interview order
- Honest about unknowns and assumptions
- Free of implementation details beyond high-level constraints

When the requirements are complete, explicitly hand off to `solution-architect` as the next step.

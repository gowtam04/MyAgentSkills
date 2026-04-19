---
name: design-system
description: >
  Create a concrete design system reference document for a product or application. Use this
  skill when the user wants a UI visual language defined before implementation, including prompts
  like "create a design system", "define the style guide", "set up design tokens", or "decide
  how this product should look." This Codex version reads the requirements and architecture first,
  asks only for missing aesthetic or brand direction, and writes a single design-system.md that
  downstream UI builders can follow.
---

# Design System

Define the visual language that frontend builders should implement.

## Core Role

- Sit between `solution-architect` and UI implementation.
- Convert product context into concrete colors, typography, spacing, component patterns, and motion rules.
- Make the design system implementable, not aspirational.

## Workflow

### 1. Read Existing Context First

Before asking for any preference:

- Read requirements docs for audience, workflows, and UI expectations
- Read architecture docs for component inventory, stack, and frontend structure
- Inspect existing theme files, CSS, component libraries, brand assets, or screenshots when available

Do not re-ask questions the repo or docs already answer.

### 2. Ask Only For Missing Visual Direction

When you need input:

- Prefer `request_user_input` when available.
- Otherwise ask concise direct questions with 2-3 concrete options and a recommended default.
- Keep the number of question rounds low.

Useful question areas:

- Aesthetic direction
- Brand color constraints
- Reference products
- Light, dark, or dual-theme expectations

### 3. Stay Concrete

Every recommendation should be directly implementable:

- Named colors with hex values
- Font families and fallback stacks
- Type scale with size, line height, and weight
- Spacing scale and layout rules
- Component patterns with default, hover, active, disabled, and focus behavior

## Output

Write a single design system doc to:

- `/docs/design-system/design-system.md`

It should cover:

- Design philosophy
- Color palette
- Typography
- Spacing and layout
- Component patterns
- Motion and interaction
- Accessibility expectations
- Implementation notes for token storage and usage

## Handoff Rules

- Treat this document as the source of truth for future UI work.
- When UI implementation begins, tell builders to honor this doc and use the existing `frontend-design` skill for the actual component and page execution.
- If the project already has a strong design system, update or extend it instead of inventing a conflicting one.

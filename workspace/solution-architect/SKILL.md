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
- Produce an implementation blueprint with enough specificity that another engineer or agent can build from it directly.

## Workflow

### 1. Start With Requirements And Repo Truth

Before asking the user anything:

- Read the requirements docs under `/docs/requirements/` or `/docs/features/{feature-name}/requirements/`
- Inspect the existing repo structure, manifests, configs, test setup, and representative files
- Identify the current stack, conventions, and integration points

If requirements are missing and the problem is still fuzzy, do minimal discovery or hand off first to `requirement-gathering`.

### 2. Ask Only Architecture-Changing Questions

When user input is necessary:

- Exhaust repo discovery first. Do not ask the user about facts the codebase, docs, configs, or existing interfaces can answer.
- If `request_user_input` is available, use it for architecture decisions that materially change boundaries, interfaces, data flow, rollout, or operational posture.
- Ask 1 focused question per round by default. Batch up to 3 only when the questions are tightly related.
- In each `request_user_input` question, provide 2-3 mutually exclusive options and put the recommended option first.
- If the tool is unavailable, ask concise direct questions with concrete options and a recommended default.
- Limit questions to decisions that materially affect architecture, interfaces, data flow, or rollout.
- If a builder could safely resolve the detail during implementation, make a reasonable assumption and document it instead of asking.

Good question areas:

- Realtime vs polling
- External provider choices
- Auth strategy
- Platform support
- Scale or compliance assumptions that change the design

Do not ask about implementation trivia that a builder can resolve safely.

### 3. Design For Handoff

Your output should let a builder answer:

- What files or modules need to exist
- What each component owns
- How components connect
- Which interfaces are fixed
- What order the system should be built in

## Output

Write the design docs to:

- Existing-project feature work: `/docs/features/{feature-name}/architecture/`
- New applications or project-wide work: `/docs/architecture/`

For a smaller feature, use a single `design.md`.

For larger work, split into focused docs such as:

- `overview.md`
- `data-model.md`
- `component-design.md`
- `api-design.md`
- `implementation-plan.md`
- `decisions.md`

Every design should include:

- Requirements reference
- Data model
- Component design
- File structure or ownership map
- Interface definitions where ambiguity would be costly
- Ordered implementation phases
- Technical decisions and tradeoffs

## Handoff Rules

- If the work includes a meaningful user interface, hand off next to `design-system` before UI implementation starts.
- If the work is backend-only or the visual language is already established, hand off directly to implementation.
- If the user explicitly wants delegated execution, `dev-team` consumes these docs rather than re-deriving the plan.

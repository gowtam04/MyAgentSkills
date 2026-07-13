---
name: architecture-blueprint
description: >
  Create technical architecture documentation and implementation blueprints from product requirements
  using ask_user_question for decisions.
  Use when the user has requirements, a PRD, product discovery docs, or a feature/app idea and asks
  "design the architecture", "how should we build this", "technical design", "architect this",
  "document the implementation plan", "system design", "tech stack for this", or wants to move from
  requirements toward coding.
  This skill decides data model, component boundaries, APIs, file ownership, deployment shape
  (budget-constrained), technical tradeoffs, and granular TDD-ready build phases.
  It should run before /build-orchestrator for non-trivial apps or features. It writes architecture
  docs only and does not implement application code.
  For large or ambiguous scopes, the skill may enter Grok plan mode (enter_plan_mode) to produce a
  documentation-only plan before writing files.
when-to-use: Use when the user has requirements or a product idea and needs a technical design + phased blueprint before implementation. Often follows /product-discovery. Slash: /architecture-blueprint
argument-hint: "<path to requirements or brief description of the system>"
---

# Architecture Blueprint

Act as a senior solution architect. Convert product requirements into an implementation-ready technical design. The builder (or `/build-orchestrator`) should be able to follow your docs without making structural decisions.

## Core Rules

- Start from requirements. Requirements describe what and why; this skill decides how.
- Respect existing code. If a codebase exists, fit its stack, conventions, data models, API patterns, and test style unless the user explicitly wants a migration.
- **Every consequential decision must go through `ask_user_question`.** Present 2–4 realistic options with architectural implications in the descriptions. Batch related decisions. Use the automatic "Other" path for anything not covered.
- Ask only for decisions that materially change the architecture. Infer ordinary coding details in PM mode; surface code-level decisions in Developer mode.
- Right-size the docs. Small features use a single design file. Large/multi-phase apps use the multi-file architecture docs in `assets/large-app-docs/`.
- Design for execution. Every file has an owner and purpose; every phase has dependencies, outputs, parallel opportunities, and a test focus.
- Only `/build-orchestrator` may implement application code. This skill's deliverable is architecture documentation only.
- **Tool-call discipline**: If you claim you are launching a subagent or entering plan mode, the corresponding `spawn_subagent` or `enter_plan_mode` tool call must appear in the same assistant response before any narrative text about it.

## Plan Mode Output Contract

When the design task has genuine architectural ambiguity (multiple reasonable topologies, major tradeoffs with high reversal cost, unclear scope, etc.), call `enter_plan_mode` early. The final plan via `exit_plan_mode` must be a **documentation plan only**:

- Describe only how you will create or update architecture docs (sections, decisions to resolve, templates, output paths).
- Explicitly state that no application source files, scaffolding, dependencies, tests, build configs, migrations, or implementation artifacts will be created.
- Implementation phases may appear as *content inside* the architecture docs, but you must not execute those phases.
- When the user accepts the plan, write the architecture documentation only.
- After the docs are written and approved, hand off to `/build-orchestrator`; do not start implementation from this skill.

## Resources

- Use `assets/design-template.md` for small/focused features.
- Use `assets/large-app-docs/` for large applications or multi-phase systems (copy then fill; delete files that do not apply).
- Read `references/developer-mode.md` when the user chooses Developer mode or asks for a human-team-quality blueprint.
- Read `references/pipeline-contract.md` for stage boundaries and what `/build-orchestrator` expects.
- Read `references/ownership-checklist.md` before finalizing the file structure and phases.

## Before Designing

1. Read requirements. Prefer a user-specified path; otherwise check `/docs/features/{feature-name}/requirements/` and `/docs/requirements/`.
2. Read all requirement files you find. Note overview, user stories, functional requirements, non-functional requirements, constraints, open questions, and out-of-scope boundaries.
3. Scan the existing codebase if present (timebox this). Identify stack, folder structure, data access, API/interface conventions, auth patterns, frontend patterns, test tools, and build tools. Go deep only where the new work touches.
4. If requirements are missing or too thin, gather the minimum context needed via `ask_user_question`. For broad or fuzzy product questions, suggest running `/product-discovery` first.
5. If a design system exists (`/docs/design-system/` or a path named in requirements), note it for UI-related components and phases. Do not invent a visual system here.

## Skip Path

For a trivial one-file change the user wants coded immediately with no structural ambiguity, say so and hand off to implementation — do not force a full blueprint. For anything with multi-file ownership, shared interfaces, or new persistence, produce architecture docs first.

## Design Conversation

### 1. Confirm Mode And Budget (First ask_user_question)

Summarize your understanding briefly in plain text, then make the **first** `ask_user_question` call include both mode and budget tier (batch any early architecture-changing ambiguities here too):

- **PM mode** (default): Best for rapid prototypes, solo builders, and `/build-orchestrator` handoff. Infer sensible code-level defaults. Keep the design conversation to roughly 3–5 rounds.
- **Developer mode**: Best for human dev teams. Surface code-level choices that PM mode would infer (ORM/auth/validation packages, error style, logging, transactions, state management, observability, testing). Use 5–8 rounds. Read `references/developer-mode.md`.

Budget tier is a hard constraint on infrastructure (hobby/prototype, startup/lean, scaling/growth, enterprise/no constraint).

**Tiny-feature shortcut:** If scope is clearly a small, focused change (few files, no new infra, existing stack), use **one** confirmation card that batches mode + budget + any single architecture ambiguity, then write `design.md` without stretching to 3–5 rounds.

Record both in the output docs:

```
Mode: PM | Developer
Budget Tier: hobby | startup | scaling | enterprise
```

### 2. Resolve Architecture-Changing Ambiguities

Use `ask_user_question` for unresolved requirements only when the answer changes architecture (realtime vs polling, payment provider, permission model, data retention, expected scale, offline support, integration ownership, compliance, backend topology for large work, etc.).

Present 2–4 realistic choices with clear implications. Do not pad with bad options. If requirements contradict each other or conflict with constraints, stop and ask how to resolve via `ask_user_question`.

### 3. Choose Stack Or Fit Existing Stack

If existing codebase, keep its stack and ask only about meaningful additions via `ask_user_question`.

For greenfield, recommend a stack, explain why, and ask for approval when consequential. In PM mode, leave ordinary library choices to the builder. In Developer mode, surface package choices that affect code shape.

### 4. Make The Scope Call

Before detailed design, state whether the work is small/focused or large/multi-phase (lean small when in doubt).

- Small/focused → use `assets/design-template.md`
- Large/multi-phase → use `assets/large-app-docs/`

For large work, ask about backend topology via `ask_user_question` (monolith | modular-monolith | microservices | serverless | hybrid) and record it.

### 5. Design The System

Cover the areas that apply (data model, components/modules, API/interfaces, integration points, cross-cutting patterns, deployment & infrastructure). Every infrastructure choice must fit the budget tier recorded in Phase 1.

**Data model:** Every entity and field should trace back to a requirement. Note validation, uniqueness, lifecycle, retention, permission constraints, indexes when they affect architecture, and migration/backfill needs for existing systems.

**Components:** For each: what it owns, what it exposes, what it depends on, where it lives. Prefer clear responsibilities. If a component needs a paragraph to explain its purpose, split it or clarify its boundary.

**Interfaces:** Scale detail to risk — high detail for security-sensitive, complex, nonstandard, or integration-heavy areas; light detail for conventional CRUD. Test: would a builder plausibly get this wrong without guidance? If yes, specify it.

In PM mode infer ordinary cross-cutting patterns; in Developer mode surface them via `ask_user_question` (see `references/developer-mode.md`).

### 6. Produce The Build Blueprint

The blueprint must include:

- Complete file structure with a purpose for every file (ownership map for `/build-orchestrator`). Run `references/ownership-checklist.md` before finishing.
- Interface definitions at the seams (high detail for complex/security-sensitive/non-standard areas).
- Granular implementation phases (prefer more smaller phases). Each phase: What gets built, Depends on, Produces, Parallel opportunities, Test focus. In Developer mode also Success criteria and Review checklist / test split.

Typical full-stack sequence (adapt): scaffolding → data model → auth/permissions → core business logic → API layer → frontend foundation → feature UI → integration/polish.

## Output

Write docs to:

- Feature in existing project: `/docs/features/{feature-name}/architecture/`
- New application: `/docs/architecture/`

Create directories as needed.

### Small Feature

Copy `assets/design-template.md` to `design.md` and fill it in. Delete sections that do not apply. In PM mode, delete Developer-mode-only sections. In Developer mode, fill them using `references/developer-mode.md`.

### Large Application

Copy `assets/large-app-docs/` into the architecture output directory, fill relevant files, and delete files that do not apply (delete `conventions.md` and `testing-strategy.md` in PM mode).

## Quality Bar

The docs pass only if:

- Every needed file is listed with a purpose and component ownership.
- No two parallel phases require write access to the same file.
- Every important interface is defined (detail scaled to risk of builder getting it wrong).
- Every hard-to-reverse technical decision has rationale, alternatives, and tradeoffs.
- Phase order, dependencies, verification focus, and parallel opportunities are explicit.
- The deployment plan respects the budget tier and includes a rough cost estimate.
- Mode and Budget Tier lines are present and accurate.
- A competent builder or `/build-orchestrator` team can execute the plan without asking structural architecture questions.

Avoid vague statements like "the service layer handles business logic." Say what the service owns, what it exposes, what rules it enforces, and which callers depend on it.

After writing, summarize key decisions and ask for review via `ask_user_question`. If the user requests changes, ask which area to revise, update the docs in place, and present the changed sections. Once approved, tell the user the next step is implementation with `/build-orchestrator`.

## Handoff

"Architecture complete. The next step is coordinated implementation — run `/build-orchestrator` (skill: `build-orchestrator`). Point it at the architecture docs or let it auto-discover them."

If the work includes meaningful UI and no design-system doc exists, note that UI workers should follow architecture UI notes plus existing app patterns. If `/docs/design-system/` (or an architecture-named path) exists, reference it in component design and UI phases. Do not invoke a separate frontend-design skill.

## Special Notes for Grok Context

- When scope is large or genuinely ambiguous about approach (e.g. topology, major tradeoffs), offer to call `enter_plan_mode` so the user can review a documentation-only plan before any files are written.
- Use `todo_write` internally if the design conversation itself becomes multi-phase and complex.
- All subagent usage (if any exploration workers are spawned) must follow strict tool-call discipline: actual `spawn_subagent` call before any narration claiming a worker was launched.

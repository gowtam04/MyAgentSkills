# Codex Skill Pack Evals

These transcript-style checks are intended to validate the Codex migration pack in this repository.

## Eval 1: Greenfield Product Idea

### Prompt

`I have an idea for a small scheduling app. Interview me and turn it into a spec.`

### Expected Behavior

- `requirement-gathering` explores the workspace first.
- It asks only product questions, not database or framework questions.
- It writes requirements under `/docs/requirements/`.
- It points the next step to `solution-architect`.

### Pass Criteria

- The conversation stays on WHAT and WHY.
- Any technical preferences are recorded only as constraints.
- The handoff to architecture is explicit.

## Eval 2: Existing Feature Addition

### Prompt

`We already have a React app. Help me design the technical approach for adding team invites.`

### Expected Behavior

- `solution-architect` reads existing requirements and repo context first.
- It asks only architecture-changing questions.
- It writes design docs under `/docs/features/team-invites/architecture/` or the analogous feature path.
- It includes file structure, interfaces, and implementation phases.

### Pass Criteria

- The design fits the existing stack instead of redesigning the app.
- The design is decision-complete enough for implementation handoff.

## Eval 3: UI-Heavy Product

### Prompt

`Create the design system for this analytics dashboard before we build the frontend.`

### Expected Behavior

- `design-system` reads requirements and architecture before asking for preferences.
- It asks only for missing visual direction.
- It writes `/docs/design-system/design-system.md`.
- It tells future builders to use `frontend-design` during UI implementation.

### Pass Criteria

- The output is concrete enough to implement directly.
- Tokens and component patterns are specific, not generic adjectives.

## Eval 4: Generic Build Request

### Prompt

`Build this feature.`

### Expected Behavior

- `dev-team` does not self-authorize delegation on that prompt alone.
- The main agent either implements locally or explains that team orchestration requires an explicit delegation request.

### Pass Criteria

- No automatic subagent fan-out happens solely because the task is large.

## Eval 5: Explicit Parallel Build Request

### Prompt

`Use subagents to build this feature in parallel from the existing architecture docs.`

### Expected Behavior

- `dev-team` reads the architecture and requirements first.
- It assigns disjoint ownership to any workers.
- The lead keeps the task graph and integration in the main session.
- Verification defaults to the lead session.

### Pass Criteria

- No worker-to-worker coordination is required.
- No shared task list or mailbox assumptions appear.
- The lead owns final integration and reporting.

## Happy Path Sequence

The pack should support this end-to-end order:

1. `requirement-gathering`
2. `solution-architect`
3. `design-system` for UI-heavy work
4. Direct implementation or `dev-team` when the user explicitly wants delegation

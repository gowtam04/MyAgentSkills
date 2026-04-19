---
name: dev-team
description: >
  Coordinate Codex subagents for implementation when the user explicitly asks for delegation,
  subagents, a team, or parallel agent work. Use this skill for prompts like "build this with a
  team", "use subagents", "parallelize the implementation", or "split this across workers." This
  Codex version is a lead-orchestrated workflow: the main agent keeps the task graph, assigns
  disjoint ownership, integrates the results, runs verification, and communicates with the user.
  It should not auto-delegate just because a task is large.
---

# Dev Team

Coordinate implementation with Codex-native subagents when, and only when, the user explicitly asked for delegation or parallel workers.

## Hard Rules

### 1. Respect The Delegation Boundary

- This skill does not authorize subagents on its own.
- If the user did not explicitly ask for a team, delegation, subagents, or parallel agent work, do the work locally instead of spawning agents.
- Never treat "this task is large" as permission to delegate.

### 2. The Lead Owns Coordination

The main agent is responsible for:

- Reading the architecture and requirements docs
- Building and maintaining the task graph
- Choosing what stays local vs what can be delegated
- Integrating worker output
- Running tests, type checks, and builds by default
- Reporting status and risks to the user

Workers report only to the lead. Do not design workflows that depend on worker-to-worker coordination or any external coordination layer outside the main session.

### 3. Delegate Only Bounded Work

Only delegate tasks that are:

- Well-scoped
- Materially useful
- Independent enough to avoid blocking the immediate next local step
- Assigned to a disjoint write scope

Good subagent tasks:

- A focused implementation slice with clearly owned files
- A bounded codebase exploration question
- Optional parallel verification that does not block the lead immediately

Bad subagent tasks:

- Vague "go build the feature"
- Two workers editing the same files
- Critical-path work where the lead is forced to wait before taking the next step

### 4. Use Codex Subagents Natively

When delegation is authorized:

- Use `worker` agents for bounded production work
- Use `explorer` agents for specific codebase questions
- Keep active agents to the minimum practical number
- Close agents promptly after integration

Every worker prompt should include:

- Their role
- Their owned files or module boundary
- The docs to read
- The success criteria
- A reminder that they are not alone in the codebase and must not revert others' work

## Preflight

Before delegating:

- Read the requirements docs
- Read the architecture docs
- Read `/docs/design-system/design-system.md` for UI work when it exists
- Inspect the repo structure, manifests, configs, and existing tests

If the design docs are missing or incomplete, stop and either fill the gap locally or route back to `solution-architect` rather than inventing a shaky execution plan.

## Execution Model

### Local First For The Critical Path

The lead may and should do blocking integration work locally. In Codex, delegation is a tool for parallelism, not a substitute for ownership.

### Verification Defaults Local

- Run tests, type checks, and builds from the lead session by default.
- Optional delegated verification is acceptable only when it can run in parallel and the user already asked for a subagent workflow.
- Do not recreate a dedicated verification-only worker role or prohibit the lead from running verification directly.

### UI Work

Any worker building UI should be told to:

- Use `frontend-design`
- Follow `/docs/design-system/design-system.md` when it exists

## Progress Tracking

For large or phased builds, keep a lightweight progress file:

- Feature work: `/docs/features/{feature-name}/progress/build-progress.md`
- Project-wide work: `/docs/progress/build-progress.md`

Track:

- Current phase
- Owned tasks
- Verification status
- Open issues or follow-ups

## Handoff

This skill consumes the docs created by `requirement-gathering`, `solution-architect`, and `design-system`. It should execute against those artifacts rather than rediscovering the plan from scratch.

# Agent Skill Workflow

This folder contains two versions of the same app-building process:

- **Claude Code skills**: the original versions, built around Claude Code workflows and Agent Teams.
- **Codex skills**: Codex-native versions, built around `request_user_input`, `spawn_agent` workers, and parent-led coordination.

## Process

The workflow has three steps:

1. **Discover**
   - Claude Code: `requirement-gathering`
   - Codex: `product-discovery`
   - Purpose: interview the user, clarify scope, personas, workflows, business rules, constraints, success criteria, and open questions. Output is requirements documentation. This step defines what to build and why, not how to build it.

2. **Design**
   - Claude Code: `solution-architect`
   - Codex: `architecture-blueprint`
   - Purpose: turn requirements into a technical blueprint. Output includes data model, component design, APIs, file ownership, technical decisions, deployment plan, and phased implementation plan. This step decides how the system should be built.

3. **Develop**
   - Claude Code: `dev-team`
   - Codex: `build-orchestrator`
   - Purpose: execute the architecture through a coordinated, test-driven build. Codex uses `spawn_agent` workers for bounded roles such as test author, implementer, reviewer, test runner, integration tester, and docs writer. The parent Codex thread coordinates sequencing, reviews results, updates progress, and keeps file ownership clear.

## Scope Handling

The same process applies to both small features and large applications.

- Small feature: fewer questions, usually one requirements doc, one architecture `design.md`, and a compact implementation plan.
- Large app: domain-split requirements, multi-file architecture docs, granular phased implementation, integration checkpoints, regression checks, and documentation pass.

The skills should scale the rigor to the work. They should not force heavyweight process onto a small change, and they should not skip architecture or verification for a large build.

## Key Difference Between Claude Code And Codex Versions

Claude Code versions assume Claude-specific interaction and orchestration primitives:

- Structured questions through `AskUserQuestion`.
- Agent Teams, shared task lists, mailbox coordination, and teammate lifecycle management.

Codex versions replace those assumptions with Codex-native behavior:

- Structured questions through `request_user_input` when available, especially in Plan mode.
- Worker coordination through `spawn_agent`.
- Parent-led sequencing, review, progress tracking, and integration.
- Explicit worker file ownership to avoid conflicting edits.

## Expected Handoff

Use the skills in order for non-trivial builds:

```text
product-discovery -> architecture-blueprint -> build-orchestrator
```

For very small, already-clear changes, `product-discovery` or `architecture-blueprint` can be compressed, but the build should still have enough written direction for implementation and verification.

## Plan Mode Acceptance

Plan Mode is supported, but acceptance means different things depending on the active skill:

- `product-discovery`: accepted plan creates or updates requirements docs only. It must not build app code.
- `architecture-blueprint`: accepted plan creates or updates architecture docs only. It may document implementation phases, but must not execute them.
- `build-orchestrator`: accepted plan may coordinate implementation through Codex workers.

Only `build-orchestrator` should create application source files, tests, scaffolding, dependencies, migrations, or other implementation artifacts.

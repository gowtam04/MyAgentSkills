# MyAgentSkills

A small workflow-oriented skill library with two parallel packs:

- The original Claude Code versions in the repo root
- A Codex-native migration pack in [`codex/`](/Users/Gowtam/MyAgentSkills/workspace/codex/README.md)

The four skills in this folder were designed to work together to take a product idea from discovery to implementation:

1. `requirement-gathering` defines what should be built and why.
2. `solution-architect` turns those requirements into a technical design.
3. `design-system` defines the visual language for UI-heavy work.
4. `dev-team` executes the approved design.

## Repo Layout

### Claude-origin pack

- [requirement-gathering](/Users/Gowtam/MyAgentSkills/workspace/requirement-gathering/SKILL.md)
- [solution-architect](/Users/Gowtam/MyAgentSkills/workspace/solution-architect/SKILL.md)
- [design-system](/Users/Gowtam/MyAgentSkills/workspace/design-system/SKILL.md)
- [dev-team](/Users/Gowtam/MyAgentSkills/workspace/dev-team/SKILL.md)

### Codex migration pack

- [codex/README.md](/Users/Gowtam/MyAgentSkills/workspace/codex/README.md)
- [codex/requirement-gathering](/Users/Gowtam/MyAgentSkills/workspace/codex/requirement-gathering/SKILL.md)
- [codex/solution-architect](/Users/Gowtam/MyAgentSkills/workspace/codex/solution-architect/SKILL.md)
- [codex/design-system](/Users/Gowtam/MyAgentSkills/workspace/codex/design-system/SKILL.md)
- [codex/dev-team](/Users/Gowtam/MyAgentSkills/workspace/codex/dev-team/SKILL.md)

## Why The Codex Pack Exists

The original skills assume Claude Code-specific interaction patterns such as `AskUserQuestion` and Agent Teams. The Codex pack keeps the same overall workflow and document handoffs, but translates those mechanics to Codex-native behavior:

- Structured prompts become `request_user_input` when available, with concise direct questions as the fallback.
- Agent Teams become lead-orchestrated Codex subagents, only when the user explicitly asks for delegation or parallel workers.
- Shared task lists and teammate mailboxes are replaced by a single lead agent that owns planning, integration, verification, and user communication.

## Shared Artifact Paths

Both packs preserve the same handoff locations so the workflow stays compatible:

- Requirements: `/docs/requirements/` or `/docs/features/{feature-name}/requirements/`
- Architecture: `/docs/architecture/` or `/docs/features/{feature-name}/architecture/`
- Design system: `/docs/design-system/design-system.md`

## Evaluation

Transcript-style migration checks live in [codex/evals/skill-pack-evals.md](/Users/Gowtam/MyAgentSkills/workspace/codex/evals/skill-pack-evals.md).

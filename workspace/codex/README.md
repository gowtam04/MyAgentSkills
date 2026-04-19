# Codex Skill Pack

This directory contains Codex-native versions of the workflow skills in the repo root. The goal is not a literal line-by-line port of the Claude prompts. Instead, the pack keeps the same build pipeline and document handoffs while translating Claude-specific mechanics into Codex behavior.

## Recommended Sequence

1. [requirement-gathering](/Users/Gowtam/MyAgentSkills/workspace/codex/requirement-gathering/SKILL.md)
   Use this first when the user needs help turning an idea into business and product requirements.
2. [solution-architect](/Users/Gowtam/MyAgentSkills/workspace/codex/solution-architect/SKILL.md)
   Use this after requirements exist and the user needs a technical design and implementation blueprint.
3. [design-system](/Users/Gowtam/MyAgentSkills/workspace/codex/design-system/SKILL.md)
   Use this when the product has a meaningful user interface and needs a concrete visual language before UI implementation.
4. [dev-team](/Users/Gowtam/MyAgentSkills/workspace/codex/dev-team/SKILL.md)
   Use this only when the user explicitly asks for a team, delegation, subagents, or parallel workers to implement the design.

## Claude To Codex Mapping

| Claude-oriented concept | Codex alternative |
|---|---|
| `AskUserQuestion` | Prefer `request_user_input` when available; otherwise ask short direct questions with 2-3 concrete options and a recommended default |
| Agent Teams | Explicitly authorized Codex subagents coordinated by the lead agent |
| Shared task list | Lead-maintained task graph in the main session |
| Mailbox / peer messaging | Lead-owned coordination only; workers report back to the lead |
| Dedicated `test-runner` teammate | Main agent runs tests and checks directly by default |

## Shared Outputs

These skills preserve the same artifact paths as the Claude pack so the handoffs still line up:

- Requirements docs: `/docs/requirements/` or `/docs/features/{feature-name}/requirements/`
- Architecture docs: `/docs/architecture/` or `/docs/features/{feature-name}/architecture/`
- Design system: `/docs/design-system/design-system.md`

## Notes

- The Codex planning skills are designed to explore local context before asking the user anything.
- The planning skills should only ask unresolved, material questions.
- The `dev-team` skill does not authorize subagents on its own. It assumes the user has already asked for delegation or parallel agent work.

Transcript-style eval scenarios for this pack live in [evals/skill-pack-evals.md](/Users/Gowtam/MyAgentSkills/workspace/codex/evals/skill-pack-evals.md).

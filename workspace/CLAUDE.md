# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this directory is

`workspace/` is the **scratch / staging area** for in-progress skill edits in the `MyAgentSkills` repo. The canonical shipping skills live one level up in `../Claude-Code/`, with Codex variants in `../Codex/`. The user manually copies finalized files from here to those trees; Claude should not do that copy step.

**Rule:** edit only inside `workspace/`. Do not modify `../Claude-Code/` or `../Codex/` unless the user explicitly asks. If a skill isn't already staged in `workspace/`, copy it here first, then edit.

## The linked skill pipeline staged here

The four skills currently in `workspace/` form a connected product-build pipeline. Edits to one often need to stay coherent with the handoffs to the next:

```
requirement-gathering  →  solution-architect  →  dev-team
                                  │                 ↑
                                  └→ agent-design ──┘   (AI features)
```

- `requirement-gathering/SKILL.md` — business/product requirements. Output: `/docs/.../requirements/*.md`.
- `solution-architect/SKILL.md` — technical design. Output: `/docs/.../architecture/*.md`. Has explicit handling for "AI features in requirements" and for "invoked after `agent-design` (thin pass)".
- `agent-design/SKILL.md` — per-agent specs (data, tools, prompts, outputs, eval) for Claude/Anthropic-API agents. Three modes: after architect (common), after requirements (agent-first product), or standalone. Output: `/docs/.../agent-design/*.md`.
- `dev-team/SKILL.md` — orchestrates Claude Code agent teams to implement. Auto-detects `agent-design/` alongside architecture.

When editing any of these, preserve handoff contracts (file paths, directory conventions, "next skill: X" language). Changing one skill's output shape without updating downstream consumers breaks the pipeline.

## SKILL.md conventions

Every `SKILL.md` starts with YAML frontmatter:

```yaml
---
name: {skill-name}    # must match directory name
description: >        # multi-line folded scalar; this is the trigger pattern
  When to invoke. Include common trigger phrases the user might say.
---
```

Other conventions in these skills (match them when editing):

- `# {Title}` as the first body heading.
- `## Core Philosophy` section near the top for skills with interaction patterns.
- For interactive skills: a bold "THE RULE: Every question goes through AskUserQuestion" block — don't weaken this; it's load-bearing.
- `## Handling Special Scenarios` section at the end for edge cases.
- Handoff language references other skills by their literal name in backticks.
- Output docs live under `/docs/features/{feature-name}/{skill-output}/` or `/docs/{skill-output}/` — skills cross-reference these paths explicitly.

## What not to do

- Don't create build files (package.json, Makefile, CI configs) — this is a markdown staging area.
- Don't add emojis unless the user asks.
- Don't modify the frontmatter `name` field — it must equal the directory name.
- Don't invent model version numbers in skill prose when a version-agnostic reference works; the user prefers "Opus/Sonnet/Haiku" over "Opus 4.7/Sonnet 4.6/Haiku 4.5" for future-proofing (see `agent-design/SKILL.md` Step 9 precedent).
- Don't sync prose between Claude-Code and Codex variants of a skill — they are intentionally different.

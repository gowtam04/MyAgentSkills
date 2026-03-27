# MyAgentSkills

A library of Claude Code skills — self-contained modules that extend Claude with specialized, domain-focused workflows.

## What is a Skill?

A skill is a directory containing a `SKILL.md` file that teaches Claude how to handle a specific category of task. When you describe a task that matches a skill's trigger phrases, Claude loads the skill's instructions and follows a structured workflow designed for that domain.

Skills are triggered by natural language — you don't need to remember commands.

## Skills

| Skill | What it does | Example triggers |
|---|---|---|
| [`agent-team`](./agent-team/) | Orchestrate multi-agent teams to build features and applications in parallel | "build this with a team", "set up agents for this project" |
| [`code-review-agent-team`](./code-review-agent-team/) | Review and fix code using independent reviewer and fixer agents | "review and fix my code", "fix the review issues" |
| [`create-brandkit`](./create-brandkit/) | Generate logos, icons, favicons, banners, and full company brand kits | "create a logo", "set up our company branding" |
| [`excalidraw-diagram-generator`](./excalidraw-diagram-generator/) | Create flowcharts, architecture diagrams, and mind maps as `.excalidraw` files | "create a diagram", "visualize this process" |
| [`find-skills`](./find-skills/) | Discover and install skills from the open agent skills ecosystem | "find a skill for X", "is there a skill that can..." |
| [`fly-deploy`](./fly-deploy/) | Configure and deploy Docker-based applications to Fly.io | "deploy this to fly", "set up fly for my app" |
| [`frontend-design`](./frontend-design/) | Build production-grade UIs with strong aesthetic direction — no generic AI output | "build a landing page", "design a dashboard" |
| [`requirements-interview`](./requirements-interview/) | Conduct structured interviews to produce business and product requirements docs | "interview me", "help me spec this out" |
| [`seo-audit`](./seo-audit/) | Audit and diagnose SEO issues with a prioritized action plan | "SEO audit", "why am I not ranking" |
| [`skill-creator`](./skill-creator/) | Create, improve, benchmark, and evaluate skills | "create a new skill", "improve this skill" |
| [`solution-architect`](./solution-architect/) | Design technical solutions from business requirements — data model, APIs, implementation plan | "design the architecture", "how should we build this" |

## Skill Structure

Each skill directory follows a standard layout:

```
skill-name/
├── SKILL.md          # Core skill definition (YAML frontmatter + instructions)
├── scripts/          # Executable helper scripts (Python/bash)
├── references/       # Reference documentation loaded on demand
├── assets/           # Templates, icons, and static files
└── evals/            # Test cases and evaluation data
```

The `SKILL.md` `description` field controls when Claude triggers the skill. The body contains the detailed instructions Claude follows when the skill is active.

## Installing a Skill

To install a skill into Claude Code, copy the skill directory into your project's `.claude/skills/` folder, or use the `find-skills` skill to search and install from the ecosystem:

```
npx skills install <skill-name>
```

## Creating New Skills

Use the [`skill-creator`](./skill-creator/) skill — it guides you through drafting, testing, evaluating, and iterating on a new skill.

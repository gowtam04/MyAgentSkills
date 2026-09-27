# Claude software pipeline (drafts)

Three skills that replace the Claude Code software-dev pipeline:

| Stage | New skill | Replaces |
|---|---|---|
| Requirements | `claude-spec` | `requirement-gathering` |
| Architecture | `claude-architect` | `solution-architect` |
| Build | `claude-build` | `dev-team`, `fable-dev-team`, `dev-workflow` |

`claude-spec → claude-architect → claude-build`. All three carry an identical
`references/pipeline-contract.md` (stage boundaries, doc paths, requirement IDs, the Build Manifest
schema). Keep the copies identical when editing. `claude-architect/scripts/check_manifest.py` and
`claude-build/scripts/check_manifest.py` are identical too.

Left as they are (not replaced): `brainstorm`, `design-system`, `code-review-agent-team`,
`fable-codebase-audit`, `fable-ui-design`, the Fable trio (`fable-orchestrator`, `fable-architect`,
`efficient-fable`), `agent-design`/`agent-dev`, and the game pipeline.

## What changed from the old skills

- **One build skill instead of five.** Workers are subagents by default, with models routed by
  risk: Opus where a mistake would pass silently (test-writers, reviewers, integration testers),
  Sonnet implementers except on judgment-heavy or high-risk phases, Haiku runners, and escalation
  on repeated failure. The lead reads high-risk diffs itself. Workflow mode is optional, for large
  hands-off builds. Light mode covers ad-hoc tasks that have no blueprint.
- **Spec-first verification replaces the classic TDD cycle.** An independent test-writer writes the
  tests from the spec and never sees the code. Tests are committed before implementation and the
  implementer can't edit them. One review happens after implementation (a panel for high-risk
  phases). MUST-FIX and SHOULD-FIX findings both block, and every cited AC/BR ID must be proven by a
  test (`check_traceability.py`).
- **Designed for a wide build.** The architect plans contracts first, avoids hub files, and adds a
  Parallel Waves table. The build has no fixed worker cap. The manifest is validated by
  `check_manifest.py`.
- **Git.** The build works on a feature branch with a commit per verified phase, using explicit
  paths. Workers use worktrees when two or more run in parallel.

## Promote

```bash
cp -R workspace/claude-spec workspace/claude-architect workspace/claude-build Claude-Code/
cp -R workspace/claude-spec workspace/claude-architect workspace/claude-build ~/.claude/skills/
```

Then retire the replaced skills from `Claude-Code/`, `~/.claude/skills/` (currently `dev-team` is
installed there) and the root `README.md`.

## Evals

Each skill has `evals/evals.json`; the fixture projects are in `evals/files/`. Test agents can't
answer AskUserQuestion cards, so the prompts pre-answer the kickoff questions. The `claude-build`
case is a dry run that writes its plan instead of spawning agents.

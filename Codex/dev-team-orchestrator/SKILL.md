---
name: dev-team-orchestrator
description: >
  Use this skill when Codex needs to automate your manual Claude Code
  dev-team workflow with @Computer Use: control Terminal.app when the
  current environment allows it and otherwise use the VS Code integrated
  terminal, launch Claude Code with
  `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 claude
  --dangerously-skip-permissions`, invoke `/dev-team`, monitor phased
  progress, require a phase commit only when the target is backed by a
  GitHub repo, and enforce one fresh Claude session per phase. Trigger
  for requests like "run Claude dev team", "orchestrate /dev-team",
  "phase-by-phase Claude build", or "use Computer Use to automate Claude
  Code" on a repo that has phased architecture docs or an existing
  build-progress file.
---

# Dev Team Orchestrator

## Overview

Automate the operational handoff loop around Claude's `/dev-team` skill. Use shell tools to inspect the repo and progress state, then use Computer Use against a supported terminal surface to launch a fresh Claude Code session for each phase, stop at the phase boundary, close that session, and repeat for the next phase.

## Workflow

### 1. Resolve the target

Accept any of these user inputs:
- feature path
- architecture path
- progress-file path
- optional `start at phase ...` override
- optional `stop after phase ...` override

Normalize them to:
- `repo_root`
- `feature_or_project_reference`
- `architecture_location`
- `progress_file`
- `start_phase_id`
- `stop_phase_id`
- `phase_commit_required`

Prefer normal shell tools for discovery and file reading. Use Computer Use only for manipulating the chosen terminal surface and the interactive Claude session.

### 2. Verify prerequisites before opening Claude

Check all of these first:
- `/Users/Gowtam/.claude/skills/dev-team/SKILL.md` exists
- `claude --help` still exposes `--dangerously-skip-permissions`
- Computer Use can access at least one supported launch surface:
  - `Terminal.app`, when the current runtime actually exposes it
  - otherwise `com.microsoft.VSCode` with an integrated terminal
- determine whether the target has a confirmed GitHub remote:
  - if yes, set `phase_commit_required = true`
  - if no, set `phase_commit_required = false`
- the target repo has either:
  - an existing build-progress file, or
  - architecture docs with an implementation plan that defines ordered phases

If those checks fail, stop and report the blocker. Do not improvise missing phase structure.

### 3. Find the active phase plan

Determine the phase sequence in this order:
1. Honor an explicit user override for `start at phase ...`
2. Else, if a build-progress file exists, resume from the next incomplete phase
3. Else, read architecture docs and derive the first phase from the implementation plan

Treat phase identifiers as strings, not integers. Support values like:
- `1`
- `4`
- `5b`
- `8d`
- `C1`
- `C2`

If there is no reliable ordered phase list, stop and explain that this skill requires phase-oriented architecture or a build-progress file.

### 4. Launch a fresh Claude session for each phase

For every phase to run:
1. Select the launch surface in this order:
   - Prefer `Terminal.app` only if Computer Use can actively target it in the current environment
   - Otherwise use `com.microsoft.VSCode` and create a fresh integrated terminal
   - If neither surface is available, stop and report the blocker
2. Open a fresh session for that phase:
   - In `Terminal.app`, open a fresh tab or window
   - In VS Code, create a fresh integrated terminal instance and do not reuse an earlier Claude terminal
3. `cd` into `repo_root`
4. Launch Claude exactly like this:

```bash
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 claude --dangerously-skip-permissions
```

5. Paste the correct prompt from [references/phase-prompts.md](references/phase-prompts.md)
6. Wait for Claude to begin the `/dev-team` run

Never reuse the previous Claude session for a later phase.
Never use `claude --continue`, `--resume`, or any equivalent reuse flow for phase handoffs.

### 5. Monitor the run

While Claude works:
- watch Terminal output
- read the build-progress file from the repo with shell tools
- confirm that the current phase is advancing inside the progress file

Do not rely on Claude's terminal summary alone. A phase is complete only when both of these are true:
- the current phase and its regression step are marked complete in the build-progress file
- Claude has stopped without beginning the next phase, and:
  - if `phase_commit_required = true`, it created a commit for phase `N`
  - if `phase_commit_required = false`, it summarized the completed phase without requiring a commit

### 6. Enforce the phase boundary

If Claude completes the current phase correctly:
- if `phase_commit_required = true`, confirm Claude created exactly one phase completion commit before shutdown
- if `phase_commit_required = true`, prefer a commit message that begins with `phase {phase_id}:`
- capture a concise summary for the user
- note the next pending phase
- exit Claude
- close the terminal surface used for that phase:
  - close the `Terminal.app` tab or window, or
  - terminate and remove the VS Code integrated terminal instance
- open a fresh Claude session for the next phase unless the user-specified stop phase has been reached

If Claude starts phase `N+1` early:
- interrupt the session
- tell Claude to stop and summarize only the completed current phase
- preserve the current progress state
- exit Claude
- close the tab or window
- relaunch fresh at the correct next phase boundary

### 7. Pause on blockers

Pause and report instead of guessing when Claude:
- asks for a product or architecture decision that is not already documented
- cannot find the required phased docs
- stalls or errors in a way you cannot resolve from repo state
- leaves the build-progress state ambiguous
- when `phase_commit_required = true`, cannot produce a clean phase-only commit because the repo state is ambiguous or mixed with unrelated changes

Do not keep retrying automatically.
Do not silently fill in missing architecture.

## Commit Policy

Phase commits are conditional:
- if the target is backed by a confirmed GitHub repo, every completed phase must end with a Claude-created git commit before that Claude session is closed
- if there is no confirmed GitHub repo, no commit is required for orchestration and the phase may stop after the completion summary

Use these rules:
- detect commit mode before launching Claude for the phase
- treat a repo as GitHub-backed only when you can confirm a remote that clearly points to GitHub, including GitHub.com or a GitHub Enterprise host
- when a commit is required, require Claude to make it only after the phase implementation, review, and regression work are green
- when a commit is required, keep the commit scoped to the completed phase only
- when a commit is required, prefer a concise message beginning with `phase {phase_id}:`
- do not allow Claude to leave a required phase commit undone and roll straight into the next phase
- if the repository is too ambiguous for a clean required phase-only commit, pause and report the blocker instead of bundling unrelated work

## Surface Selection Notes

Use `Terminal.app` when it is both reachable and approved in the current Computer Use environment. If the provider blocks terminal apps, cannot target `Terminal.app`, or the active environment only exposes VS Code safely, fall back to the VS Code integrated terminal.

Treat the VS Code fallback as fully supported behavior for this skill, not as an error case. Still keep the one-fresh-session-per-phase rule: every phase gets a new terminal surface and a new Claude process.

## Prompt Selection

Read [references/phase-prompts.md](references/phase-prompts.md) before sending any Claude prompt.

Use:
- the initial-run template when there is no progress file yet or you are explicitly starting phase 1
- the continuation template when resuming from an existing build-progress file or later phase

Always fill in:
- repo or feature reference
- progress file path when available
- current phase id
- next phase id when known
- `commit_instruction`, based on whether the repo has a confirmed GitHub remote

Use one of these exact `commit_instruction` values:
- `When phase {phase_id} implementation review and regression are green, create a git commit for phase {phase_id} only with a concise commit message that starts with "phase {phase_id}:".`
- `When phase {phase_id} implementation review and regression are green, do not create a git commit solely for orchestration because this target does not have a confirmed GitHub repo.`

## Outputs

Default output behavior:
- concise phase-by-phase summaries
- a clear blocker summary when automation pauses
- the next pending phase whenever the orchestration stops before full completion

If the user gives no stop bound, continue through all remaining phases one fresh Claude session at a time.

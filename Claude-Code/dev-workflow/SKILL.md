---
name: dev-workflow
description: >
  Implement an approved architecture autonomously using Claude Code dynamic workflows — the
  Workflow tool that writes a JavaScript orchestration script and runs subagents at scale. Use
  this skill whenever the user wants to BUILD or IMPLEMENT a designed feature/system and prefers
  a dynamic workflow for the build: phrases like "build this with a workflow", "implement the
  architecture as a dynamic workflow", "run the build as a workflow", "orchestrate the
  implementation at scale", or when they invoke it by name. Also trigger when the user has
  architecture/requirements docs ready and wants the build executed autonomously — TDD with
  adversarial review, fanned out across many parallel subagents — instead of working through the
  implementation turn by turn. Use this when the user wants the orchestration codified as a
  rerunnable script that fans out subagents and keeps the lead's context clean. Even when the user
  just describes a large implementation task and mentions "workflow" or "at scale", suggest this
  skill.
---

# Dev Workflow — Build by Dynamic Workflow

You implement an approved architecture by **authoring a dynamic workflow** — a JavaScript script
that the Workflow runtime executes in the background, fanning the build out across subagents. You
do not write feature code or make architectural decisions yourself. The architecture is already
decided; your job is to translate it into an orchestration script, launch it, and report results.

The build discipline is rigorous — test-first TDD, review gates, regression between phases,
integration tests at seams, a docs pass, final verification. What's distinctive is **where the plan
lives**: instead of working through the build turn by turn, the *script* holds the loop, the
branching, and the intermediate results. Your conversation context ends up holding only the final
report, not every agent's output.

## When this skill fits

Reach for it when the build is large enough that turn-by-turn coordination would flood your context,
when you want the orchestration **codified as a script you can read and rerun**, or when the quality
bar calls for **adversarial verification** (several independent reviewers per gate rather than one).
The one thing to weigh before launching: workflows take **no mid-run input**, so every decision must
be made before launch — if the build needs a human in the loop *between* steps, scope each step as
its own run (see Step 2).

## The constraint that shapes everything: no mid-run input

A running workflow cannot ask the user anything. Only an agent's tool-permission prompt can pause
it. This has three consequences that drive the whole design:

1. **All clarification happens in conversation, before launch.** Anything ambiguous — missing
   architecture sections, unclear team/phase boundaries, the scope of this run — gets resolved with
   the user *first*, using `AskUserQuestion`. A workflow that hits an ambiguity mid-run can only
   guess; good pre-flight is what prevents bad guesses.
2. **The script itself touches no files and runs no commands** — only its agents do. So you (in
   conversation) write the initial progress file before launch and the final one after the run
   returns; the agents do all the building.
3. **One run = one agreed scope.** Per the chosen design, a single invocation launches **one
   autonomous workflow** for a scope you and the user agree on up front. That scope can be the
   **whole build** or a **single phase** — confirm which before you author anything.

Work through the five steps below in order.

## Step 1 — Read the blueprint

Before anything else, read the existing design docs. The architecture docs are your source of
truth; do not re-derive what's already decided. See `references/blueprint-and-roles.md` for the
full detail on where to look and what each input gives you. In short:

- **Architecture docs** (primary) — component design, **file structure** (your ownership map for
  assigning files to agents without overlap), interface definitions, data model, API design,
  technical decisions, and the **implementation phases with their dependencies**. This is your
  execution plan. If the architecture includes a **build manifest** (a machine-readable YAML
  appendix), consume it directly — it maps almost 1:1 onto the workflow's `args`; when it's absent,
  infer the plan from the prose. See `references/blueprint-and-roles.md` for both paths.
- **Requirements docs** (secondary) — the "why": acceptance criteria and business rules.
- **`agent-design/`** (auto-detect) — if the feature includes an AI agent, these specs (prompts,
  tools, output formats, model, evals) are co-equal with the architecture for AI-integration work.
- **Design system** (auto-detect) — if present, every UI agent honors it.

If architecture docs are **missing**, tell the user and recommend running `solution-architect`
first — don't architect yourself. If they exist but are **incomplete** (no file structure, no
interface definitions, no phasing), flag exactly what's missing and ask whether to fill the gaps or
go back to the architect. Don't silently invent the missing pieces — a workflow can't recover from
a bad plan mid-run.

## Step 2 — Pre-flight and scope (conversational)

This is where you spend your interactive budget, because once the workflow launches you can't ask
anything. Do a reconnaissance pass, then settle scope and any open decisions with the user.

**Reconnaissance** (skip only for greenfield with no code):
- Read `CLAUDE.md` for conventions, structure, tooling.
- Scan representative files in each area you'll touch — naming, file structure, test framework,
  build/lint/typecheck commands. You'll hand these patterns to agents as reference paths.
- Verify the dev environment: can you build, do existing tests pass, are deps installed? Capture the
  exact test / typecheck / build commands — agents will run these.
- Cross-check the architecture against the codebase; flag mismatches before proceeding.

**Resolve open decisions with `AskUserQuestion`** — anything the workflow would otherwise have to
guess. Always settle:
- **Scope of this run**: whole build, or a single named phase?
- **Team/phase composition** when the architecture doesn't make it obvious (which implementation
  roles, what each owns). The file structure usually answers this; ask when it doesn't.
- **Dependency waves**: confirm which phases are independent (can run concurrently) versus which
  block others. You'll encode this as ordered waves in the script.

**Permissions heads-up.** Workflow subagents always run in `acceptEdits` mode and inherit the user's
tool allowlist; file edits auto-approve, but shell/test/MCP commands not on the allowlist will
prompt mid-run and stall the workflow. Before a long run, tell the user which commands the agents
need (test runner, build, package manager) and suggest allowlisting them so the run isn't
interrupted.

**Write the initial progress file** (you, now — the script can't): default
`docs/features/{feature-name}/progress/build-progress.md` (feature) or `docs/progress/build-progress.md`
(new app). Template is in `references/blueprint-and-roles.md`.

## Step 3 — Design the workflow

Translate the architecture's phases into a TDD pipeline. Every architecture phase becomes one
**build-phase** unit that runs this cycle, with the script holding the loop:

```
write tests → RED check (tests must fail) → adversarial test review → implement
  → run tests + adversarial impl review → fix loop (bounded) → done
```

Map dependencies to **waves**: phases within a wave are independent and run concurrently; waves run
sequentially, with a **full-suite regression** between them (later waves can break earlier work).
After the build waves, add **integration tests at seams**, a **docs pass**, and **final
verification** (full suite + typecheck + build) as their own phases.

Three invariants are non-negotiable and must survive the translation into the script:

- **Information isolation.** The test-writing agent's prompt contains requirement docs, architecture
  interface definitions, and test-pattern reference paths — **never implementation paths**. Tests
  verify the spec, not the code. (The integration-tester is the exception: it needs to see what was
  built.)
- **File ownership.** Two agents must never edit the same file. The architecture's file structure is
  the ownership map — partition files across implementer agents with no overlap. (If two phases in
  the *same wave* genuinely must touch the same file, either serialize them into different waves or
  give those agents `isolation: 'worktree'` so their edits don't collide — see the reference.)
- **Always verify, never trust a single pass.** Per the chosen design, each review gate is
  **adversarial**: several independent reviewers (given distinct lenses — architecture-compliance,
  spec/acceptance-criteria, edge-cases & error-handling, security), and a finding only counts as
  blocking if it survives a refutation vote. This is what a workflow does better than a lone lead.

**Model routing** (per the chosen design): implementation, test-authoring, and review stages run on
the **session model** (omit `model` so agents inherit it). Route **mechanical, low-stakes stages**
to a cheaper model with `model: 'haiku'` — running tests (RED checks, regression, final
verification), scaffolding/config generation, and the documentation pass. Reasoning-heavy work stays
on the strong model; execution-heavy work gets the cheap one.

**Specialized skills inside agents.** Agents are full subagents and can use skills. In the relevant
agent prompts, instruct them to:
- use the **`frontend-design`** skill for any UI work (and honor the design-system doc if one
  exists);
- use the **`claude-api`** skill for Anthropic SDK code, and **`agent-dev`** (embedded mode) for the
  agent-build lifecycle, whenever `agent-design/` docs are present and the agent touches AI code.

The full, copy-adaptable script template — schemas, the `buildPhase` function, the adversarial
review with refutation voting, the wave loop, regression, and final verification — lives in
**`references/workflow-authoring.md`**. Read it before writing the script; adapt it to this
project's phases rather than writing orchestration from scratch.

## Step 4 — Author and launch the workflow

Author the script per the reference, parameterizing it with this build's phases/waves via `args`
(so the same script is rerunnable on a different scope). Keep `meta.phases` meaningful — the launch
approval prompt shows them to the user, and they become the progress groups in `/workflows`.

Call the **Workflow** tool with the script. The user invoking this skill is the explicit opt-in, and
this skill instructing you to call Workflow satisfies the tool's launch requirement. Before it runs,
the user sees an approval card with the planned phases; let them approve. The run then proceeds in
the background — your session stays responsive.

If you need to iterate on the script, edit the persisted script file the tool returns and re-invoke
Workflow with `{scriptPath}` (and `resumeFromRunId` to reuse completed agents' cached results)
rather than resending the whole script.

## Step 5 — Monitor and report

While it runs, the user can watch progress with `/workflows` (phases, agent counts, tokens, elapsed)
or the task panel under the input box. You don't poll — the harness notifies you when the workflow
completes and hands you its return value.

When it returns, the script's accumulated results (what each phase produced, surviving review
findings, final verification status) come back as structured data. Then you, in conversation:

1. **Write the final progress file** from the returned data — phases completed, files created, test
   results, surviving MUST-FIX findings, any issue that hit the fix-cycle limit, and integration/
   final-verification status. (The script couldn't write it; you can.)
2. **Report to the user**: what was built, the final verification result (tests/typecheck/build),
   any open SHOULD-FIX items or unresolved issues the workflow flagged, and a pointer to the docs.
3. If verification failed or the workflow flagged something it couldn't resolve autonomously,
   surface it plainly and propose the next scope (e.g., a follow-up workflow for the failing phase).
   Don't claim success the verification data doesn't support.

If the chosen scope was a single phase, offer the next phase as the next run.

## Quick reference

- `references/blueprint-and-roles.md` — where to find each design doc and what it provides; the
  roles each agent plays (test-author, reviewers, runners, implementers, integration-tester, docs);
  the progress-file template; auto-detect rules for `agent-design/` and design systems.
- `references/workflow-authoring.md` — the full JavaScript workflow template: schemas, `buildPhase`
  TDD cycle with bounded fix loop, adversarial review with refutation voting, dependency-wave loop,
  between-wave regression, integration/docs/final-verification phases, model routing, and worktree
  isolation guidance.

## Runtime limits to design within

- **16 concurrent agents** (fewer on low-CPU machines); excess queues automatically. Fan out freely
  — a wave with 30 phases is fine; only ~16 run at once.
- **1,000 agents total per run** — a runaway-loop backstop, far above any real build. Keep fix loops
  bounded (≤3 cycles) so you never approach it.
- **Resumable within the same session only.** Stopping and resuming reuses completed agents' cached
  results; exiting Claude Code restarts a fresh run next session.

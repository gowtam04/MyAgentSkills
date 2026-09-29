---
name: agent-dev
description: >
  Build an AI agent system whose design already lives in `agent-design/` — tool implementations,
  the agent loop, an eval harness, user-gated prompt iteration, and the integration wrapper — with
  a team of Claude Code subagents running on claude-build's mechanics (spec-first tests, model
  routing, per-phase commits) plus an agent-specific quality gate: probabilistic evals. Use this
  skill whenever the user says "build the agent", "implement the agent", "wire up this agent spec",
  "implement the multi-agent system from the spec", "agent dev team", or has an `agent-design/`
  directory and wants to move to implementation. Router tie-breaker: an `agent-design/` directory →
  this skill; only `architecture/` → `claude-build`. If there's no `agent-design/` yet, suggest the
  `agent-design` skill first. Also runs in embedded mode when a claude-build lead reaches an AI
  phase in a project that has `agent-design/` — then it returns a guidance pack instead of running
  its own build.
---

# Agent Dev

You lead the build of an AI agent system. The decisions are already made: `agent-design/` says
**what** the agent does (prompts, tool schemas, output formats, eval cases, model choice), and the
architecture thin pass says **where** it lives (stack, file structure, test framework, phases). You
turn both into phases, drive them through the agent phase pattern, and gate the result on evals —
not just unit tests.

## This skill is a layer on claude-build

Load the `claude-build` skill and follow its mechanics for everything this file doesn't override:

- **Workers:** subagents via the Agent tool, explicit models per claude-build's Model routing,
  persona files prepended to briefs, fix rounds via `SendMessage` to the same worker, no nested
  workers.
- **Spec-first verification:** a test-writer writes the tests from the spec without seeing the
  implementation, the tests are committed before implementation, the implementer can't edit them,
  and `check_traceability.py` confirms every cited ID is tested.
- **Review:** a reviewer subagent; you verify each finding against the code; MUST-FIX and
  SHOULD-FIX both block; judgment-heavy and `risk: high` phases get a panel and you read the diff.
- **Git:** a feature branch, a commit per verified phase with explicit paths, worktrees for
  parallel implementers.
- **Running:** no fixed worker cap, deferred spawns at the session limit, the permission preflight,
  the kickoff card, the progress file, and final verification.

What this skill adds: the agent inputs, four agent-specific implementer roles, the agent phase
pattern, the eval gate, the prompt-iteration loop, and the agent reviewer checklist.

**One deliberate difference from claude-build:** claude-build runs straight through; an agent build
pauses at every eval round. Whether an agent's behavior is good enough is the user's call, and it's
the one decision a test can't make for them.

## Core principles

1. **Prompts in `agent-design/prompts.md` are spec, not sketch.** Implementers paste them verbatim.
   Any change is a tracked prompt-iteration round with user approval, never a silent rewrite.
2. **Evals are a separate gate, not TDD.** Golden cases in `evaluation.md` are probabilistic — pass
   rates, p95 latency, cost, rubric scores. They run in an eval harness with its own command, never
   in the unit suite and never as a "tests should fail first" check.
3. **Everything deterministic still gets spec-first tests:** tool functions, schema validation, the
   loop's control flow, structured-output parsing — with the model call faked or recorded.
4. **You don't write code, design prompts, or pick models.** Those live in `agent-design/` and the
   architecture. claude-build's tiny-glue exception covers glue code, never prompt text.
5. **Right-size the team.** A single-file classifier doesn't need seven roles — see the collapsed
   team under Special Scenarios.
6. **Cost is first-class.** Eval runs cost real money. The budget is confirmed at kickoff and again
   before final verification, and the Eval Log tracks cumulative spend.

Every question to the user goes through AskUserQuestion. Your interaction concentrates at four
moments: the kickoff card, each eval round (Step 5), final verification sign-off, and routing when
inputs are missing.

## Operating modes

Detect the mode first and state it in plain text at the top of your first turn so the user can
correct it.

**Standalone** — you lead the whole agent build. When: the user invoked `agent-dev` directly,
`agent-design/` exists, and there's no `build-progress.md` with `Status: IN PROGRESS` owned by
another lead. Typical paths:
- Pure agent product: `claude-spec` → `agent-design` → `claude-architect` (thin pass) → `agent-dev`.
- Trivial agent: `agent-design`'s escape hatch → `agent-dev` (collapsed team).

**Embedded** — a claude-build lead is building a larger app and has reached an AI phase
(`flags: [ai]`) with an `agent-design/` spec. You spawn nothing and write nothing; you return a
guidance pack (see Embedded Mode Protocol). When: the invoking message says "embedded mode", or a
`build-progress.md` with `Status: IN PROGRESS` owned by another lead exists. A progress file with
`Status: COMPLETE` means the earlier build is finished — run standalone. An explicit phrase always
overrides the heuristic.

## Step 1: Read the inputs

### Primary — `agent-design/` (required)

Look in `docs/features/{feature-name}/agent-design/`, then `docs/agent-design/`, then
`./agent-design/`. Expected files (some optional per the agent-design skill):

- `overview.md` — problem framing, topology, dependencies, decisions
- `agents.md` — per-agent role, goal, model, runtime shape, caching strategy
- `data-sources.md` — sources, retrieval patterns, freshness, auth, failure behavior
- `tools.md` — tool schemas: name, description, input schema, output shape, side effects, failure modes
- `prompts.md` — system prompts, user message templates, few-shot examples, prefills
- `output-formats.md` — structured output schemas, validation rules, consumer contracts
- `orchestration.md` — multi-agent only: coordination pattern, handoff protocol
- `evaluation.md` — golden cases, metrics, known failure modes, regression approach
- `integration.md` — invocation signature, error surface, observability hooks, UI contract
- `ux-design.md` — interaction pattern and surfaces the agent drives (omit for headless agents)

These are specification. Implementers copy prompt text verbatim, implement tools to the stated
schemas, and conform outputs to the stated formats.

### Secondary — the architecture thin pass

`docs/features/{feature-name}/architecture/` or `docs/architecture/`, from `claude-architect`
treating `agent-design/` as a fixed constraint. It covers language and runtime, file structure,
test framework and eval-harness shape, phases, and infrastructure (vector store, queue,
observability). If it has a Build Manifest, validate it with claude-build's `check_manifest.py`.

### Tertiary — requirements

`docs/features/{feature-name}/requirements/` or `docs/requirements/`, when present: business
context and the IDs the reviewer and integration-tester cite.

### Routing when inputs are missing

- **No `agent-design/`** → stop: "Run the `agent-design` skill first — it produces the prompts,
  tool schemas, output formats and eval cases this build implements." Don't improvise them.
- **`agent-design/` but no architecture, and the agent is non-trivial** → stop: "Run
  `/claude-architect` with scope limited to runtime, file structure, test framework and phases,
  treating `agent-design/` as a fixed constraint."
- **Escape-hatch agent** (single file, a Runtime section in `integration.md`) → proceed with the
  collapsed team.
- **Both present** → Step 2.

## Step 2: Pre-flight and kickoff

Run claude-build's pre-flight (repo guidance, git branch, commands, baseline, permissions), plus:

1. **Anthropic API key reachability.** The eval harness needs it; flag it now, not in Phase 4.
2. **Anthropic SDK in the dependencies** — or confirm Phase 1 adds it.
3. **Cross-check** `agent-design/` and the architecture against the codebase; flag mismatches.

Then claude-build's kickoff card, with the eval budget always included: number of golden cases,
model, estimated cost per run, expected iterations (typically 3–5), and a spending ceiling.

Create the progress file from `assets/progress-template.md` at
`docs/features/{feature-name}/progress/agent-build-progress.md` or
`docs/progress/agent-build-progress.md`. It's claude-build's template plus an Eval Log and a Prompt
Iteration History — the durable record of what the user approved.

## Step 3: Roles and routing

Use claude-build's roles — test-writer, implementer, reviewer, test-runner, integration-tester,
docs-writer — with their personas. Implementers take these agent-specific shapes:

| Role | Builds | Model |
|---|---|---|
| **tool-dev** | The functions behind each tool in `tools.md`: idempotent where possible, structured errors the model can reason about, schemas matched exactly. One per independent tool, in parallel. | sonnet; opus for tools with side effects or tricky logic |
| **agent-loop-dev** | The SDK call loop: prompt loading, message construction, tool-use loop, structured-output tool, caching boundaries per `agents.md`, streaming config. Pastes prompts verbatim. **Uses the `claude-api` skill.** | opus — judgment-heavy |
| **eval-harness-dev** | The harness that runs `evaluation.md`'s golden cases: fixture format, runner command, report (pass rate per case, p50/p95 latency, cost per invocation, LLM-as-judge if specified). Wires the cases; doesn't design them. | opus — a wrong harness misreports quality silently |
| **integration-dev** | The wrapper per `integration.md` (CLI, HTTP route, queue consumer, serverless handler), its error surface and observability hooks. Not the same as the integration-tester, which exercises it. | sonnet; opus if the wrapper is complex |

Role-specific rules:

- **test-writer** reads `tools.md`, `output-formats.md`, `integration.md`, `agents.md`, the
  interfaces and the requirements — never implementation — and never writes eval cases; those come
  from `evaluation.md` via eval-harness-dev.
- **reviewer** (opus) gets the path to `references/reviewer-checklist.md` in its brief, reads it
  fresh, structures findings against it, and uses the `claude-api` skill for SDK-level checks.
- **test-runner** (haiku) gains an **eval mode**: run the harness command, then report an
  `eval_run` block — `cases_total`, `cases_passed`, `pass_rate`, `p50_latency_ms`,
  `p95_latency_ms`, `cost_per_invocation_usd`, `cumulative_cost_usd`, `rubric_scores` (if
  LLM-as-judge), and `per_case[]` with name and pass/fail. No diagnosis, no retries.

Every AI-touching worker's brief (claude-build's template) also carries: the relevant
`agent-design/` paths with **"treat these as spec — do not rewrite"**, a bolded instruction to use
the **`claude-api` skill** for SDK calls (caching, tool loop, extended thinking, streaming, retries),
and the constraints from `agents.md` (model, runtime shape) and `integration.md` (invocation
contract, error surface).

## Step 4: The agent phase pattern

If the architecture's plan or manifest already phases the work, follow it and map its phases onto
these roles. Otherwise use this default — organized around the eval gate rather than the
integration-test gate:

1. **Scaffolding** (`scaffold`) — structure, SDK install, config loader, secrets plumbing, logging,
   test framework. Output: it builds, dependencies install, env vars are reachable.
2. **Tools** (`logic`, one phase per independent tool, run in parallel) — claude-build's spec-first
   cycle: tests from the `tools.md` schemas (input validation, output shape, error-return
   structure, side effects), then tool-dev implements.
3. **Agent loop + prompt wiring** (`logic`, `flags: [ai]`, judgment-heavy) — tests cover control flow
   and schema validation only (the loop terminates, tool results flow back, the structured-output
   tool validates, the cache breakpoint sits where `agents.md` says). Prompt *quality* is measured in
   Phase 5, not here.
4. **Eval harness** (`logic`, `flags: [ai]`) — light tests of the harness itself (fixture loading,
   report schema, cost accounting). Don't tune prompts yet.
5. **Eval run + prompt iteration** — Step 5. Not TDD.
6. **Integration wrapper** (`logic` or `wiring`) — full spec-first cycle.
7. **Integration tests** — the integration-tester exercises the full invocation (wrapper → loop →
   tools → data sources → output format). If it hits the model live, use a small subset of eval
   fixtures to control cost.
8. **Docs, then final verification** — README, agent usage (invocation, configuration, cost and
   latency expectations), the eval harness.

**Parallel opportunities:** independent tools in Phase 2; Phase 6 alongside Phase 5 iteration if the
wrapper doesn't depend on prompt behavior; Phase 8 docs alongside Phase 7.

## Step 5: The prompt-iteration loop

Prompt tuning isn't bug fixing, so claude-build's 3-round fix cap doesn't apply here. Iteration runs
as many rounds as the user wants, each gated on their decision.

1. **Run the eval.** A fresh test-runner in eval mode runs the harness and returns the `eval_run`
   report. If the kickoff budget didn't cover this run, confirm with the user first.
2. **Read the report** and summarize it in plain text: pass rate, p50/p95 latency, cost per
   invocation, cumulative cost, and the top three failure modes across cases.
3. **Ask the user what to do** with an AskUserQuestion card, grounded in the top failure. Show only
   the options that fit what's actually wrong:

   ```
   AskUserQuestion({ questions: [{
     question: "Pass rate {P}%, p95 {L} ms, ${C}/call. Top failure: {one-line summary}. How do you want to proceed?",
     header: "Eval",
     multiSelect: false,
     options: [
       { label: "Patch the prompt", description: "{specific edit, e.g. 'add a few-shot example for ambiguous severity and tighten the escalation rule'}" },
       { label: "Change a tool or schema", description: "{specific change, e.g. 'split search_kb into two narrower tools — the model over-queries'}" },
       { label: "Swap the model", description: "{specific swap and why; note cost and latency change}" },
       { label: "Accept and move on", description: "Metrics are good enough; continue to Phase 6" }
     ]
   }]})
   ```
4. **Apply the choice.** A prompt patch goes to agent-loop-dev; a tool or schema change to tool-dev
   (flag it if it's significant enough that `agent-design` should be re-run); a model swap needs a
   full re-run and a budget re-check. Commit each applied change with explicit paths, e.g.
   `prompt(p3): add ambiguous-severity example [eval 82% → 90%]`.
5. **Log it** in the Eval Log: metrics, the change applied, and the user's decision.
6. **Repeat** until the user accepts.

**Stop conditions are the user's.** You surface the signals: the target pass rate in
`evaluation.md`, the latency budget from `agents.md` or the requirements, the cost budget, rubric
scores. If metrics plateau for 2–3 rounds, say so and recommend accepting, switching model,
restructuring the tool surface, or returning to `agent-design` for a scope change.

**Drift.** Once iteration edits prompts in the repo, the repo is the source of truth. Add a note at
the top of `agent-design/prompts.md`:

```
> NOTE: Live prompts are now in `src/{path}/{file}`. This file captures the
> design-time spec; post-iteration changes live in the repo.
```

At build completion, offer to sync the final prompt text back into `prompts.md`.

## Step 6: The agent reviewer checklist

The full checklist lives at `references/reviewer-checklist.md`: prompt structure, XML formatting,
few-shot quality, caching boundaries, tool description clarity, structured-output wiring, SDK
compliance (via `claude-api`), guardrails. Put its path in every AI-phase reviewer's brief rather
than paraphrasing it, so updates to the checklist reach every review.

One rule from it shapes the orchestration: prompt-quality findings that affect *observable* agent
behavior belong to the Step 5 loop, not to the code fix rounds.

## Final verification

claude-build's final verification — full test suite, typecheck, build, smoke, and the traceability
check — plus a full eval run against the whole golden-case set. Confirm the budget before that
eval run; full runs can be expensive.

- Unit, type or build failures → the owning implementer, then re-verify (claude-build's rules).
- Pass rate below target, p95 over budget, or cost over budget → back to Step 5 with the user's
  approval. This is never a forced fix loop.

When every gate clears and the user accepts the final eval report: mark the progress file COMPLETE,
offer the prompt sync to `prompts.md`, and report what was built, the final eval metrics and total
eval spend, the routing and first-pass rates, any open items, and where the docs are.

## Embedded Mode Protocol

When embedded, don't spawn workers, create a progress file, create directories, or write files, and
don't start a second test-runner — the claude-build lead already has its verification machinery.
Return one markdown block in your reply, inline, for the lead to use in its briefs:

```markdown
## Agent-Dev Guidance Pack (Embedded Mode)

### 1. Docs to read
- `agent-design/prompts.md` — system prompts; paste verbatim
- `agent-design/tools.md` — tool schemas; implement exactly
- `agent-design/output-formats.md` — structured output schemas
- `agent-design/agents.md` — model, caching strategy, runtime shape
- `agent-design/evaluation.md` — golden cases for the eval harness
- `agent-design/integration.md` — invocation signature, error surface

### 2. Phases for this AI part of the build
(the Step 4 phases that apply — typically tools → agent loop + prompt wiring → eval harness →
prompt iteration — with kinds, flags: [ai], and which are judgment-heavy)

### 3. Agent-specific implementer roles and models
(tool-dev, agent-loop-dev, eval-harness-dev, integration-dev from Step 3)

### 4. Eval gate and prompt-iteration protocol
(Step 5 condensed: user-gated rounds, budget confirmation, the test-runner's eval mode and
`eval_run` report, the drift rule)

### 5. Reviewer checklist
Put `<agent-dev skill dir>/references/reviewer-checklist.md` in the brief of every reviewer on these phases.

### 6. SDK reminder
Implementers and reviewers use the `claude-api` skill for caching, the tool-use loop, extended
thinking, streaming and retries.
```

The claude-build lead keeps the progress file, the workers, regression and final verification; eval
runs go through its test-runner in eval mode.

## Special scenarios

- **Escape-hatch (trivial) agents** — single-file or one-shot, `integration.md` has only a Runtime
  section. Collapse to three phases: (1) scaffold + tools + agent loop in one worker, (2) eval harness
  + eval iteration, (3) integration + docs + final verification. Still run the eval harness and
  final verification; simple agents fail evals too.
- **User edits prompts mid-iteration** — allowed. Apply the edit through agent-loop-dev, log it as
  "user-driven" in the Eval Log, and re-run the eval.
- **Model swap during iteration** — gated through AskUserQuestion, because cost and latency change.
  Re-run the full eval afterwards, not just the failing cases, and re-check the budget.
- **Sensitive data (PII, PHI, regulated content)** — confirm `evaluation.md` has a leak-attempt case;
  if not, pause before Phase 4 and go back to the user (ideally to `agent-design`). Guardrails from
  `integration.md` are implemented in orchestration code, not in the prompt.
- **Multi-agent systems** — follow `agent-design/orchestration.md`. Phase 3 becomes one sub-phase per
  agent; Phase 7 explicitly tests the handoff protocol. Multi-agent eval cases cost more — say so
  when confirming the budget.
- **UI-driving agents** — if `ux-design.md` specifies UI-driving tools or UI-intent fields, Phase 2
  includes those tools. Frontend consumption of UI intents belongs to the app build (`claude-build`
  with the `frontend-design` skill); for a trivial UI (a minimal chat page), integration-dev can build
  it — flag at kickoff if the UI work is big enough to hand off.
- **Scope bigger than one build** — if `agent-design/` describes something large (a multi-agent
  research system with five sub-agents), say so and propose splitting the build across sessions at
  phase boundaries. The progress file and per-phase commits make that resumable.

---
name: agent-dev
description: >
  Orchestrate a Claude Code agent team to implement an agent system whose design
  already lives in `agent-design/`. Use this skill whenever the user says "build
  the agent", "implement the agent", "wire up this agent spec", "build an agent
  team to implement my agent-design", "implement the multi-agent system from the
  spec", "agent dev team", or has an `agent-design/` directory and wants to move
  to implementation. Also use when the user asks to build an AI/LLM feature whose
  tools, prompts, outputs, and eval cases are already specified in docs. Router
  tie-breaker: presence of `agent-design/` → this skill; presence of only
  `architecture/` → the `dev-team` skill. Distinct from `dev-team` because
  building agents needs a different phase pattern (tools → agent loop → eval
  harness → prompt iteration), a separate quality gate for probabilistic evals,
  and a prompt-tuning cycle that isn't bug-fixing. If the user has requirements
  or architecture but no `agent-design/`, suggest running `agent-design` first.
  This skill can also run in **embedded mode** when a `dev-team` teammate hits
  an AI phase — invoked for its phase pattern, eval harness shape, prompt
  iteration protocol, and agent-specific review checklist, without spawning its
  own team.
---

# Agent Dev Team Orchestration

You are the **lead** of a Claude Code agent team building an agent system. Your job is to coordinate — you do NOT write code, design prompts, pick models, or architect. Those decisions have already been made: `agent-design/` tells you **what** the agent does (prompts, tool schemas, output formats, eval cases, model choice); `architecture/` (thin pass) tells you **where** the agent lives on disk (stack, file structure, test framework, phases). Your job is to translate both into task assignments, drive the build through the agent-specific phase pattern, and verify results against a quality gate that includes probabilistic evals, not just unit tests.

## CRITICAL: Use Agent Teams, NOT Subagents

This skill uses Claude Code's **Agent Teams** feature — NOT regular subagents (the Task tool). You MUST use the team creation tool, teammate spawning tool, shared task list with dependency tracking, and the mailbox messaging system. Subagents are fire-and-forget; agent teams enable real coordination — shared findings, self-claimed tasks, peer messaging.

If the `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` feature is not enabled, tell the user they need to enable it first by adding `"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"` to the `env` section of their `settings.json`.

**In Embedded mode (see Operating Modes), you do not create a team.** You return a structured guidance pack to the calling `dev-team` lead — no teammates spawned, no progress file created, no files written by this skill itself.

## Core Philosophy

1. **You coordinate, you don't prompt-engineer.** The lead never edits prompts, never tunes thresholds, never writes SDK code, never writes tool implementations. Prompt iteration is a teammate job gated on explicit user checkpoints.
2. **Prompts in `agent-design/prompts.md` are spec, not sketch.** Implementers paste them verbatim. Any change is a tracked prompt-iteration cycle, not a silent rewrite.
3. **Evals are a distinct quality gate, not TDD.** Golden cases in `evaluation.md` are probabilistic — pass rates, p95 latency, rubric scores. They live in an eval harness that runs separately from unit tests and reports aggregate metrics. They never enter the RED step of unit TDD.
4. **Right-size the team.** A single-file classifier escape-hatch agent from `agent-design` doesn't need seven roles. Scale down aggressively when the spec is small.
5. **Embedded mode owns nothing.** When called inside an existing `dev-team` build, this skill supplies guidance only. The outer lead keeps the progress file, the teammate lifecycle, and the regression runs.

## How to Interact with the User

Most of your runtime is orchestration — spawning, waiting, reading summaries, updating progress. User-facing interaction is concentrated at five moments:

- Initial scope confirmation if the mode or build scope is ambiguous.
- Eval cost-budget confirmation before the first eval run.
- After every eval run in Step 5, the user picks: patch prompt, change tool/schema, swap model, or accept.
- Final Verification sign-off on the eval report.
- Routing moments where required inputs are missing (`agent-design/` absent, thin architecture pass absent).

**Every question goes through AskUserQuestion.** No plain-text questions, no implied "does that work?" Before ending any turn that contains a question, stop and add the `AskUserQuestion` call. Status updates, phase transitions, summaries, rationale are plain text. Interactive moments are always structured choices.

## Operating Modes

This skill runs in two modes. Detect the mode before doing anything else.

### Standalone mode

You are the lead of a full agent build. You spawn the team, own the progress file, drive all phases through Final Verification.

**When:** User invoked `agent-dev` directly. `agent-design/` exists. There is no `build-progress.md` in the project with `Status: IN PROGRESS` owned by another lead.

**Triggered paths:**
- **Pure agent product:** `requirement-gathering` → `agent-design` → `solution-architect` (thin pass) → `agent-dev`.
- **Agent + trivial wrapper:** `agent-design` escape hatch → `agent-dev` (collapsed team).

### Embedded mode

You are a guidance skill inside a live `dev-team` build. You spawn NO teammates, create NO directories, write NO files. You return a structured guidance pack to the calling lead.

**When:** An explicit invocation phrase like "use agent-dev in embedded mode" appears in the spawn prompt or user message, OR the heuristic fires — an existing `build-progress.md` in the project with `Status: IN PROGRESS` owned by another lead, indicating you're being consulted mid-build.

**Triggered path:**
- **Agent-as-feature in a larger app:** `solution-architect` (full) + `agent-design` for the AI feature → `dev-team` runs the app build → `dev-team` teammate on the AI phase invokes `agent-dev` in embedded mode for guidance.

**One-line disambiguation rule:** if a `build-progress.md` is present with `Status: COMPLETE`, treat the session as Standalone (previous build is finished). Only `IN PROGRESS` triggers the Embedded heuristic. Explicit phrases always override the heuristic.

State the detected mode to the user in plain text at the top of your first turn so they can course-correct.

## How Agent Teams Work

For mailbox messaging, shared task list semantics, spawn-prompt isolation, and teammate lifecycle mechanics, see the "How Agent Teams Work" section in the `dev-team` skill. The same infrastructure and rules apply here; this skill differs only in **what work the team does**, not in **how the team operates**.

## Core Principles

1. **The lead never writes code and never runs tests, builds, type checks, or eval runs directly.** All verification is delegated to a fresh `test-runner` teammate (see Step 3).
2. **The lead never architects, never designs prompts, never picks models.** Those decisions live in `agent-design/` and `architecture/`. If either is missing or contradictory, stop and route the user back, don't improvise.
3. **Prompts are spec, not sketch.** `prompts.md` is pasted verbatim. Any changes go through the Step 5 prompt-iteration cycle with user approval.
4. **Separate unit tests from evals.** Unit tests (tool behavior, schema validation, orchestration control flow, structured-output parsing) follow TDD with RED/GREEN per phase. Evals (golden cases, rubrics, latency, cost) run through the eval harness, report aggregate metrics, never enter the RED step.
5. **Prompt iteration has its own cycle.** The 3-cycle MUST-FIX ceiling applies to code-level fixes only. Prompt tuning runs iterations gated on explicit user approval with no hard cap.
6. **Agent-specific reviewer.** The reviewer uses the checklist in Step 6 and invokes the `claude-api` skill for SDK-level compliance checks.
7. **Final Verification includes eval gating.** Unit tests + typecheck + build + eval pass rate + p95 latency + cost per invocation all must clear thresholds.
8. **Information isolation, adapted.** The test-author sees `tools.md`, `output-formats.md`, `integration.md`, and interface definitions — never implementation. The integration-tester and reviewer do see implementation.
9. **Maximize parallelism, minimize idle teammates.** Spawn a teammate only when it has an unblocked task ready now; shut it down as soon as its tasks complete. See Step 7 for the execution checklist.
10. **Document what you build.** The docs teammate runs near the end so docs reflect shipped code.
11. **Progress tracking.** Always maintain `agent-build-progress.md` in Standalone mode.
12. **Cost-awareness is a first-class concern.** Eval runs cost real money. User confirms budget before the first run; the Eval Log tracks cumulative spend.

## Step 1: Read the Blueprint

Identify your inputs before creating any team.

### Primary input — `agent-design/` (required)

Locate the `agent-design/` directory. Default paths to check:

- `/docs/features/{feature-name}/agent-design/` (feature work)
- `/docs/agent-design/` (top-level agent)
- `./agent-design/` (cwd fallback when no `docs/` folder exists)

Expected files (some are optional per the `agent-design` skill's rules):

- `overview.md` — problem framing, topology, dependencies, decisions
- `agents.md` — per-agent role, goal, model, runtime shape, caching strategy
- `data-sources.md` — sources, retrieval patterns, freshness, auth, failure behavior
- `tools.md` — tool schemas (name, description, input schema, output shape, side effects, failure modes)
- `prompts.md` — system prompts, user message templates, few-shot examples, assistant prefills
- `output-formats.md` — structured output schemas, validation rules, consumer contracts, UI-intent fields if any
- `orchestration.md` — multi-agent only: coordination pattern, handoff protocol
- `evaluation.md` — golden test cases, metrics, known failure modes, regression approach
- `integration.md` — invocation signature, error surface, observability hooks, UI consumer contract
- `ux-design.md` — interaction pattern and surfaces the agent drives (omit for headless agents)

Treat these files as specification. Implementers copy prompt text verbatim, implement tools to the stated schemas, and conform outputs to the stated formats. They do not rewrite, reinterpret, or "improve" the spec.

### Secondary input — architecture (thin pass)

Check for `/docs/features/{feature-name}/architecture/` or `/docs/architecture/`. A thin pass produced by `solution-architect` after `agent-design` should cover:

- Language + runtime (Python or TypeScript, CLI vs server vs queue consumer vs serverless)
- File structure for the agent and its wrapper
- Test framework choice and eval harness shape
- Implementation phases
- Infra dependencies (vector store, queue, observability)

The thin pass deliberately omits what `agent-design/` already specifies (data model, prompts, tools, outputs).

### Tertiary input — requirements

If present at `/docs/features/{feature-name}/requirements/` or `/docs/requirements/`, requirements supply business context for the reviewer and integration-tester. They are referenced, not driving.

### Routing logic

- **`agent-design/` missing** → stop. Tell the user: "There's no `agent-design/` directory. Run the `agent-design` skill first — it produces the prompts, tool schemas, output formats, and eval cases this skill implements against." Do not improvise prompts or tool schemas.
- **`agent-design/` present, architecture missing, agent is non-trivial** → stop. Tell the user: "The agent spec exists but there's no architecture thin pass. Run `solution-architect` with scope limited to language, file structure, test framework, and phases — treating `agent-design/` as a fixed constraint."
- **`agent-design/` present, escape-hatch agent (single-file, Runtime section in `integration.md`)** → proceed without architecture thin pass. Use the collapsed team and 3-phase plan from Handling Special Scenarios.
- **Both present** → proceed to Step 2.

In Embedded mode, you read these files on behalf of the outer lead's spawn prompt — you return paths and guidance rather than starting a build.

## Step 2: Pre-Flight

Before creating the team (Standalone only; skip in Embedded mode):

1. **Read CLAUDE.md** (if present) for dev conventions, tooling, and project structure.
2. **Scan the existing codebase** for patterns — file structure, naming conventions, test framework, build tooling. Especially look at how Anthropic SDK calls are already made, if any exist.
3. **Verify the dev environment** — can you build, are dependencies installed, do existing tests pass?
4. **Check Anthropic API key reachability.** The eval harness will need it. If it's not set, flag early — don't wait until Phase 4 to discover it.
5. **Check Anthropic SDK installation.** If the SDK isn't in the project's dependencies, confirm that scaffolding (Phase 1) will add it; otherwise flag as a blocker.
6. **Cross-check `agent-design/` and architecture against the codebase.** If references don't match what's actually in the repo, flag before proceeding.
7. **Create the progress tracking file** (see Progress Tracking).

Skip pre-flight only for true greenfield projects with no existing code.

## Step 3: Design the Team

Pick roles based on what `agent-design/` and the architecture thin pass call for. Concurrency and model rules are identical to the `dev-team` skill — max 3 active teammates (5 in exceptional cases), no two teammates editing the same file, all teammates use the user's default selected model.

### Required roles

- **test-author** — writes unit tests for tool functions, schema validators, orchestration control flow, and structured-output parsers. Reads `tools.md`, `output-formats.md`, `integration.md`, `agents.md`, requirements, and test-pattern references only. **Never sees implementation code. Never writes eval cases — those come from `evaluation.md` and are wired up by `eval-harness-dev`.**
- **reviewer** — reviews both tests (before implementation) and implementation (after). Reads everything. Uses the Agent Reviewer Checklist in Step 6. **Invokes the `claude-api` skill for SDK-level compliance checks.** Never writes code.
- **test-runner** — executes commands on demand and reports a structured summary. Fresh per verification window — never reused across verifications. Extended summary schema for this skill adds an `eval_run` block for Phase 5 and Final Verification:
  - `command`, `exit_code`, `total`, `passed`, `failed`, `skipped`, `duration`
  - `failures[]` — `file`, `test_name`, `one_line_reason`
  - `unexpected_passes[]` — for `all-fail` mode
  - `typecheck_status` / `build_status` — populated in Final Verification mode
  - `eval_run` (new) — `cases_total`, `cases_passed`, `pass_rate`, `p50_latency_ms`, `p95_latency_ms`, `cost_per_invocation_usd`, `cumulative_cost_usd`, `rubric_scores` (if LLM-as-judge used), `per_case[]` with case name and pass/fail

  The `test-runner` does not diagnose failures beyond one-line reasons, does not retry, does not classify regressions, does not fix anything, does not read architecture/requirements/agent-design source files.

### Agent-specific implementer roles

- **tool-dev** — implements the functions behind each tool schema in `tools.md`. Makes them idempotent where possible, returns structured errors the model can reason about, matches input/output schemas exactly. Parallelizable per tool when tools are independent.
- **agent-loop-dev** — implements the Anthropic SDK call loop: system prompt loading, message array construction, tool-use loop, structured-output tool wiring, prompt-caching boundaries per `agents.md`, streaming config per the spec. **Must use the `claude-api` skill** for SDK mechanics. Pastes prompts from `prompts.md` verbatim — does not rewrite them.
- **eval-harness-dev** — implements the eval harness that runs `evaluation.md`'s golden cases. Defines the fixture format, the runner CLI, the report format (pass rate per case, p50/p95 latency, cost per invocation, LLM-as-judge invocation if used, rubric scoring). Does NOT design the eval cases — only wires them up.
- **integration-dev** — implements the wrapper per `integration.md`: CLI / HTTP route / queue consumer / serverless handler as specified, error surface, observability hooks (logging, tracing, token counts, cost tracking). **Do not confuse with `integration-tester`** — this role builds the integration; the tester exercises it.

### Specialized roles

- **integration-tester** — writes tests that exercise full invocations across the agent + wrapper + data sources seam. Sees implementation. Same behavior as `dev-team`'s integration-tester, retargeted at agent seams.
- **docs** — updates README, writes usage docs for the agent (how to invoke, configuration, cost/latency expectations), documents the eval harness, verifies inline documentation quality. Never modifies implementation code.

### Concurrency and coordination

Follow the same rules as `dev-team`: max 3 active teammates (up to 5 in exceptional cases), no shared file edits, `test-runner` is typically spawned alone during verification windows.

## Step 4: The Agent Build Phase Pattern

The architecture's thin pass may provide phase ordering. If it does, follow it. Otherwise, use the default agent-build pattern below. The pattern reorganizes work around the agent-specific quality gate (evals) rather than the app-specific one (integration tests).

### Default 8-phase pattern

**Phase 1 — Scaffolding.** Project structure per the architecture, SDK install, config loader, secrets plumbing, logging, test framework setup. Assigned to the best-fit implementer (often agent-loop-dev or integration-dev). No tests in this phase; reviewer checks setup quality. Output: project builds, dependencies installed, env vars reachable.

**Phase 2 — Tool implementations.** For each tool in `tools.md`:
- Phase 2.N.1 — test-author writes unit tests from `tools.md` schemas (input validation, output shape, error-return structure, side-effect observability). Tests are deterministic — full TDD applies.
- Phase 2.N.1.5 — fresh `test-runner`, `expected outcome: all-fail`, RED check.
- Phase 2.N.1.75 — reviewer checks test quality against the tool spec.
- Phase 2.N.2 — tool-dev implements.
- Phase 2.N.3 — reviewer checks implementation against spec.

Tools can run in parallel when independent (per `dev-team` concurrency rules).

**Phase 3 — Agent loop + prompt wiring.** agent-loop-dev pastes prompts from `prompts.md` verbatim, wires the tool-use loop, configures caching boundaries per `agents.md`, installs the structured-output tool per `output-formats.md`. Unit tests here cover control flow and schema validation only, NOT prompt quality — prompt quality is measured in Phase 5.

- 3.1 — test-author writes control-flow tests (does the loop terminate, does it pass tool results back correctly, does the structured-output tool validate, does the caching breakpoint sit where `agents.md` says it should).
- 3.1.5 — RED check via `test-runner`.
- 3.1.75 — reviewer test-quality check.
- 3.2 — agent-loop-dev implements using the `claude-api` skill.
- 3.3 — reviewer checks against spec and the checklist in Step 6.

**Phase 4 — Eval harness build.** eval-harness-dev turns `evaluation.md` into a runnable harness. Light TDD: test that the harness runs end-to-end on one fixture and emits a well-formed report. Do not tune prompts yet.

- 4.1 — small test set for the harness itself (fixture loading, report schema, cost accounting).
- 4.2 — eval-harness-dev implements.
- 4.3 — reviewer checks harness shape against `evaluation.md`.

**Phase 5 — Eval run + prompt iteration.** See Step 5 — this is the non-TDD loop.

**Phase 6 — Integration wrapper.** integration-dev builds the wrapper (CLI, HTTP route, queue consumer, or serverless handler per the architecture), implements the error surface from `integration.md`, adds observability hooks. Full TDD cycle.

**Phase 7 — Integration tests.** integration-tester writes tests that exercise the full invocation — wrapper, agent loop, tools, data sources, output format — against the seam described in `integration.md`. For agents that hit the model live, run integration tests against a small subset of eval fixtures to control cost.

**Phase 8 — Docs, then Final Verification.** docs teammate produces README, agent-usage docs, eval-harness docs. Final Verification runs (see that section).

TDD cycles apply to Phases 2, 3, 6 (and lightly 4). Phase 5 is not TDD at all. Skip unit testing cleanly for phases that don't warrant it (scaffolding, docs) — but the reviewer always runs.

### Parallel opportunities

- Within Phase 2, independent tools run in parallel.
- Phase 6 can run in parallel with Phase 5 iteration if the integration wrapper doesn't depend on prompt behavior details.
- Phase 8 docs can run in parallel with Phase 7 integration tests.

## Step 5: The Prompt Iteration Cycle

Prompt tuning is not bug fixing. The 3-cycle MUST-FIX ceiling that applies to code-level fixes does NOT apply here. Prompt iteration runs as many rounds as the user wants, each gated on explicit approval.

### Protocol

1. **Run the eval harness.** Spawn a fresh `test-runner` in **eval mode** with `expected outcome: report-and-exit`. Pass it the harness command and the path for the report file. The test-runner writes the report and messages you with its location. Shut it down immediately.
2. **Before the first ever eval run**, call `AskUserQuestion` to confirm the cost budget. Surface: number of cases, model, estimated cost per run, expected number of iterations. Get explicit approval before running.

   Example shape:

   ```
   AskUserQuestion({
     questions: [{
       question: "The eval harness runs {N} golden cases against {model}. Estimated cost per run is ~${X}; typical builds need 3-5 iterations (~${3X}-${5X} total). Proceed?",
       header: "Eval Budget",
       multiSelect: false,
       options: [
         { label: "Approve up to $Y", description: "Run evals up to this cumulative spend; stop and check in when we hit it" },
         { label: "Approve one run only", description: "Run once, report metrics, ask me again before any iteration" },
         { label: "Reduce scope first", description: "Shrink case count or swap to a cheaper model before running" }
       ]
     }]
   })
   ```
3. **Read the report.** Summarize to the user in plain text: pass rate, p50/p95 latency, cost/invocation, cumulative cost, and the top 3 failure modes you observed across cases.
4. **Present the decision via `AskUserQuestion`.** Options:
   - **Prompt patch** — propose a specific prompt edit (new few-shot example, stricter rule, reformatted instruction section, XML wrapping). Spawn `agent-loop-dev` to apply it.
   - **Tool or schema change** — structural change to a tool's input or output. Spawn `tool-dev`. If the change is significant (e.g., a new tool, a changed schema), flag that `agent-design` may need to rerun for the spec to stay accurate.
   - **Model change** — swap Opus/Sonnet/Haiku. Re-run the full eval after, since cost/latency profile shifts.
   - **Accept current results** — move to Phase 6 (or Phase 7/8 if already past integration).

   Example shape (adapt `question` to reference the top failure mode observed, and swap options based on what's actually wrong — don't show irrelevant options):

   ```
   AskUserQuestion({
     questions: [{
       question: "Pass rate {P}%, p95 latency {L}ms, cost ${C}/inv. Top failure: {one-line summary of the most common miss}. How do you want to proceed?",
       header: "Eval Decision",
       multiSelect: false,
       options: [
         { label: "Patch the prompt", description: "{specific edit proposal grounded in the failure mode — e.g., 'Add a few-shot example covering ambiguous severity tickets and tighten the escalation rule'}" },
         { label: "Change a tool or schema", description: "{specific structural change — e.g., 'Split search_kb into two narrower tools because the model over-queries'}" },
         { label: "Swap the model", description: "{specific swap with reason — e.g., 'Move from Sonnet to Opus to fix multi-step reasoning on complex cases; cost rises ~3x'}" },
         { label: "Accept and move on", description: "Metrics are good enough for this build; proceed to Phase 6" }
       ]
     }]
   })
   ```
5. **Log the iteration.** Append a row to the Eval Log in the progress file with timestamp, metrics, the change applied, and the user's decision.
6. **Repeat** from step 1 until the user chooses Accept.

### Stop conditions

The user, not the lead, decides when to stop. There is no automated threshold. The lead surfaces signals:

- Target pass rate from `evaluation.md` (if stated).
- Latency budget from `agents.md` or non-functional requirements.
- Cost budget from the user's initial confirmation.
- Rubric scores if LLM-as-judge is used.

If metrics plateau across 2-3 iterations with no meaningful improvement, say so in plain text and recommend one of: accept, switch model, restructure the tool surface, or pause and return to `agent-design` for a scope change.

### Drift handling

Once iteration begins editing prompts in the repo, `agent-design/prompts.md` starts drifting. Policy: **repo is the source of truth for live prompts once iteration starts.** Add a header note to `prompts.md` at the top:

```
> NOTE: Live prompts are now in `src/{path}/{file}`. This file captures the
> design-time spec; post-iteration changes live in the repo.
```

At build-complete time (after Final Verification), offer the user the choice to sync final prompt text back into `prompts.md` so the design doc reflects shipped behavior.

## Step 6: The Agent Reviewer Checklist

The reviewer's full checklist lives at `references/reviewer-checklist.md` (sibling of this SKILL.md). It covers prompt structure, XML formatting, few-shot quality, caching boundaries, tool description clarity, structured-output tool wiring, SDK-level compliance (via the `claude-api` skill), and guardrail implementation, plus MUST-FIX vs. SHOULD-FIX classification.

Include the path to that file in the reviewer's spawn prompt — the reviewer reads it at the start of the review and structures findings against it. Do not paraphrase or inline the checklist into the spawn prompt; send the path and let the reviewer load it fresh. That way, checklist updates over time propagate without touching spawn prompts.

One rule from the checklist worth surfacing in this body because it affects orchestration: the 3-cycle MUST-FIX ceiling applies only to code-level fixes. Prompt-quality findings that affect *observable* agent behavior belong to the Step 5 prompt-iteration cycle, not the fix-loop.

## Step 7: Execute

As the lead, your job during execution is to manage the **spawn-work-shutdown lifecycle** of teammates and keep the pipeline moving. You do not write code, run commands, or tune prompts — you drive task assignments, read teammates' outputs, and decide who runs next.

### Just-in-time spawning

Every teammate is a full Claude Code session burning tokens from the moment it's spawned. An idle teammate waiting on dependencies is wasted money — and because agent-build roles like `agent-loop-dev` and `eval-harness-dev` load heavy context (prompts, tool schemas, SDK reference) on spawn, leaving them idle is more expensive than the equivalent `dev-team` roles. Follow this rule:

**Only spawn a teammate when it has an unblocked task ready to work on. Shut down a teammate as soon as its tasks are complete.**

Bad (what NOT to do):
```
1. Spawn tool-dev, agent-loop-dev, eval-harness-dev, test-author, reviewer all at once
2. Most sit idle waiting on Phase 2 tool tests to be written → burning tokens
3. test-runner kept alive across Phase 2.1.5 and Phase 2.1 regression → stale context, noisy summaries
```

Good (what TO do, for a Phase 2 tool cycle):
```
1. Spawn test-author for Phase 2.N.1 (tool tests — unblocked now)
2. test-author finishes → shut it down → spawn a fresh test-runner for the RED check (2.N.1.5) → read summary → shut it down
3. Spawn reviewer for Phase 2.N.1.75 → reviewer finishes → shut it down
4. Spawn tool-dev for Phase 2.N.2 → implementation done → shut it down
5. Spawn reviewer again for Phase 2.N.3 → finishes → shut it down
6. Spawn a fresh test-runner for between-phase regression → read summary → shut it down
```

When independent tools in Phase 2 are ready in parallel, spawn multiple tool-devs at once (within the 3-active limit) — but still shut each one down the moment its tool is done. Parallelism is not a license to leave teammates hanging.

### Execution checklist

1. **Spawn teammates whose tasks are unblocked now.** Independent tools in Phase 2 may spawn multiple implementers simultaneously. But never spawn a teammate whose work is blocked by an incomplete task — that's what "just-in-time" means.
2. **Watch for task completions.** When a teammate finishes, act immediately — don't let them sit idle waiting for you to notice.
3. **Shut down finished teammates promptly.** Every minute an idle teammate runs is wasted tokens. This is especially true for `agent-loop-dev` and `eval-harness-dev`, which load heavy SDK + spec context on spawn.
4. **Spawn the next wave** of teammates whose tasks just unblocked.
5. **Monitor progress** — check in on teammates, redirect if they're going down a rabbit hole. Watch especially for prompt-iteration rabbit holes in Phase 5 (a teammate trying to "fix" a prompt without user approval is out of scope — the user owns those decisions).
6. **Verify results** when a teammate finishes — read their output files, and for any test / typecheck / build / eval run, spawn a fresh `test-runner` and read its summary. Never run these commands from the lead session directly.
7. **Update progress** after each completed task — including the Eval Log and Prompt Iteration History in Phase 5.
8. **`test-runner` is always fresh and always short-lived.** Spawn one per verification window (RED check, between-phase regression, MUST-FIX re-verify, eval run, Final Verification); shut it down as soon as you've read its summary. Never reuse a `test-runner` across windows — fresh context is the whole point of the role.

Think of it like a pipeline: there should always be work in flight, but never idle workers on the clock.

### Spawn-prompt requirements for every AI-touching teammate

When you spawn tool-dev, agent-loop-dev, eval-harness-dev, integration-dev, integration-tester, or the reviewer, their spawn prompt must include:

- Role and what they own.
- Paths to relevant files in `agent-design/` — `prompts.md`, `tools.md`, `output-formats.md`, `agents.md`, `evaluation.md`, `integration.md`, `data-sources.md` as applicable — with the explicit instruction **"treat these as spec, do not rewrite."**
- Paths to relevant architecture docs.
- Paths to existing code files to study for pattern reference.
- **A bolded instruction to use the `claude-api` skill** when writing Anthropic SDK calls (caching config, tool-use loop, extended thinking, streaming).
- Success criteria — which tests must pass, which schemas must match, which reviewer checklist items must clear.
- Any constraints from `agents.md` (model, runtime shape), `integration.md` (invocation contract, error surface), or the architecture.

For non-AI teammates (test-author, docs, test-runner), follow the spawn-prompt conventions from `dev-team`.

## Progress Tracking

Standalone mode only. Default path: `docs/features/{feature-name}/progress/agent-build-progress.md` (for feature work) or `docs/progress/agent-build-progress.md` (top-level agent).

Copy the file at `assets/progress-template.md` (sibling of this SKILL.md) to the progress path and fill in the feature name and source-doc paths. The template includes the Phase Tracker, Eval Log, Prompt Iteration History, Files Created, and Open Issues sections. Update it after every completed step — the Eval Log and Prompt Iteration History are especially important because they're the durable record of what the user approved during Step 5 iteration.

## Final Verification

After all phases, integration testing, and documentation complete, spawn a fresh `test-runner` in **agent-final** mode. Pass commands for:

- Full unit test suite — `expected outcome: all-pass`.
- Type check — must be clean.
- Full build — must succeed.
- Eval harness run against the full golden-case set — populates the `eval_run` block in the summary.

The summary file gates completion:

- Any unit test failure, type error, or build error → re-spawn the relevant implementer to fix, then spawn another fresh `test-runner` to re-verify.
- Eval pass rate below threshold, p95 latency over budget, cost over budget → return to Step 5 with user approval. Do not force a MUST-FIX fix cycle here.

**Before running Final Verification**, reconfirm the cost budget via `AskUserQuestion` — full eval runs can be expensive, and the user should know what they're authorizing.

When every gate clears AND the user accepts the final eval report:

1. Update `Status: COMPLETE` in the progress file.
2. Offer to sync final prompt text back to `agent-design/prompts.md` (user choice).
3. Shut down any remaining teammates from the lead session, including the final `test-runner`.
4. Report to the user: what was built, final eval metrics, any open SHOULD-FIX items, any issues that hit the 3-cycle limit, paths to documentation.

## Embedded Mode Protocol

When detected as Embedded (see Operating Modes):

**Do not do any of this:**
- Do not create a team.
- Do not create a progress file.
- Do not create any directories.
- Do not write any files.
- Do not spawn a second `test-runner` — the outer `dev-team` lead already has one.

**Do this:** Return a single structured markdown block as plain text in your turn's output — directly to the calling lead, in-conversation. Do not write it to a file, do not create any directories, do not save it anywhere. The calling lead reads the block inline and uses it to shape their spawn prompts.

The block's structure:

```markdown
## Agent-Dev Guidance Pack (Embedded Mode)

### 1. Docs to read
- `agent-design/prompts.md` — system prompts; paste verbatim
- `agent-design/tools.md` — tool schemas; implement exactly as specified
- `agent-design/output-formats.md` — structured output schemas
- `agent-design/agents.md` — model choice, caching strategy, runtime shape
- `agent-design/evaluation.md` — golden cases for the eval harness
- `agent-design/integration.md` — invocation signature, error surface

### 2. Condensed phase pattern
(the Step 4 phases relevant to this AI-implementation phase within the outer build — typically tool implementations → agent loop + prompt wiring → eval harness → prompt iteration)

### 3. Agent-specific roles
(tool-dev, agent-loop-dev, eval-harness-dev definitions from Step 3 — role, responsibilities, files they own — for the outer lead to apply to existing teammates or new hires)

### 4. Prompt iteration protocol
(the Step 5 protocol condensed, including the "repo is source of truth once iteration starts" drift rule and the cost-budget confirmation requirement)

### 5. Reviewer checklist pointer
The full checklist lives at `agent-dev/references/reviewer-checklist.md`. Include that path in the outer reviewer's spawn prompt for AI phases.

### 6. SDK reminder
Use the `claude-api` skill for caching config, tool-use loop shape, extended thinking, streaming, and retry policy.
```

The outer `dev-team` lead keeps the progress file, the teammate lifecycle, the regression runs, and the Final Verification. Eval runs happen through the outer lead's `test-runner` — do not spawn a second.

## Handling Special Scenarios

**Escape-hatch (trivial) agents from `agent-design`.** Single-file or one-shot agents whose `integration.md` contains only a Runtime section. Skip the architecture thin pass assumption. Run a collapsed team:

- **Phase 1** — scaffold + implement tools + wire agent loop (one teammate covers all three).
- **Phase 2** — eval harness + eval iteration.
- **Phase 3** — integration + docs + Final Verification.

Still run the eval harness. Still do Final Verification. Do not skip either just because the agent is simple.

**`agent-design/` missing.** Stop. Route the user to the `agent-design` skill. Do not improvise prompts, tool schemas, output formats, or eval cases. "The app has an AI assistant" is not a spec.

**Architecture thin pass missing and agent is non-trivial.** Stop. Route the user to `solution-architect` with scope limited to language, file structure, test framework, phases — treating `agent-design/` as a fixed constraint. The architect does NOT redesign the agent.

**User wants to edit prompts mid-iteration.** Allowed. Apply their edit via `agent-loop-dev`, record in the Eval Log with "user-driven" as the change-applied note, and re-run eval.

**Model swap during iteration.** Gated through `AskUserQuestion` because cost and latency profiles change significantly. After the swap, re-run the full eval, not just the previously failing cases — and confirm the cost budget still holds.

**Drift between `prompts.md` and committed prompts.** Once Step 5 starts editing prompts in the repo, the repo becomes the source of truth. Add a header note to `prompts.md` per the Drift Handling section in Step 5. Offer to sync at build-complete.

**Sensitive data (PII, PHI, regulated content).** The reviewer checklist gains an explicit leak-attempt eval case — verify one exists in `evaluation.md`; if it doesn't, pause Phase 4 and return to the user (ideally back to `agent-design`). Guardrails listed in `integration.md` must be implemented in orchestration code, not the prompt.

**Embedded mode collision with `dev-team`'s test-runner.** The outer `test-runner` runs the eval harness too. Do not spawn a second from this skill — always route eval runs through the outer lead's verification machinery.

**Eval cost surprise.** Before the first eval run (Step 5) and before Final Verification, confirm the cost budget via `AskUserQuestion`. Surface estimated cost per run × expected iterations. The Eval Log tracks cumulative spend so the user can see it rising.

**Multi-agent systems.** Follow `agent-design/orchestration.md` for the coordination pattern. Phase 3 expands: each agent in the system gets its own agent-loop wiring sub-phase. Integration tests (Phase 7) explicitly verify the handoff protocol between agents. Eval cases that exercise multi-agent flows usually cost more — flag this when confirming the eval budget.

**UI-driving agents.** If `ux-design.md` specifies UI-driving tools (`show_media`, `open_booking_widget`) or UI-intent fields in structured outputs, Phase 2 tool implementations include those UI tools. Frontend consumption of UI intents is typically out of scope for `agent-dev` — if the agent is embedded in a larger app, `dev-team` owns the frontend work. For agent + thin-wrapper builds where the UI is trivial (e.g., a minimal chat page), integration-dev can implement the UI surface directly; flag to the user at Phase 1 if the UI work is significant enough to warrant handing off to `frontend-design` + `dev-team` instead.

**The team doesn't match what the spec calls for.** If `agent-design/` describes an agent too complex for the default team (e.g., a multi-agent research system with 5 sub-agents), scale up the team carefully within the concurrency limits. Consider sequential rather than parallel for sub-agent wiring so the reviewer can keep up. If the scope feels too large for one `agent-dev` session, tell the user and propose splitting the build across multiple sessions by phase boundaries.

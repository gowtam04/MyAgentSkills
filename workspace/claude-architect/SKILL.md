---
name: claude-architect
description: >
  Turn requirements into a technical architecture and a build blueprint that a team of Claude Code
  subagents can execute in parallel without asking questions — stack, data model, components,
  interfaces, budget-fit deployment, a file-ownership map, granular phases traced to requirement
  IDs, pinned test/build/smoke commands, and a machine-readable Build Manifest validated by a
  script. Writes architecture docs only, never application code. Use this skill whenever the user
  has requirements, a PRD, or a clear feature/app idea and says "design the architecture", "how
  should we build this", "technical design", "architect this", "system design", "pick the stack",
  "plan the implementation", or wants to move from requirements toward coding — and suggest it
  when they jump from requirements straight to "build it". Second stage of the Claude pipeline:
  claude-spec → claude-architect → claude-build. Not for games (use game-architecture-blueprint).
---

# Claude Architect

Act as a senior solution architect. Take the requirements (what and why) and decide how to build
it — then document that decision so completely that implementation becomes an execution problem,
not a design problem.

Two facts about the consumer shape everything you write:

1. **The builders can't ask you anything.** `claude-build` hands your docs to subagents that start
   with no context and no way to ask a clarifying question mid-build. Where you're vague, they
   guess — and a guess at a seam between two workers is the most expensive kind, because each side
   guesses differently.
2. **The build runs as wide as your plan allows.** `claude-build` launches every phase whose
   dependencies are done and whose files don't overlap, all at once. A plan where every phase
   touches `app.ts` builds one worker at a time no matter how capable the team. **The shape of
   your blueprint sets the build's speed.**

This is stage 2 of 3. `references/pipeline-contract.md` defines exactly what you receive and what
you must hand over, including the Build Manifest schema.

## Core rules

- **Start from the requirements; don't rewrite them.** If a requirement is contradictory, wrong,
  or infeasible, surface it with AskUserQuestion — it's the user's call, not yours to paper over.
- **Respect what exists.** In an existing codebase, fit its stack, conventions and patterns unless
  the user asks for a migration.
- **Decisions that are expensive to reverse go to the user.** Present them as AskUserQuestion
  choices with the architectural implication of each option. Smaller calls you make yourself,
  with a one-line rationale.
- **Right-size the output.** A small feature gets one `design.md`; a large app gets the multi-file
  set. Depth follows complexity and risk, not a template's length.
- **Documentation only.** No application code, scaffolding, or dependency installs.

## Asking questions

Route every decision the user must make through **AskUserQuestion**: 1–4 questions per call, 2–4
options each, descriptions that state the tradeoff ("WebSockets — instant, but adds a stateful
server to operate"), a justified recommendation first marked "(Recommended)", `header` ≤ 12
characters, `multiSelect` when several apply. Explain your recommendation in plain text right
before the card. A question left in plain text stalls the conversation — every turn ends with a
card or with writing docs.

**Round budget:** about 3–5 rounds in PM mode, 5–8 in Developer mode. Batch related decisions.
The budget exists to prevent an endless interview, not to suppress a real decision.

## Before designing

1. **Read the requirements** — the user's path, else `docs/features/{name}/requirements/` or
   `docs/requirements/`. Read everything: stories and criteria, rules, non-functional needs,
   constraints, assumptions, Open Questions (flag the ones that block design), Out of Scope.
2. **Check the IDs.** You'll cite `US-`/`AC-`/`BR-` IDs on every phase. If the requirements lack
   them, offer a quick polish pass with `claude-spec`, or mint provisional IDs with the user's OK —
   never invent acceptance criteria.
3. **Scan the codebase** if there is one: stack, structure, data access, API style, auth, frontend
   patterns, test framework, build/test commands. Timebox it; on a large repo delegate the sweep to
   an Explore subagent and keep its summary. Go deep only where the new work lands.
4. **Design system:** if `docs/design-system/design-system.md` (or a path the requirements name)
   exists, UI phases will reference it. Don't invent a visual system here.
5. **AI/LLM features** in the requirements: read `references/agent-features.md` and design them as
   ordinary components with interfaces, phases and an eval plan.
6. **No requirements at all?** For anything beyond a small feature, suggest `claude-spec` first.
   Otherwise gather the essentials in 1–2 rounds and design from what you have.

**Skip path:** if the work is small enough that `claude-build`'s light mode could plan it in a few
lines (one bounded change, no new persistence, no shared interfaces), say so and don't force a
blueprint.

## The design conversation

### 1. Confirm understanding, mode, and budget

Summarize the requirements briefly in plain text. Then make the **first** card batch these two
foundational questions (plus any early blocking ambiguity):

- **Mode** — *PM mode (default)*: rapid build or an agent team; you infer sensible code-level
  defaults. *Developer mode*: a human team wants a say in code-level practice; every choice you'd
  otherwise infer becomes a question, and two extra sections are produced. See
  `references/developer-mode.md`.
- **Budget tier** — Hobby / prototype ($0–50/mo), Startup / lean ($50–500), Scaling / growth,
  Enterprise / no constraint. The tier is a hard constraint on every infrastructure choice.

**Tiny-feature shortcut:** for a clearly small change on an existing stack, one card batching
mode + budget + the single real ambiguity is enough; then write `design.md`.

Record both as the first lines of the output: `Mode: PM | Developer` and `Budget Tier: …`.

### 2. Resolve what changes the architecture

Ask only where the answer changes the design: realtime vs polling, payment provider, permission
model, expected scale, offline support, data retention, compliance, integration ownership. Details
the builders can decide don't need a card. If requirements conflict with each other or with a
constraint, stop and ask how to resolve it.

### 3. Stack

Existing codebase → keep it; ask only about genuine additions. Greenfield → recommend a stack in
plain text with the reason, then confirm with a card of options you'd genuinely recommend. Prefer
stacks agents can verify from a terminal: typed languages catch seam mismatches early, and a
test runner plus a scriptable smoke check (Playwright, curl, a CLI run) let the build prove its
work without a human. In PM mode leave ordinary library picks to the builders; Developer mode
surfaces the ones that shape the code.

### 4. Scope call and topology

State in plain text whether this is **small/focused** (→ `assets/design-template.md`) or
**large/multi-phase** (→ `assets/large-app-docs/`). Lean small when in doubt — adding docs later is
cheap. For large work, ask about backend topology (monolith / modular monolith / microservices /
serverless) with honest tradeoffs for *this* project and team size, and record
`Backend Topology:` in the overview.

### 5. System design

Cover what applies:

- **Data model** — entities, fields and types, relationships, constraints, indexes for real query
  patterns, migration/backfill for existing data. Every entity traces to a requirement.
- **Components** — for each: what it owns, what it exposes, what it depends on, where it lives.
  If you can't say what a component does in one sentence, split it.
- **API design** — routes, request/response shapes, auth, error format, pagination.
- **Integrations** — interface, failure handling, data flow for each external system.
- **Cross-cutting patterns** — error handling, logging, transactions, state management,
  observability. PM mode infers them; Developer mode asks (see `references/developer-mode.md`).
- **Deployment and infrastructure** — every choice right-sized to the budget tier, ending with a
  rough monthly cost bucket. Pin the runnable commands here, including `smoke`. Read
  `references/deployment.md` for the checklist, the tier ladders, and what a good smoke command
  looks like.
- **Key decisions** — the expensive-to-reverse ones get a card before you commit (1–2 cards, not a
  card per choice), then an ADR entry: decision, alternatives, why, tradeoffs accepted.
- **Defaults you chose for the user** — every gap you filled without asking (a limit the
  requirements didn't state, a rule you inferred, a recommended option taken on their behalf) goes
  in a Defaults table in `decisions.md` with its **change cost**: cheap (config or copy), moderate
  (touches a few components), or expensive (reshapes the data model or a workflow). Sort it
  expensive-first so the user reviews the risky guesses before the build starts.

### 6. The build blueprint

This is what `claude-build` executes. It must answer every structural question a builder could
have.

- **File structure = ownership map.** Every file to create or modify, with a one-line purpose,
  grouped by component; note new vs modified in an existing repo. List test files next to the code
  they cover — the build gives tests to a different worker than code, so tests need their own
  owned paths. No two phases should need to edit the same file.
- **Interfaces at every seam.** Where one worker's output meets another's input, specify full
  signatures, input/output types with field-level detail, error types, and behavior notes.
  Conventional internals (standard CRUD, simple mappers) can stay light. The test is not "would a
  senior dev get this right?" but "would two agents who can't talk to each other both get this
  right?" — at seams, the answer is usually no unless you write it down.
- **Phases.** Granular and build-ordered; prefer more, smaller phases, each touching one layer or
  domain. For each: what gets built (files), kind, depends on, produces, test focus, and
  requirement refs (the IDs it satisfies). Mark `risk: high` on auth, permissions, payments, money
  math, migrations, security boundaries and concurrency — the build reviews those harder. When a
  phase calls a function another phase implements, either make it depend on that phase or say its
  tests fake the callee against the contract — an unstated cross-phase call leaves a builder
  blocked or testing against nothing. In Developer mode, add success criteria and a review/test
  split per phase.
- **Verification design.** For `logic` and `ui` phases, the test focus names what the spec-first
  tests must prove, citing AC IDs. Name the integration checkpoints — the seams where independently
  built pieces first meet (backend stack complete, UI wired to API, final end-to-end) — and what
  each must prove with the smoke command or an integration test.

### 7. Design for a wide build

Read `references/wide-build.md` before you finalize phases. The short version:

1. **Contracts first.** Shared types, interfaces, API types and event names go in an early,
   small `contracts` phase, so every later phase can build and test against them in parallel.
2. **One slice per domain or module.** Give each independent module its own phase (`p4a`, `p4b`,
   …) with its own source files, its own test files, and its own requirement refs.
3. **No hub files.** Entry points, routers, DI containers and registries are where plans
   serialize. Modules expose a `register(app)`-style function in their own file; a single
   `wiring` phase owns the hub and calls them. A file shared by three or more phases means
   restructure.
4. **Tests are their own files**, owned per phase, so all test-writers can run at once.
5. **Few, meaningful integration checkpoints** — they're barriers.

Add a **Parallel Waves** table to the implementation plan (wave → phases that can run together)
and name the critical path. Don't manufacture independence that isn't real: modules that share
mutable state or a file are one slice.

### 8. The Build Manifest

For any multi-phase build, write the Build Manifest (schema and field rules in
`references/pipeline-contract.md`) **last**, as a projection of the finished prose. Then validate
it:

```bash
python3 <this skill's dir>/scripts/check_manifest.py <implementation-plan.md or design.md> --requirements <requirements dir> --root <project root>
```

No dependencies needed. It checks ownership (no path owned twice, test files separate, shared files
created upstream), the dependency graph (no cycles, no unknown ids), requirement IDs (every cited
ID exists; every ID is covered or deferred), and commands. It also prints the parallel waves and
critical path — if the widest wave is much narrower than the number of independent modules, look
for a hub file or an unnecessary dependency edge. Fix errors in the prose first, then the
manifest, and re-run until 0 errors.

## Completeness gate

Don't present the docs until all of these hold:

- [ ] `Mode`, `Budget Tier` (and `Backend Topology` for large work) are recorded
- [ ] Architecture-changing questions are resolved, or explicitly deferred with the user's OK
- [ ] Every entity traces to a requirement; every requirement ID is covered by a phase or listed
      as deferred
- [ ] Every file to create or modify has a purpose and exactly one owning phase; test files are
      listed separately
- [ ] Every seam between phases has an interface specified at no-questions-asked depth
- [ ] Every phase has kind, depends on, produces, test focus and requirement refs
- [ ] Every call from one phase's code into another phase's function is covered by a dependency
      or by a stated fake-the-contract test plan
- [ ] Every default chosen on the user's behalf is in the Defaults table with its change cost
- [ ] Integration checkpoints are named with what each proves
- [ ] `test`, `test_one`, `typecheck`, `build` and `smoke` are pinned (TBD only if a scaffold phase
      sets them)
- [ ] Deployment fits the budget tier and has a monthly cost bucket
- [ ] No hub file is shared by three or more phases; the Parallel Waves table names the critical
      path
- [ ] `references/ownership-checklist.md` passes
- [ ] The Build Manifest matches the prose and `check_manifest.py` reports 0 errors

## Output

- New application: `docs/architecture/`
- Feature in an existing project: `docs/features/{feature-name}/architecture/`

**Small feature** → copy `assets/design-template.md` to `design.md`, fill it, delete sections
that don't apply (and the Developer-only sections in PM mode).

**Large application** → copy `assets/large-app-docs/` into the output directory, fill the relevant
files, delete the ones that don't apply (`conventions.md` and `testing-strategy.md` in PM mode).
The Parallel Waves table and the Build Manifest live in `implementation-plan.md`.

Write concretely. Not "the service layer handles business logic" but "`invoice.service.ts` exposes
`finalize(invoiceId): Promise<Invoice>`, enforces BR-4 (sent invoices are read-only) and is called
only by the invoice routes."

## After writing

1. List the files as clickable links and walk through the key decisions and why.
2. Ask for approval with a card: Looks good / Some changes / Rethink the approach. Include any
   still-open requirement questions in the same call.
3. On changes, ask which area (data model, API, phasing, stack, a specific decision), revise in
   place, re-run the validator, re-present. Loop until approved.
4. On approval: "Architecture complete. Next is the build — run `/claude-build`." In Developer
   mode, mention the conventions and testing-strategy docs the build will feed to its workers.

## Special scenarios

- **Existing codebase:** design how the new work fits in. Document modifications to existing
  files precisely (what changes and why) and give each modified file one owning phase.
- **Strong technical opinions from the user:** incorporate them; raise real problems once with the
  tradeoff, and if they insist, design around their choice and record it in the ADRs.
- **Developer mode without developers in the room:** still recommend a concrete answer for every
  code-level choice, mark each `Proposed — confirm with dev team`, and list them under Unresolved.
- **Mid-conversation switch PM → Developer:** see `references/developer-mode.md`.
- **Very small features:** a short `design.md` with components, file list, interfaces and the
  phase is enough; inline the manifest fields into the phase prose.

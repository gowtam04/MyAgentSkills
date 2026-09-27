# Pipeline Contract

The shared agreement between `claude-spec` → `claude-architect` → `claude-build`. The same file
ships in all three skills — keep the copies identical, so every stage agrees on what the others
produce and expect.

## Stage boundaries

| Stage | Skill | Owns | Does not own |
|---|---|---|---|
| Spec | `claude-spec` | WHAT and WHY: personas, workflows, business rules, testable acceptance criteria with stable IDs, constraints, out-of-scope, assumptions | Frameworks, schemas, APIs, infrastructure, code |
| Architecture | `claude-architect` | HOW: stack, data model, components, interfaces, deployment, file ownership, phases with `requirement_refs`, pinned commands, Build Manifest | Inventing product behavior; application code |
| Build | `claude-build` | Implementation by a team of Claude Code subagents: spec-first tests, code, review, integration, docs | Redesigning the product or the architecture |

Each stage stops at its boundary. When a later stage finds a gap that belongs to an earlier one
(a missing business rule, an interface nobody defined), it goes back to the user rather than
filling the gap itself — a silent guess made downstream is invisible to everyone upstream.

## Doc paths (relative to the project root)

| Kind | Requirements | Architecture | Build progress |
|---|---|---|---|
| New application | `docs/requirements/` | `docs/architecture/` | `docs/progress/build-progress.md` |
| Feature in an existing project | `docs/features/{name}/requirements/` | `docs/features/{name}/architecture/` | `docs/features/{name}/progress/build-progress.md` |
| Ad-hoc task (`claude-build` light mode) | — | — | `docs/plans/{slug}.md` (only when worth keeping) |

A user-named location always wins; keep the same internal file names inside it. The design system,
when one exists, lives at `docs/design-system/design-system.md` (or wherever the architecture says).

## Requirement IDs

- User stories `US-1`, acceptance criteria `AC-1.1` (nested under their story), business rules `BR-1`.
- Large specs may namespace per domain: `AUTH-US-1`, `AUTH-AC-1.2`, `BILLING-BR-3`.
- IDs are stable: append new ones, never renumber. Downstream stages cite them, so renumbering
  silently breaks every reference.
- Acceptance criteria are objectively testable — Given/When/Then, or a concrete checkable
  assertion with real values. The build's test-writer turns them into tests without asking anyone.

## What the spec leaves for architecture

- Specific capabilities and business rules — verbs and objects, not feature names.
- Personas, roles and permission boundaries.
- Primary workflows step by step, including failure, empty, conflict and permission-denied states.
- Stable IDs on every story, criterion and rule.
- Non-functional expectations in user terms (speed, reliability, scale, accessibility, compliance).
- Constraints and preferences (timeline, budget, tech preferences as *constraints*, existing systems).
- Out of Scope — a hard boundary; builders will not cross it or invent around it.
- Open Questions (real unknowns only) and Assumptions (only ones the user confirmed on the speed path).

## What architecture leaves for build

- Header lines: `Mode: PM | Developer`, `Budget Tier: hobby | startup | scaling | enterprise`,
  and for large work `Backend Topology: ...`.
- A complete File Structure: every file to create or modify, with its purpose — this is the
  ownership map. Test files are listed too.
- Interfaces at every seam where two workers meet, at the depth an agent that can't ask back needs.
- Granular phases, each with: what gets built, depends on, produces, test focus, `requirement_refs`.
- Integration checkpoints, each naming what an end-to-end check there must prove.
- Pinned commands, including an agent-checkable `smoke` command (see below).
- A Parallel Waves table naming the critical path.
- The Build Manifest (below) for any multi-phase build, passing `check_manifest.py` with 0 errors.
- The requirements path(s) it was designed from.

## What build honors

- The manifest (when present and consistent with the prose) is the plan: phase DAG, ownership,
  commands. On a prose↔manifest conflict the prose wins; the conflict is noted and, if it blocks
  assignment, taken to the user.
- `requirement_refs` go into every test-writer, implementer and reviewer brief.
- No invented product behavior and no redesign. Gaps stop the affected phase and go to the user.
- Disjoint ownership: no two concurrent workers edit the same file; `shared` files have one writer
  at a time.
- Spec-first verification: a phase's tests are written from the spec by a worker that never sees
  the implementation, and the implementer can't edit them. Tests carry the AC/BR IDs they prove,
  and `check_traceability.py` confirms every cited ID is covered by a test before the build is
  called done.
- MUST-FIX and SHOULD-FIX review findings both block a phase.

## Build Manifest

A machine-readable projection of the architecture's File Structure and phases, written **last**,
after the prose is final. The prose stays the source of truth: if a field can't be filled without
inventing something the prose doesn't say, the prose is incomplete — fix the prose first.

It lives in a fenced ```` ```yaml ```` block under a `## Build Manifest` heading in
`implementation-plan.md` (large apps) or `design.md` (small features). A trivial single-phase
feature may skip the block and state `owns` / `tests` / `requirement_refs` in the phase prose.

Write it in a simple YAML subset — block mappings, block lists or `[a, b]` flow lists, plain or
quoted scalars, `#` comments. No anchors, tags, or multi-line strings. That keeps
`check_manifest.py` working even where PyYAML isn't installed.

```yaml
commands:
  install: "npm ci"                      # optional
  test: "npm test"                       # full suite
  test_one: "npx vitest run {files}"     # {files} = space-separated test paths
  typecheck: "npx tsc --noEmit"          # or "none" for untyped stacks
  lint: "npm run lint"                   # optional
  build: "npm run build"
  smoke: "node smoke/run.mjs"            # agent-checkable proof the app actually runs
  run: "npm run dev"                     # optional: how to start it by hand
  eval: "npm run eval"                   # optional: golden-case eval harness for AI features
phases:
  - id: p1
    name: Scaffold                       # MUST match the prose phase name
    kind: scaffold
    depends_on: []
    owns: ["package.json", "tsconfig.json", "smoke/run.mjs", "smoke/checks/app-starts.mjs"]
    tests: []
    requirement_refs: []
    test_focus: "build and smoke pass on an empty app"
  - id: p3a
    name: Invoice rules
    kind: logic
    depends_on: [p2]
    owns: ["src/invoices/rules.ts"]
    tests: ["src/invoices/rules.test.ts"]
    shared: []
    requirement_refs: [US-3, AC-3.1, AC-3.2, BR-4]
    test_focus: "totals, tax rounding, overdue transitions"
    risk: high                           # optional: normal (default) | high
    flags: []                            # optional: ai
integration_checkpoints:
  - name: backend-e2e
    after: [p5]
    verifies: "create → pay → receipt works end-to-end against a real DB (US-3, US-5)"
deferred_refs: [US-9]                    # optional: IDs deliberately not built in this plan
```

**Phase `kind`** decides how the build verifies the phase:

| kind | What it is | How build verifies it |
|---|---|---|
| `scaffold` | Project skeleton, config, tooling, CI, the smoke script | build + smoke; review |
| `contracts` | Shared types, interfaces, schemas, event names | typecheck; review |
| `logic` | Domain rules, services, data access, API handlers, jobs | spec-first tests → implement → review |
| `ui` | Screens and components | spec-first behavior tests → implement → review; screenshot smoke |
| `wiring` | The one phase that owns a hub (entry point, router, registry) and plugs modules in | build + smoke; review |
| `data` | Migrations and seed data | migrate on an empty DB (and rollback if supported); review |
| `infra` | Deployment config, containers, IaC | build/validate; review |
| `docs` | Documentation only | review against the code |

**Field rules**

- `id` unique; `depends_on` references existing ids; no cycles.
- `owns` (production files) and `tests` (test files) are globs that trace to the File Structure.
  No path appears in two phases, and no path is in both `owns` and `tests`. Test files are owned
  separately because the build gives them to a different worker than the code.
- `logic` and `ui` phases have at least one `tests` entry.
- A file touched by more than one phase goes in `shared` for every phase except the one that
  creates it (which lists it in `owns`). That creator must be an upstream dependency of every
  sharer. A file shared by three or more phases is a hub — restructure around a `wiring` phase.
- `requirement_refs` cite IDs that exist in the requirements. If the requirements lack IDs, the
  architect flags the gap instead of inventing refs. Every requirement ID is either cited by some
  phase or listed in `deferred_refs`.
- **Cross-phase calls.** If a phase's code calls a function another phase implements (routes
  calling an auth phase's `authenticate()`), either list that phase in `depends_on`, or state in the
  phase notes that its tests fake the callee against its contract and that it's wired up for real
  at a later phase or checkpoint. Otherwise the caller's tests can't run, or quietly test against
  nothing. The validator can't see calls in code, so the architect checks this by hand.
- `risk: high` marks phases where a subtle mistake is expensive: auth, permissions, payments,
  money math, data migrations, security boundaries, concurrency. The build reviews these with a
  panel and reviews their tests before implementation.
- `commands.test`, `build` and `smoke` are required. `"TBD — set in scaffold"` is allowed only
  when a `scaffold` phase exists to set them.

**The `smoke` command** proves the app actually runs, not just that unit tests pass. It starts
the thing, exercises it for real, and exits non-zero on failure: a Playwright script that loads
key pages and saves screenshots to `tmp/smoke/` for a web UI, a start-server-then-curl script for
an API, a real invocation against a fixture for a CLI. Agents lean on it at integration
checkpoints, because unit tests can all pass while the assembled app doesn't start. The runner
discovers check files from a folder, so each phase adds its own check instead of editing a
shared script.

## Skip paths

- **Spec optional** when the user already has architecture-ready requirements (testable criteria,
  clear rules). `claude-spec` can polish them (add IDs) instead of re-interviewing.
- **Architecture optional** for work small enough that `claude-build` light mode can plan it in
  a few lines: a bug, a refactor, a feature that touches a handful of files with no new
  persistence or shared interfaces. Anything bigger gets a blueprint first.
- **Games** use the game pipeline instead (`game-design-document` → `game-architecture-blueprint`
  → `game-dev-orchestrator`); this pipeline has no notion of feel, content volume or playtests.
- **Pure thinking** with no deliverable belongs to `brainstorm`, not `claude-spec`.

## Handoffs

- After the spec: "Next is technical design — run `/claude-architect`."
- After the architecture: "Next is the build — run `/claude-build`."

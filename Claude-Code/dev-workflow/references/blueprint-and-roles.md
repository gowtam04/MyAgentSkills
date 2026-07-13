# Blueprint inputs, agent roles, and progress tracking

Read this during **Step 1 (read the blueprint)** and **Step 2 (pre-flight)**. It covers where each
design doc lives, what role each agent plays in the workflow, and the progress-file template.

## Contents
- [Where to find the design docs](#where-to-find-the-design-docs)
- [Auto-detect: design systems](#auto-detect-design-systems)
- [The agent roles a workflow plays](#the-agent-roles-a-workflow-plays)
- [Progress-file template](#progress-file-template)

## Where to find the design docs

Read in this order. If the user points you at a specific directory, use that instead of the defaults.

### Architecture docs (primary — your source of truth)
Default: `/docs/features/{feature-name}/architecture/` (feature work) or `/docs/architecture/` (new
app). Expect:
- **Component design** — components, responsibilities, interfaces.
- **File structure** — every file to create, with its purpose. This is the **ownership map**: you
  partition these files across implementer agents so no two agents edit the same file.
- **Interface definitions** — contracts between components. These go to the test-writing agents.
- **Implementation phases** — ordered phases with dependencies and parallel opportunities already
  identified. This is your wave plan (Step 3).
- **Build manifest** *(if present)* — a machine-readable YAML appendix (typically a `## Build
  Manifest` section in `implementation-plan.md` or the design doc) giving, per phase: `id`, `name`,
  `depends_on`, `owns`/`shared` file globs, `requirement_refs`, `test_focus`, optional `flags`; plus
  a `commands` block (`test`/`test_one`/`typecheck`/`build`) and `integration_checkpoints`. **When
  present, consume it directly** — it maps almost 1:1 onto the workflow's `args` (see "Mapping the
  build manifest to `args`" below) and removes most of the inference Step 2/3 would otherwise do.
  **When absent, fall back to inference** — derive waves from the prose "Depends on", `implFiles`
  from the File Structure, and commands from your reconnaissance, exactly as you would otherwise. The
  manifest is an accelerator, not a requirement; its absence is not a blocker.
- **Data model**, **API design**, **technical decisions** — agents must not contradict these.

If architecture docs are **missing**, stop and recommend `solution-architect`. If **incomplete**
(no file structure / interfaces / phasing), flag exactly what's missing and ask the user how to
proceed. A workflow can't recover from a bad plan mid-run, so the plan must be complete before
launch. A **missing build manifest is not "incomplete"** — fall back to inferring waves, ownership,
and commands from the prose and File Structure; only missing File Structure, interfaces, or phasing
counts as incomplete.

### Mapping the build manifest to `args` (when present)
The manifest maps almost directly onto the workflow's `args` (see `workflow-authoring.md`):

| Manifest field | Workflow `args` |
|---|---|
| `commands.{test,test_one,typecheck,build}` | `args.commands` |
| `phases[].depends_on` | wave ordering — phases whose deps are all satisfied go in the same wave (`args.waves`) |
| `phases[].owns` | the phase's `implFiles` (ownership partition) |
| `phases[].shared` | collision points — serialize into different waves or use `isolation: 'worktree'` |
| `phases[].requirement_refs` | feed the phase's requirement context; pass the IDs to the test-author (assert against) and reviewers (spec/acceptance-criteria lens) |
| `phases[].test_focus` | seed the test-author prompt's coverage targets |
| `phases[].flags` | the phase's `ui` / `ai` booleans and `needsScaffold` |
| `integration_checkpoints[]` | `args.integration` seam entries |

Cross-check the manifest against the File Structure and prose phases before trusting it. If they
disagree, the prose and File Structure win (the manifest is a derived appendix) — flag the mismatch
to the user before launch, the same as any incomplete-plan case.

### Requirements docs (secondary — the "why")
Default: `/docs/features/{feature-name}/requirements/` or `/docs/requirements/`. The architecture's
"Requirements Reference" usually points here. Use for acceptance criteria and business rules — these
go to test-writing agents (to assert against) and reviewers (to check the build serves the need).
If the requirements use stable IDs (US-/AC-/BR-) and the architecture's `requirement_refs` cite
them, pass the specific IDs a phase satisfies to that phase's test-author (to assert against) and
its reviewers (the spec/acceptance-criteria lens) — this sharpens the "does it satisfy the spec?"
gate from "read all the requirements" to "verify these exact criteria."

## Auto-detect: design systems

### Design system (for UI work)
Look for `/docs/design-system/design-system.md` (or wherever the architecture points). If present,
record its path and pass it to every UI agent so the visual language stays consistent. If absent,
that's fine — proceed; UI agents still use the `frontend-design` skill for quality. Don't block on
its absence and don't fabricate one.

## The agent roles a workflow plays

In a workflow these aren't long-lived workers — they're `agent()` calls, each a fresh subagent
whose entire context is the prompt you give it. The responsibilities below are encoded as
functions/stages in the script.

**Always present:**
- **test-author** — writes unit/component tests for a phase. Prompt contains requirement docs,
  architecture interface definitions + data model, and test-pattern reference paths. **Never
  implementation paths** (information isolation). Returns the list of test files it created.
- **reviewers (adversarial panel)** — several independent reviewers per gate, each given a distinct
  lens (architecture-compliance, spec/acceptance-criteria, edge-cases & error-handling, security).
  Reviewers never write code. A finding blocks only if it survives a refutation vote (see
  `workflow-authoring.md`).
- **test-runner** — runs an existing test suite / typecheck / build and returns a structured
  pass/fail summary (no diagnosis, no fixing, no retries). Cheap model (`model: 'haiku'`). Used for
  the RED check, between-wave regression, and final verification. Keep its prompt minimal — the
  point is to keep noisy output out of the reasoning agents.

**Implementation roles (vary by project — name them from the architecture's components):**
backend-dev, frontend-dev, mobile-dev, data-layer-dev, devops, ai-dev, etc. Each owns a
non-overlapping slice of the file structure. Any UI role is told to use the **`frontend-design`**
skill (and the design-system doc if found).

**Specialized (when applicable):**
- **integration-tester** — writes tests across component seams. **Unlike test-author, it sees
  implementation code** — it needs to know what's actually built. Spawned at natural integration
  boundaries (after the backend stack connects, after frontend meets the API, at the end), not every
  phase.
- **docs** — writes README/API docs/developer guides reflecting what was actually built. Never
  modifies implementation code. Cheap model. Spawned near the end.

All agents inherit the user's session model unless you route them down. Mechanical/execution stages
(test-runner, scaffolding, docs) → `model: 'haiku'`. Reasoning stages (authoring, implementing,
reviewing) → omit `model` to inherit the session model.

## Progress-file template

You (in conversation) write this — before launch (initial) and after the run returns (final). The
workflow script can't touch the filesystem. Default location:
`docs/features/{feature-name}/progress/build-progress.md` or `docs/progress/build-progress.md`.

```markdown
# [Feature/Project Name] — Build Progress (dynamic workflow)

## Status: IN PROGRESS | COMPLETE | FAILED

## Scope of this run
(whole build, or the named phase)

## References
- Architecture: /docs/.../architecture/...
- Requirements: /docs/.../requirements/...
- design-system: (path if present)
- Workflow script: (the scriptPath the Workflow tool returned, for rerun/resume)

## Wave / Phase Tracker
| Wave | Phase | Tests | RED ok | Impl | Review (surviving MUST-FIX) | Regression | Status |
|------|-------|-------|--------|------|------------------------------|------------|--------|
| 1    | ...   | ⬜     | ⬜      | ⬜    |                              | ⬜          | ⬜      |

## Integration Tests
## Documentation
## Final Verification (tests / typecheck / build)
## Files Created (by phase)
## Surviving findings & open issues
(MUST-FIX that hit the cycle limit; anything the workflow flagged it couldn't resolve autonomously)
```

Status glyphs: ⬜ not started · 🔄 in progress · ✅ done · ❌ blocked/failed.

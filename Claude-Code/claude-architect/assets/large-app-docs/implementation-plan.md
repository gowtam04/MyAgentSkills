# Implementation Plan

Granular, build-ordered phases. Prefer more, smaller phases — one layer or one domain each — and
design for a wide build: contracts first, one slice per module, no hub files shared across phases,
tests in their own files (see the architect skill's `references/wide-build.md`).

## Phase {id}: {Name}
- **Kind:** scaffold | contracts | logic | ui | wiring | data | infra | docs
- **What gets built:** specific files/components (production files)
- **Tests:** the test files this phase owns (`logic` and `ui` phases)
- **Depends on:** phase ids that must be complete first
- **Produces:** interfaces/files available to later phases
- **Test focus:** what the spec-first tests must prove, citing AC IDs
- **Requirement refs:** US-/AC-/BR- IDs this phase satisfies
- **Risk:** normal | high (auth, permissions, payments, money math, migrations, security, concurrency)
- **Success criteria** *(Developer mode)*: concrete reviewable outcomes beyond "tests pass"
- **Review checklist / test split** *(Developer mode)*: unit vs integration, mocked vs real, review gates

(Repeat per phase.)

## Integration Checkpoints
The seams where independently built phases first meet — typically backend stack assembled, UI
wired to the API, and final end-to-end. For each: which phases must be done, and what the check
proves (smoke paths, integration tests, requirement IDs covered).

| Checkpoint | After | Proves |
|---|---|---|
| backend-e2e | p4a, p4b, p4c | create → pay → receipt against a real DB (US-3, US-5) |

## Parallel Waves
| Wave | Phases (run together) | Barrier after |
|---|---|---|
| 1 | | |

**Critical path:** p1 → …

## Build Manifest
Generated last, from the prose above and the File Structure in `component-design.md`. The prose is
the source of truth; if a field can't be filled without inventing something, fix the prose first.
Schema and field rules: `references/pipeline-contract.md`. Validate with `scripts/check_manifest.py`
until it reports 0 errors.

```yaml
commands:
  test: "..."
  test_one: "... {files}"
  typecheck: "..."
  build: "..."
  smoke: "..."
phases:
  - id: p1
    name: Scaffold
    kind: scaffold
    depends_on: []
    owns: []
    tests: []
    requirement_refs: []
    test_focus: "..."
integration_checkpoints:
  - name: ...
    after: []
    verifies: "..."
deferred_refs: []
```

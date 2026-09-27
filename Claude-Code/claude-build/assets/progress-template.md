# {Project / Feature} — Build Progress

Status: IN PROGRESS | BLOCKED | COMPLETE

## References
- Architecture: `{path}`
- Requirements: `{path}`
- Build Manifest: present | absent (inferred — see Deviations) — `check_manifest.py`: {0 errors / notes}
- Design system: `{path}` | none
- Mode: PM | Developer   Budget tier: {tier}
- Engine: subagents | workflow (script path: `{path}`)
- Model routing: judgment-heavy phases (Opus implementer + panel + lead diff read): {ids} · all others: Sonnet implementer

## Environment
- Commands: install `…` · test `…` · test_one `…` · typecheck `…` · build `…` · smoke `…` · eval `…`
- Baseline (before the build): {passed/failed; pre-existing failures listed here}
- Permissions: {allow rules added | auto mode | prompts expected}

## Resume Snapshot
- Branch: `build/{slug}`   Build start commit: `{sha}`
- Verified phases (id → commit):
- In flight (id → step → named agents → worktree/branch):
- Deferred spawns (hit the subagent limit or a rate limit; launch when a slot frees):
- Unmerged worktree branches:
- Open findings (MUST-FIX and SHOULD-FIX, both block):
- Blockers waiting on the user:

## Phase Tracker
| Phase | Kind | Risk | Refs | Tests | Test lock | Impl | Review | Regression | Commit | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| p1 Scaffold | scaffold | normal | — | — | — | ⬜ | ⬜ | ⬜ | | ⬜ |
| p3a {name} | logic | high | US-3, BR-4 | ⬜ | `{sha}` | ⬜ | ⬜ | ⬜ | | ⬜ |

⬜ not started · 🔄 in progress · ✅ done · ❌ blocked/failed

## Phase Log
### {id} {name}
- Agents (name → role → model):
- Tests written / unexpected passes:
- Test disputes and rulings:
- Review findings (verified / dropped with reason) and fix rounds:
- Regression result:
- Files changed:

## Integration Checkpoints
| Checkpoint | After | Proves | Result | Evidence |
|---|---|---|---|---|

## Deviations from the blueprint
(Manifest corrections, inferred ownership, anything done differently from the architecture — and why.)

## Lead-local fixes
(Tiny-glue edits made by the lead: file, change, why a worker wasn't worth it.)

## Final Verification
- test / typecheck / build / smoke (/ eval): {results vs baseline}
- Traceability (`check_traceability.py`): {n}/{n} cited IDs proven by a test · untested: {IDs}
- Requirement coverage: {IDs covered} · deferred: {IDs}
- Open items:
- Agents by role and model; escalations:
- First-pass rate by role and tier (first attempt passed its gate):

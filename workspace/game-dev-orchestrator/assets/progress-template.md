# {Game / Feature} — Game Build Progress

Status: IN PROGRESS | BLOCKED | COMPLETE

## References
- Architecture: `{path}`
- GDD: `{path}`
- Game Build Manifest: present | absent (inferred — see Deviations) — `check_manifest.py`: {0 errors / notes}
- Asset Manifest: present | absent | greybox-only
- Mode: PM | Developer   Scale: jam | vertical-slice | shippable-indie
- Engine: {engine / runtime}
- Build engine: subagents | workflow (script path: `{path}`)
- Model routing: judgment-heavy phases (Opus implementer + panel + lead diff read): {ids} · all others: Sonnet implementer · style lock: Opus artist · asset families: Sonnet artists

## Environment
- Commands: install `…` · run `…` · test `…` · test_one `…` · typecheck `…` · build/export `…` · smoke `…` · screenshot `…`
- Baseline (before the build): {passed/failed; pre-existing failures listed here}
- Permissions: {allow rules added | auto mode | prompts expected}
- Asset tooling: Pillow {yes/no} · SVG rasterizer {tool/no} · image-gen tool {name/none → fallback: …}
- Playtest evidence dir: `tmp/playtest/`

## Resume Snapshot
- Branch: `build/{slug}`   Build start commit: `{sha}`
- Style lock: `{palette / rules / reference sheet paths}` | greybox-only — commit `{sha}`
- Verified phases (id → commit):
- In flight (id → step → named agents → worktree/branch):
- Deferred spawns (hit the subagent limit or a rate limit; launch when a slot frees):
- Unmerged worktree branches:
- Open findings (MUST-FIX and SHOULD-FIX, both block):
- Open asset defects:
- Blockers waiting on the user:

## Phase Tracker
| Phase | Kind | Risk | gdd_refs | Tests | Test lock | Impl / Assets / Content | Review | Regression | Playtest | Commit | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| p1 Scaffold | scaffold | normal | — | — | — | ⬜ | ⬜ | ⬜ | — | | ⬜ |
| p3 Style lock | assets | normal | 06-art-audio-juice#art-direction | — | — | ⬜ | ⬜ | — | — | | ⬜ |
| p4a {name} | gameplay | high | 03-systems#drop | ⬜ | `{sha}` | ⬜ | ⬜ | ⬜ | ⬜ | | ⬜ |

⬜ not started · 🔄 in progress · ✅ done · ❌ blocked/failed · — not applicable

## Phase Log
### {id} {name}
- Agents (name → role → model):
- Tests written / unexpected passes:
- Test disputes and rulings:
- Review findings (verified / dropped with reason) and fix rounds:
- Asset QA: contact sheets, defects, lock match:
- Regression result:
- Playtest: criteria → PASS / FAIL / NEEDS-HUMAN, evidence paths:
- Files changed:

## Playtest and Integration Checkpoints
| Checkpoint | After | Proves | Integration tests | Playtest | Evidence |
|---|---|---|---|---|---|

## NEEDS-HUMAN
(Criteria screenshots can't settle — feel, timing, audio, haptics — and what the user should try.)

## Audio and Art Stubs
(Stubbed or greybox assets that ship in this build, and why.)

## Deviations from the blueprint
(Manifest corrections, inferred ownership, legacy-manifest mappings, art fallbacks, anything done
differently from the architecture — and why.)

## Lead-local fixes
(Tiny-glue edits made by the lead: file, change, why a worker wasn't worth it.)

## Final Verification
- test / typecheck / build or export / smoke / screenshot: {results vs baseline}
- Traceability (`check_traceability.py`): {n}/{n} cited gdd_refs proven by a test · untested: {refs}
- gdd_refs coverage: proven by tests {refs} · by playtest {refs} · deferred {refs}
- Slice playtest: {result, evidence paths}
- Asset defects remaining:
- Open items:
- Agents by role and model; escalations:
- First-pass rate by role and tier (first attempt passed its gate):

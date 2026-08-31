# Build Progress

Status: `not-started` | `in-progress` | `blocked` | `done` | `verified` | `COMPLETE`

## References

- Architecture: `[path]`
- Requirements: `[path]`
- Build Manifest: `present | absent` (path if present)
- Mode: `PM | Developer`
- Budget Tier: `hobby | startup | scaling | enterprise`
- Rigor: `light | standard | full` (from Mode + scope)

## Environment

- Install / test / typecheck / build commands (from architecture/manifest when available):
- Notes:

## Resume Snapshot

Enough for a restarted session to continue without redoing green work:

- Last completed phase id / name:
- Last green verification (commands + outcome summary):
- Open review findings (MUST-FIX + SHOULD-FIX — both must clear before phase verified):
- Worktrees / branches in play (if any):
- Active Task worker ids (role → id, for resume):

## Current Phase

- Phase name / number / manifest id:
- Requirement refs:
- Status: `not-started` | `in-progress` | `blocked` | `done` | `verified`
- Active workers (role → owned files / isolation):

## Phase Log

### Phase N: {Name}

Requirement refs:

| Step | Status | Notes |
|------|--------|-------|
| Tests | | |
| Red check | | |
| Test review | | |
| Implementation | | |
| Impl review | | |
| Regression | | |

Files created/modified:

Verification commands and results:

MUST-FIX / SHOULD-FIX (all must be fixed before phase verified):

## Integration

- Checkpoints (from architecture when present):
- Seams covered:
- Results:

## Final Verification

- Full suite:
- Typecheck / build:
- Requirement refs covered / gaps:
- Review findings remaining (should be none):
- Unresolved risks:

## Parent-Local Fixes

(Tiny critical-path edits done by the orchestrator parent, if any.)

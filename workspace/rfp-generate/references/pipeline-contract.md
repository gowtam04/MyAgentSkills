# This skill in the pipeline

**Requires:** `rfp-analyzer` + `rfp-config`. If those outputs are missing, tell the user which prior skill to run. Mock (`03-mock/`) is recommended, not required; reuse its file map when present.

**Owns:** intake of real facts, then the final package from intake only. May refresh Prime/Sub checklists if intake adds artifacts the master checklist already implied — do not invent new RFP requirements.

**Does not own:** invented values; ghost-writing a partner’s experience.

## Event folder

The Git working folder has one subdirectory per RFP, named the Event ID. Work in that folder (no extra `rfp/` prefix).

```
<working-folder>/<event-id>/
  00-source/package/
  01-analysis/master-checklist.yaml
  01-analysis/key-staff.yaml
  02-config/team.yaml            # user_is, owners, work_split
  03-mock/                       # optional file map
  04-intake/intake.yaml          # write (part 1)
  05-final/                      # write (part 2)
    README.md
    compliance-matrix.md
    ...
```

If cwd is already the event folder, use it. If cwd is the working folder, use `<cwd>/<event-id>/`. If several event folders exist and the user did not name one, ask.

## Invention

Part 1: missing → `status: missing`, never a plausible fill-in.

Part 2: every value traces to `intake.yaml` or RFP-required boilerplate. Block artifacts whose required fields are missing.

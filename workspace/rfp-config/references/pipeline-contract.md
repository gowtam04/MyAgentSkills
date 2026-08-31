# This skill in the pipeline

**Requires:** `rfp-analyzer` output. If `01-analysis/master-checklist.yaml` or `01-analysis/key-staff.yaml` is missing, tell the user to run `/rfp-analyzer`.

**Owns:** `team.yaml`, Prime checklist PDF, Sub checklist PDF (derived from the master checklist; do not invent new requirements).

**Does not own:** new RFP requirements, mock/final documents, rates, bios.

**Next:** `/rfp-mock`

## Event folder

The Git working folder has one subdirectory per RFP, named the Event ID. Work in that folder (no extra `rfp/` prefix).

```
<working-folder>/<event-id>/
  00-source/event-meta.yaml          # read: solicitation_vehicle
  01-analysis/
    master-checklist.yaml            # read: items to route (id, category, role, joint, volume, artifact, source, form_file, required)
    key-staff.yaml                   # read: roles to assign
    analysis-report.md               # read: takeaways / mandatory quals
  02-config/                         # write
    team.yaml
    prime-checklist.pdf
    sub-checklist.pdf                # omit if prime-only
```

If cwd is already the event folder, use it. If cwd is the working folder, use `<cwd>/<event-id>/`. If several event folders exist and the user did not name one, ask.

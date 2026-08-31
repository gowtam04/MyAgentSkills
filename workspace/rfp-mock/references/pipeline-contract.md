# This skill in the pipeline

**Requires:** `rfp-analyzer` + `rfp-config`. If `01-analysis/master-checklist.yaml` or `02-config/team.yaml` is missing, tell the user which prior skill to run.

**Owns:** full MOCK proposal package matching this RFP’s real structure.

**Does not own:** real company data, unmarked submission files.

**Next:** `/rfp-generate`

## Event folder

The Git working folder has one subdirectory per RFP, named the Event ID. Work in that folder (no extra `rfp/` prefix).

```
<working-folder>/<event-id>/
  00-source/package/                 # official forms to fill, not redraw
  01-analysis/master-checklist.yaml  # items, volumes, format_rules, form_file
  01-analysis/key-staff.yaml
  02-config/team.yaml                # who is prime/sub; which roles sit where
  03-mock/                           # write
    README.md
    ...
```

If cwd is already the event folder, use it. If cwd is the working folder, use `<cwd>/<event-id>/`. If several event folders exist and the user did not name one, ask.

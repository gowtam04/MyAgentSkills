# This skill in the pipeline

`rfp-analyzer` is first. It does not need prior RFP skill output.

**Owns:** event research, analysis briefing, master checklist (no owners), key-staff table.

**Does not own:** prime/sub, proposal prose, bidder strategy as fact.

**Next:** `/rfp-config`

## Event folder

The user keeps a Git working folder (a repo) with **one subdirectory per RFP, named the Cal eProcure Event ID**. All files this skill writes go in that event folder. There is no extra `rfp/` prefix.

```
<working-folder>/                 # git repo
  0000037577/                     # event folder
    00-source/
      event-meta.yaml
      manifest.md
      package/
    01-analysis/
      analysis-report.pdf
      analysis-report.md
      master-checklist.yaml
      master-checklist.pdf
      key-staff.yaml
  0000038001/                     # a different RFP
    ...
```

Resolve the event folder:

1. If cwd (or a parent) already looks like an event folder — directory name is an Event ID, or it contains `00-source/`, `01-analysis/`, or `event-meta.yaml` — use it.
2. Otherwise cwd is the working folder. Create `<cwd>/<event-id>/` if needed and use that.
3. If several event folders exist and the user did not name one, ask which Event ID.

Do not write outputs into this skill’s source tree.

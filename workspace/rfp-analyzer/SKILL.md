---
name: rfp-analyzer
description: >
  Research a California Cal eProcure RFP/IFB from its event URL (or a dropped
  event package) and produce a plain-language analysis briefing plus a master
  submission checklist. Use when the user pastes a caleprocure.ca.gov link,
  an Event ID, "analyze this RFP", "Cal eProcure RFP", "what does this
  solicitation require", or runs /rfp-analyzer. First skill in the Cal eProcure
  response pipeline; does not write the proposal.
---

# RFP analyzer

Act as a capture-team analyst for California State procurements. Turn a Cal eProcure event into (1) a plain-language analysis briefing and (2) a master checklist of everything needed for a responsive bid.

## Resources (read first, in order)

1. `references/pipeline-contract.md`
2. `references/cal-eprocure.md`
3. `references/analysis-report.md`
4. `references/master-checklist.schema.md`
5. `assets/analysis-exemplar.pdf` (visual target)

Also load the bundled `pdf` skill before rendering the briefing.

## Core rules

- The Event Package is the source of truth, not the Event Details blurb.
- Do not assign prime/sub or write proposal content.
- Do not invent bidder strategy as fact. Takeaways are constraints the documents impose.
- Every checklist item cites a source (part, exhibit, addendum).
- Adapt sections to **this** buy. Do not force the exemplar’s CAB Online outline onto a different solicitation.

## Procedure

### 1. Locate the working tree

Follow the event-folder rules in the pipeline contract. Event ID = folder name directly under the Git working folder (not under an extra `rfp/` prefix). Reuse that folder if it already exists.

### 2. Obtain sources

Follow `cal-eprocure.md` (PeopleSoft GBL GET for headers; headed real-Chrome + CDP for every Event Package file; user-dropped files last resort). Write `00-source/event-meta.yaml` and `00-source/manifest.md`. Do not analyze from the Event Details SPA shell.

### 3. Read the package

Follow the reading order in `cal-eprocure.md`. Latest addendum wins. Extract at least:

- What is being bought and why
- Current environment (if IT/services)
- Term, phasing, payment, SLAs, location/offshore
- Key-staff roles and mandatory quals
- Submission volumes, format, due date/time/zone, channel
- Scoring and mandatory-fail conditions
- Named forms/exhibits/workbooks
- Solicitation vehicle (open RFP, CMAS, SB/DVBE option, …)

### 4. Public context (narrow)

Only to explain named systems, statutes, or the buying org as they relate to this SOW. Cite URLs. No generic agency padding.

### 5. Write the analysis

Write `01-analysis/analysis-report.md` to the section and voice contract in `analysis-report.md`. Then render `01-analysis/analysis-report.pdf` to the visual bar in that file (match the exemplar). Inspect rendered pages; fix layout before continuing.

### 6. Write the master checklist and key staff

Write `01-analysis/master-checklist.yaml` and `01-analysis/key-staff.yaml` per `master-checklist.schema.md`. Render `01-analysis/master-checklist.pdf` as a clean human table grouped by category (id, name, required, source, artifact, volume, notes). No owner column.

Completeness: a stranger could assemble a responsive bid from the checklist without re-reading the RFP.

### 7. Handoff

List output paths. Then: “Analysis complete. Next: `/rfp-config` to set prime/sub and produce the partner checklists.”

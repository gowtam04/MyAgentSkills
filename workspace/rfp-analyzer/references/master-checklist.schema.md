# Master checklist schema

Write `01-analysis/master-checklist.yaml`. The human PDF is a rendering of this file. **No `owner` field** — later skills assign owners.

## File shape

```yaml
event_id: "0000037577"
solicitation_id: "RFP 26-10053 A5"
title: ""
due_at: "2026-03-04T12:00:00-08:00"   # timezone required
submission:
  method: "caleprocure"               # caleprocure | email | physical | other
  method_notes: ""
  volumes:
    - id: V1
      name: "Volume 1 — Technical/Administrative"
      sealed_separately: false
    - id: V2
      name: "Volume 2 — Cost"
      sealed_separately: true
  format_rules: []                    # page limits, fonts, original-forms-only, filenames
  delivery_notes: ""
solicitation_vehicle: "open_rfp"      # open_rfp | ifb | cmas | lpa | sb_dvbe_option | rfq | other
items: []
```

## Item

```yaml
- id: CL-001
  category: process            # process | administrative | qualifications | technical | cost | compliance | format
  name: "Acknowledge Addendum 5"
  required: mandatory          # mandatory | optional | conditional
  condition: ""                # if conditional: when it applies
  source: "Addendum 5; Part 1 §3.2"
  artifact: attestation        # pdf | docx | xlsx | form | attestation | narrative | resume | reference | workbook | other
  form_file: ""                # filename under 00-source/ if an official form exists
  volume: V1                   # or null for process gates (conference, due date)
  page_limit: null
  notes: ""
  role: ""                     # key-staff role name if this item is tied to one role; else ""
  joint: false                 # true for teaming agreement, CUF, combined DVBE, etc.
```

IDs are `CL-` plus three digits, assigned in reading order, never reused. Append new IDs if the analyzer is re-run after an addendum; do not renumber.

## Categories

| category | Examples |
|---|---|
| process | Intent to bid, mandatory pre-bid, Q&A cutoff, due date/time, submission channel |
| administrative | Cover letter, confidentiality, GenAI disclosure, addenda ack, STD forms, TACPA |
| qualifications | Bidder qual form, firm references, **each key-staff role** (qual form, resume, references, certs) as separate items |
| technical | Exhibit B Yes/No, approach narratives, deliverable confirmations |
| cost | Each cost worksheet, sealed-separately packaging |
| compliance | DVBE %, SB preference, insurance, bonds, licenses, no-offshore, CMAS proof if the vehicle needs it |
| format | File naming, page limits, font, “do not modify official forms” |

If the RFP lists a named form or exhibit, it is an item. If the RFP lists a key-staff role, that role produces **multiple** items (minimum: qual form, resume; plus references/certs when required).

## Completeness gate

The checklist is complete only if a stranger could assemble a responsive bid from it without re-reading the RFP. Process gates and format rules count. “See Part 1” is not an item.

## Key-staff sidecar

Also write `01-analysis/key-staff.yaml`:

```yaml
event_id: "0000037577"
roles:
  - id: KS-01
    title: "Project Manager"
    mandatory: true
    shareable: false
    minimum_quals: "PMP/PgMP; N years …"
    source: "Part 1 §7.3"
    related_checklist_ids: [CL-040, CL-041, CL-042]
```

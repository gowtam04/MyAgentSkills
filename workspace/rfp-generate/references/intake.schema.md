# Intake schema

Write `04-intake/intake.yaml` in part 1. Final documents may only use values from this file plus RFP-required boilerplate (e.g. addenda acknowledgements).

## File shape

```yaml
event_id: "0000037577"
solicitation_id: ""
confirmed_at: ""               # ISO datetime when user confirmed intake is complete
fields: []
artifacts: []                  # uploaded files the user provided
```

## Field

```yaml
- id: IN-001
  checklist_id: CL-010         # master checklist id this satisfies; or null if supporting
  name: "Prime legal name"
  value: ""
  status: provided             # provided | missing | not_applicable
  missing_reason: ""
  source: "user"               # user | upload | team.yaml | rfp_boilerplate
  notes: ""
```

`team.yaml` facts already known (legal names, CMAS numbers, SB/DVBE flags, role owners) are copied into intake at the start with `source: team.yaml` and confirmed, not re-invented.

## Status rules

| status | Meaning | Allowed in final docs? |
|---|---|---|
| provided | User (or upload) gave a value | Yes |
| not_applicable | User said it does not apply, with `missing_reason` | Only as “N/A” if the RFP allows N/A |
| missing | Needed and not given | **No.** Block generation of any artifact that needs it |

Never fill `value` with a guess, a mock leftover, or “TBD”.

## What to collect

Drive from `master-checklist.yaml` + `team.yaml`, not from a generic company questionnaire.

Always, when applicable:

- Entity: legal name, dba, address, FEIN, DUNS/UEI, website, authorized signer name/title
- Vehicles: CMAS number(s) and categories, SB cert number/expiry, DVBE cert number/expiry
- Contacts: proposal contact, day-to-day, after-hours
- Insurance / bonds / licenses the checklist requires, with document paths
- Each named person for owned roles: legal name, title, employer (prime or sub), years, certifications, resume path, reference contacts if required
- Past-performance projects the user wants used: customer, contract #, dates, value, scope, contact
- Narrative answers the user wants used (or “write from these bullets only”)
- Cost inputs the user is willing to provide (do not invent rates)

If the user is **prime**, intake must also account for every package-level field even when the file will come from the sub: either an uploaded sub artifact (`artifacts[]`) or `status: missing`.

If the user is **sub**, collect only what the sub owns plus joint items they must sign. Do not demand the prime’s cost workbook.

Use `team.yaml` `resources[].owner` and `work_split` to decide what the user owns. Do not re-derive prime/sub.

## Artifacts

```yaml
- id: ART-001
  path: ""                     # workspace path
  checklist_ids: [CL-041]
  description: "Resume — Solution Architect"
```

## Completeness gate (leave intake only when)

- Every **mandatory** checklist item owned by the user has a `provided` field or a blocking `missing`.
- User confirmed the recap (including the missing list).
- No field has a non-empty `value` with `status: missing`.

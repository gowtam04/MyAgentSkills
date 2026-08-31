---
name: rfp-config
description: >
  Configure who is prime and who is sub (or prime-only) for a Cal eProcure
  proposal, assign each key-staff resource and workstream to a firm, and
  derive partner-shareable Prime and Sub checklists. Use when the user says
  "set the prime and sub", "who owns which resources", "RFP team config",
  "generate the prime checklist", "subcontractor checklist", or runs
  /rfp-config. Runs after /rfp-analyzer. User's CMAS is enough to prime only
  when this solicitation's vehicle actually allows it.
---

# RFP config

Act as capture-team coordinator. Decide prime vs sub for **this** event, assign resources, write `team.yaml`, and derive the Prime and Sub checklists the partner will use.

## Resources (read first, in order)

1. `references/pipeline-contract.md`
2. `references/team-config.schema.md`

Load the bundled `pdf` skill before rendering partner checklists.

## Core rules

- Require `01-analysis/master-checklist.yaml` and `01-analysis/key-staff.yaml`. If missing, tell the user to run `/rfp-analyzer`.
- Do not add or drop RFP requirements. Route existing `CL-*` items.
- Do not collect bios, rates, addresses, or FEIN — that is `/rfp-generate` intake.
- Ask before assuming. Recommendations are allowed; silent defaults are not.
- If there is no sub, emit only the Prime checklist (full master, all owned by prime).

## Procedure

### 1. Load the analysis

Open the event folder from the pipeline contract (`<working-folder>/<event-id>/`). Read `event-meta.yaml` (vehicle), `master-checklist.yaml`, `key-staff.yaml`, and the analysis takeaways. Summarize in a few lines: vehicle, due date, mandatory quals that affect who can prime, key-staff count.

### 2. User firm (minimum)

Ask (free text / cards as fits): legal name, CMAS number(s) and categories if any, Small Business yes/no, DVBE yes/no. Stop there.

### 3. Prime vs sub

Using the vehicle + mandatory quals + CMAS rule in `team-config.schema.md`, **recommend** one of:

- User primes, no partner
- User primes, partner is sub
- Partner primes, user is sub

State why in one paragraph (e.g. “This is a PCC 6611 competitive RFP, not a CMAS order, so CMAS does not by itself make you the bidder of record.”). Confirm with `ask_user_question`. If a partner exists, collect their legal name and SB/DVBE flags.

### 4. Assign resources

For every role in `key-staff.yaml`, assign `prime` or `sub`. Honor `shareable: false` (do not split that role). Batch related roles in `ask_user_question` (multi-select or grouped cards). Then assign high-level `work_split` (narratives, past performance, cost workbook, DVBE source) — ownership only, not content.

### 5. Write `02-config/team.yaml`

Exact shape in `team-config.schema.md`. Include `prime_decision_rationale`.

### 6. Derive partner checklists

Apply the routing table in `team-config.schema.md` to every master-checklist item. Write:

- `02-config/prime-checklist.pdf`
- `02-config/sub-checklist.pdf` (omit if `prime_only`)

Partner-ready PDFs: grouped sections, each row = what / RFP cite / artifact / notes. Prime PDF includes **Collect from sub**. Joint items labeled “coordinate”. No YAML, no mock names, no win themes.

Inspect rendered pages before finishing.

### 7. Handoff

List output paths. Then: “Team configured. Share the Prime/Sub checklists with the partner. Next: `/rfp-mock` for a format-review package.”

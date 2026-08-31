# Team config schema

Write `02-config/team.yaml`. Prime/Sub checklist PDFs are **derived** from `01-analysis/master-checklist.yaml` + this file.

## File shape

```yaml
event_id: "0000037577"
solicitation_id: "RFP 26-10053 A5"
user_is: prime                 # prime | sub
structure: prime_sub           # prime_only | prime_sub
solicitation_vehicle: open_rfp
cmas_sufficient_to_prime: false
prime_decision_rationale: >
  Open competitive CDT STP RFP under PCC 6611, not a CMAS order.
  User confirmed partner will prime.
prime:
  legal_name: ""
  is_user: false
  cmas_numbers: []
  cmas_categories: []
  small_business: false
  dvbe: false
  notes: ""
sub:                           # omit or null if prime_only
  legal_name: ""
  is_user: true
  cmas_numbers: []
  cmas_categories: []
  small_business: false
  dvbe: false
  notes: ""
resources:                     # one row per key-staff.yaml role
  - role_id: KS-01
    title: "Project Manager"
    owner: prime               # prime | sub
    shareable: false
work_split:
  narratives:                  # high-level ownership of narrative areas, not the prose
    - area: "Technical approach"
      owner: prime
    - area: "OCM / training"
      owner: sub
  past_performance_owner: prime
  cost_workbook_owner: prime
  dvbe_participation_source: sub   # prime | sub | both | none
joint_items:
  - "Teaming agreement"
  - "Commercially Useful Function documentation"
```

Full addresses, FEIN, staff names, rates, and bios do **not** belong here. That is `/rfp-generate` intake.

## Prime vs sub rule

1. Read `solicitation_vehicle` from `event-meta.yaml` / master checklist.
2. Read user’s CMAS numbers/categories and SB/DVBE (asked in this skill).
3. Recommend:
   - **User primes** if this event is a CMAS/LPA order covered by their schedule, **or** it is an open RFP/IFB and nothing in the mandatory bidder quals obviously bars them (state residual risk).
   - **Partner primes** if the vehicle is an open competitive RFP that CMAS does not satisfy, or mandatory quals/licenses are a gap.
   - **Prime-only** if the user says there is no partner.
4. User confirms. Record `prime_decision_rationale` in one short paragraph of facts they agreed to.

Never default silently. CMAS is not “enough to prime” a PCC 6611 competitive RFP just because the firm holds a CMAS.

## Deriving partner checklists

For each `items[]` row in the master checklist:

| Rule | Prime list | Sub list |
|---|---|---|
| `structure: prime_only` | all items | (no sub PDF) |
| `joint: true` | include, label “coordinate with sub” | include, label “coordinate with prime” |
| `role` set and that role’s `owner` is prime | include | omit |
| `role` set and that role’s `owner` is sub | include under **Collect from sub** | include |
| category `cost` and `cost_workbook_owner` is prime | include | omit (unless joint) |
| process / format / administrative entity forms | include on **prime** (bidder of record). Sub only if the form is about the sub entity (sub’s SB/DVBE cert, sub’s insurance, sub’s qual form) | sub-entity items only |
| Unclear | ask; do not guess | ask |

Do not add requirements that are not in the master checklist. Role-derived rows already exist as separate CL items (resume, qual form, …); assignment just routes them.

Prime PDF sections: process gates, what prime prepares, **Collect from sub**, joint/coordinate, format/packaging.

Sub PDF sections: what sub must send the prime, joint/coordinate, named roles they staff, due-to-prime-by if the user set one.

Tone: partner-shareable. No YAML, no mock names, no win-strategy commentary. Each row: what, RFP cite, artifact/format, notes.

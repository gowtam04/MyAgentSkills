---
name: rfp-generate
description: >
  Generate the final Cal eProcure proposal: first a comprehensive intake that
  collects every required fact (nothing assumed or invented), then professional
  submission documents built only from that intake. Use when the user says
  "generate the RFP response", "final proposal", "intake for the bid",
  "write the real proposal", or runs /rfp-generate. Runs after /rfp-analyzer
  and /rfp-config. Do not write finals until intake is complete. Never
  hallucinate rates, bios, certifications, or past performance.
---

# RFP generate

Two parts, in order. Act as proposal-ops with a hard no-invention rule. Part 1 collects facts. Part 2 writes the package. Do not start Part 2 until intake is confirmed.

## Resources (read first, in order)

1. `references/pipeline-contract.md`
2. `references/intake.schema.md`
3. `references/proposal-package.md`

Load bundled `pdf` and `docx` skills before writing documents.

## Core rules

- Require analysis + `02-config/team.yaml`. If missing, tell the user which prior skill to run. Mock is recommended, not required; if `03-mock/` exists, reuse its file map.
- Every final value traces to `04-intake/intake.yaml` or RFP-required boilerplate (addenda ack, restated shalls). Nothing else.
- Missing required facts **block** the artifacts that need them. Do not write around gaps.
- Do not ghost-write a partner’s experience. Uploaded sub/prime artifacts or `status: missing`.
- You may refresh Prime/Sub checklists if intake reveals extra artifacts the master checklist already implied. Do not invent new RFP requirements.

---

## Part 1 — Intake

### 1. Build the field list

From `master-checklist.yaml` + `team.yaml`, create one intake field per fact needed for items the user owns, plus package-level fields if the user is prime (see `intake.schema.md`). Copy known `team.yaml` values in with `source: team.yaml` and confirm them.

### 2. Collect

Interview until every mandatory owned item is `provided`, `not_applicable` (with reason), or `missing` (with reason). Accept uploads; record paths in `artifacts[]`. Use `ask_user_question` for choices; free text for names, numbers, prose, paths.

Never pre-fill with mock data, “typical” rates, or guessed cert numbers.

### 3. Recap and confirm

Show a recap: provided counts, missing (blocking) list, N/A list. Confirm via `ask_user_question`. Write `04-intake/intake.yaml` only after confirmation (`confirmed_at` set).

If the user wants to generate anyway with gaps, still write intake, then in Part 2 emit only unblocked artifacts and list BLOCKED items in the compliance matrix. Do not silently omit them.

---

## Part 2 — Generate

### 4. Gate

If any **mandatory** field for an artifact is `missing`, do not produce that artifact. List blockers first.

### 5. Write `05-final/`

Follow `proposal-package.md`. Same volume/file map as mock when mock exists, with MOCK labels removed.

- Fill official forms from `00-source/` with intake values.
- Narratives: only user-approved bullets/prose from intake; no embellished past performance.
- Cost: only if rates are `provided`.
- Headers/footers: solicitation ID, volume, page n of m. Professional, neat, consistent.
- No `TBD`, `lorem`, leftover mock names, or placeholder certs.

### 6. Index and matrix

- `05-final/README.md` — file → checklist IDs → volume
- `05-final/compliance-matrix.md` — every mandatory `CL-*` → file/page or BLOCKED

### 7. Visual check

Render first pages of each PDF. Fix layout. Confirm no MOCK watermark remains.

### 8. Handoff

“Final package is in `05-final/`. Review the compliance matrix before submitting on Cal eProcure.”

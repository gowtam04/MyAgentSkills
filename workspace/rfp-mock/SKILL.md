---
name: rfp-mock
description: >
  Build a complete MOCK Cal eProcure proposal package — every mandatory
  section, form, and volume — using obviously fake data so a partner can
  approve format before real content exists. Use when the user says "mock
  the RFP response", "sample proposal package", "format review for our
  partner", "dummy bid", or runs /rfp-mock. Runs after /rfp-analyzer and
  /rfp-config. Every page must be labeled MOCK — NOT FOR SUBMISSION.
---

# RFP mock

Act as proposal-ops. Produce a thorough, submission-shaped package with fake data so the partner can accept or mark up format, section order, forms, and page limits.

## Resources (read first, in order)

1. `references/pipeline-contract.md`
2. `references/proposal-package.md`

Load bundled `pdf` and `docx` skills before writing documents.

## Core rules

- Require `01-analysis/master-checklist.yaml` and `02-config/team.yaml`. If missing, tell the user which prior skill to run.
- Structure = this RFP’s checklist and volumes, not a generic template.
- Fill official forms from `00-source/`. Do not redraw them.
- Invented data must be obviously fake. Label **every** page and sheet `MOCK — NOT FOR SUBMISSION`.
- Completeness beats polish: a missing mandatory section fails the format review.
- Honor page limits, fonts, and file-naming rules from the checklist `format_rules`.

## Procedure

### 1. Load

Open the event folder (`<working-folder>/<event-id>/`). Read master checklist, key-staff, team.yaml, and `submission.volumes`. List the artifact set you will produce (file → CL ids → volume) and confirm with the user only if the RFP is ambiguous about packaging.

### 2. Build `03-mock/`

Follow `proposal-package.md`. For each mandatory (and each optional-you-are-including) checklist item, emit the artifact:

- Narratives: DOCX/PDF with mock firm (`Example Systems LLC` as the firm matching `user_is`, `Partner Example LLC` as the other), mock staff, mock past performance.
- Forms/workbooks: copies from `00-source/` filled with mock values.
- Cost: State workbook, round fake numbers, MOCK label, sealed-separately folder if required.
- Administrative attestations: mock-signed, clearly fake.

Reflect `team.yaml` in the mock (who is prime, which roles sit where) so the partner sees the real division of labor with fake names.

### 3. Index

Write `03-mock/README.md`: `file → checklist IDs → volume`. Every mandatory `CL-*` must appear.

### 4. Visual check

Render first pages of each PDF. Fix overflow, missing watermarks, and volume mix-ups (cost in Volume 1, etc.).

### 5. Handoff

List the mock folder. Then: “Mock package ready for partner format review. After they sign off (and you have real inputs), run `/rfp-generate`.”

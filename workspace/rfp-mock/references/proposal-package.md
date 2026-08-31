# Mock proposal package

Structure always comes from **this** RFP’s master checklist, not a generic proposal template.

## Official forms

If `00-source/` contains an official form or workbook (`form_file` on a checklist item):

- Copy it into `03-mock/`.
- Fill it (xlsx cells, fillable PDF fields, or the `pdf` skill’s form recipes) with mock values.
- Do **not** recreate STD forms, Exhibit C, or State templates in Word.

If the form is locked/macros-only and cannot be filled here, produce a clearly named companion sheet and say so in the README. Still do not redraw the State form.

## Narratives

- DOCX and/or PDF as the RFP specifies. Default DOCX if unspecified, plus a PDF export if useful for the partner.
- Honor page limits, fonts, margins, and file-naming rules from `submission.format_rules`.
- Headers/footers: solicitation ID, volume, page n of m, plus **MOCK — NOT FOR SUBMISSION**.
- Use the bundled `docx` and `pdf` skills. US Letter. Visual-check first pages.

## Cost

Use the State’s Exhibit C / cost xlsx from `00-source/`. Round fake numbers. MOCK label on every sheet. If Volume 2 is sealed separately, put cost in its own folder and say so in the README. Never mix cost figures into Volume 1 narratives unless the RFP requires it.

## Data

Obviously fake: `Example Systems LLC` as the firm matching `user_is` in `team.yaml`, `Partner Example LLC` as the other, `Jane Q. Architect` for staff, round numbers for rates. Reflect the real prime/sub split from `team.yaml` with those fake names.

Every page and sheet: **MOCK — NOT FOR SUBMISSION**.

## Completeness

Every mandatory checklist item has an artifact. A missing mandatory section fails the format review.

## Index

`03-mock/README.md`: table of `file → checklist IDs → volume`. Every mandatory `CL-*` must appear.

## Quality

After writing PDFs: render 1–2 pages with `pdftoppm` and inspect watermarks, overflow, and volume mix-ups.

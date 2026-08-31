# Final proposal package

Structure always comes from **this** RFP’s master checklist (and from `03-mock/`’s file map when it exists), not a generic proposal template.

## Official forms

If `00-source/` contains an official form or workbook (`form_file` on a checklist item):

- Copy it into `05-final/`.
- Fill it (xlsx cells, fillable PDF fields, or the `pdf` skill’s form recipes) with **intake** values.
- Do **not** recreate STD forms, Exhibit C, or State templates in Word.

If the form is locked/macros-only and cannot be filled here, produce a clearly named companion sheet and say so in the README. Still do not redraw the State form.

## Narratives

- DOCX and/or PDF as the RFP specifies. Default DOCX if unspecified.
- Honor page limits, fonts, margins, and file-naming rules from `submission.format_rules`.
- Headers/footers: solicitation ID, volume, page n of m. No MOCK labels.
- Use the bundled `docx` and `pdf` skills. US Letter. Visual-check first pages.
- Only user-approved bullets/prose from `intake.yaml`. No embellished past performance.

## Cost

Use the State’s Exhibit C / cost xlsx from `00-source/`. Fill only if rates are `provided` in intake. If rates are `missing`, do not emit a filled cost workbook. If Volume 2 is sealed separately, put cost in its own folder and say so in the README. Never mix cost figures into Volume 1 narratives unless the RFP requires it.

## Data

Every sentence/value traces to `04-intake/intake.yaml` or RFP-required boilerplate (e.g. “we acknowledge Addendum 5”). If a required field is `missing`, do not produce that artifact; list it BLOCKED in the compliance matrix.

Do not ghost-write a partner firm’s experience. Use their uploaded artifacts or block.

## Index

- `05-final/README.md`: `file → checklist IDs → volume`
- `05-final/compliance-matrix.md`: every mandatory `CL-*` → file + location (page or sheet), or BLOCKED

## Quality

- No `lorem`, `TBD`, `TODO`, leftover mock names, or placeholder certs.
- After writing PDFs: render 1–2 pages with `pdftoppm` and inspect. Confirm no MOCK watermark remains.

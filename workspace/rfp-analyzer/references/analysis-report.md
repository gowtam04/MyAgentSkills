# Analysis report

Visual and section contract. Open `assets/analysis-exemplar.pdf` before writing the PDF. Match that family of document — not a generic memo and not a dump of RFP text.

Write `01-analysis/analysis-report.md` first (complete, cited), then render `01-analysis/analysis-report.pdf` with the bundled `pdf` skill (reportlab). After rendering, `pdftoppm` the first three pages and a middle page; fix overlap, clipping, and weak hierarchy before finishing.

## Voice

Plain language for a proposal team that has not lived in this RFP. Translate jargon, then keep the official term. One-sentence version of the whole buy. Numbers from the RFP, not rounded guesses. No bidder strategy presented as fact; takeaways are “what the documents force you to respect.”

## Visual bar (exemplar)

| Token | Value |
|---|---|
| Heading color | `#1B4F8A` |
| Rule / accent | `#2E8F9A` (teal underline under titles) |
| Table header fill | `#1B4F8A` with white text |
| Alt row | `#E8F1F8` |
| Info callout | pale blue fill, navy left bar |
| Timing / critical callout | pale orange fill, orange left bar |
| Body text | dark `#222`, ~10.5–11pt, generous line height |
| Page | US Letter, ~0.75" margins |
| Footer | `{short title} — {solicitation id} — Analysis Briefing` plus `n of m` |
| Cover title | large navy, teal rule, centered metadata |

Sans-serif throughout. No stock gradient heroes, no clip-art. Diagrams are labeled rounded boxes and arrows (current-state vs future-state), not screenshots of the RFP.

## Cover

Centered: project name (plain language), subtitle “What This Procurement Is About — A Plain-Language Analysis”, then solicitation ID, customer, conducted-by, solicitation date, analysis date, source list.

## Sections (adapt; do not force)

Omit a section if the RFP has no such content (a commodities IFB has no “existing applications”). Do not invent a CAB-Online-shaped outline for a different buy. Keep numbering contiguous.

1. **Executive summary — the project in plain terms.** Problem, what is being bought, one-sentence version, key-stats table (term, platform, delivery model, cost weight, SLA — only columns that exist).
2. **Who is buying and why.** Org, program, statutory or mission driver, contract type (fixed-price, vehicle, withhold).
3. **What exists today** (IT/services). Named systems, what is manual, pain points the RFP itself lists. Current-state diagram when it clarifies.
4. **What will be bought / built.** Concept, future-state diagram, requirement counts by capability if a matrix exists, interfaces table.
5. **Rollout, term, phasing.**
6. **Why it is necessary** — only reasons the RFP (or cited public source) actually gives.
7. **How the project will run.** Term, deliverables methodology, key staff, SLAs, location/offshore, payment.
8. **What bidders must submit and how they are scored.** Volumes, sealed cost, weights, mandatory-fail conditions. This section is mandatory for every RFP/IFB.
9. **Key takeaways for the proposal.** Bullet constraints, not a sales pitch.
10. **Glossary + sources.**

## Diagrams

When the SOW has a current/future process, draw it. Caption as `Figure n — …`. Keep labels short. If a diagram would only repeat a table, skip it.

## Completeness gate

- Every figure in the stats table is in the source documents (or marked “not stated”).
- Submission/scoring section exists and matches the latest addendum.
- Key-staff roles listed in the RFP appear in the report **and** in `key-staff.yaml`.
- Sources list the RFP parts actually read, with dates/versions.

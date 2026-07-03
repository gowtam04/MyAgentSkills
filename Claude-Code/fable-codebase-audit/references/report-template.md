# Report structure

Write the final report to `CODEBASE_AUDIT.md` at the repo root (or the path the
user asked for). Follow this skeleton. It's ordered for a busy reader: the person
who opens this file wants the verdict and the top risks in the first screen, and
the exhaustive list only if they keep scrolling.

Fill every section with real content. If a section is genuinely empty (e.g. no
Critical findings — a good outcome), say so explicitly rather than deleting the
heading; an absent section reads as an oversight.

Keep prose tight. Engineers trust a report that respects their time. Link to
`file:line` everywhere so findings are one click from the code.

````markdown
# Codebase Audit — <repo name>

**Date:** <YYYY-MM-DD> · **Commit:** <short SHA> · **Auditor:** Claude Fable 5
**Scope:** <what was reviewed — dirs/modules included and anything excluded>

## Executive summary

Three to six sentences a tech lead can read in under a minute: overall health,
the shape of the risk (where the serious stuff clusters), and the single most
important thing to do next. Name the standout strength too — an honest audit
isn't only a list of complaints.

**Overall health:** <one line — e.g. "Solid core, but auth and input handling
need work before this scales.">

**Findings at a glance:**

| Severity | Security | Correctness | Architecture | Maintainability | Total |
|----------|---------:|------------:|-------------:|----------------:|------:|
| Critical |          |             |              |                 |       |
| High     |          |             |              |                 |       |
| Medium   |          |             |              |                 |       |
| Low      |          |             |              |                 |       |
| **Total**|          |             |              |                 |       |

## Top risks — act on these first

The 3–7 findings that matter most, in priority order, each in two or three
lines. This is the section people actually act on. Every item links to its full
entry below.

1. **[CRITICAL] <title>** — <one-line why it matters> → `path/file:line` (#id)
2. ...

## System-level assessment

The architecture read that only a whole-codebase view can produce — this is the
part a single-file linter can never write, so make it count.

- **Architecture & boundaries:** how the system is structured, where the seams
  are clean and where they've eroded, coupling and dependency-direction issues.
- **Cross-cutting patterns:** concerns handled inconsistently across the code
  (auth, error handling, validation, logging, config).
- **Tech-debt hotspots:** files/areas where churn meets complexity — where the
  next bug is most likely to appear. Reference the recon churn data.
- **Testing & safety net:** how much of the risky code is actually covered.

## Findings

All findings, grouped by dimension, ordered by severity within each group. Use
the entry format below. Give each a stable id (`SEC-01`, `COR-01`, `ARC-01`,
`MNT-01`) so the summary and top-risks can link to it.

### Security
### Correctness
### Architecture
### Maintainability

<!-- Finding entry format: -->
#### <ID> · <Severity> · <short title>
- **Location:** `path/to/file.ext:line` (+ related locations)
- **What's wrong:** the defect, concretely.
- **How it fails:** the inputs/state/sequence that trigger it and the result.
- **Why it matters:** impact — who/what is affected and how badly.
- **Recommendation:** the fix direction (described, not applied).
- **Confidence:** high | medium | low · **Verified:** yes/how
- **Also relates to:** <other dimension, if any>

## Appendix

- **Recon snapshot:** languages, size, module map, churn hotspots (from
  `scripts/recon.sh`) — so the reader can see what "the whole codebase" meant.
- **Coverage & method:** how the review was sliced, how many agents ran, what
  was verified vs. reported at lower confidence.
- **Explicitly out of scope / not reviewed:** be honest about blind spots
  (generated code, vendored deps, a subsystem you couldn't reach). Silent gaps
  read as "audited and clean" when they weren't.
````

## Severity discipline in the report

- Lead with impact, not volume. A report with three Criticals and no filler is
  more useful than one with eighty Lows burying them.
- Every Critical/High must be verified (a skeptic pass confirmed it). Say so in
  the entry. If you couldn't verify a scary-looking one, keep it but mark it
  lower-confidence and explain what would confirm it.
- Group repeated instances of one root cause into a single finding with a list
  of locations, not N near-duplicate entries. Note the count — "this pattern
  appears in 14 handlers" is itself a signal.

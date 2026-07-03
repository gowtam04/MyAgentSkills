# Output structure — the `docs/review/fable/` collection

The audit is written as a directory of Markdown files, not one report. Two kinds
of file: **one index** and **one file per review area**.

```
docs/review/fable/
├── fable-review.md                     ← index (verdict, top risks, system read)
├── fable-review-01-tenant-isolation-rls.md
├── fable-review-02-authn-authz.md
├── fable-review-03-hipaa.md
├── …
└── fable-review-15-conventions.md
```

## Naming & numbering rules

- The index is always exactly `fable-review.md`. It has no number, so it sorts
  above every area file in the directory listing — the reader opens it first.
- Area files are `fable-review-NN-<slug>.md`:
  - `NN` is a zero-padded two-digit number: `01`, `02`, … `15`. Numbering runs in
    **priority order** — domain- and security-critical areas first, generic
    quality areas (testing, dependencies, conventions) last — so `-01-` is the
    most important thing to read.
  - `<slug>` is short kebab-case (2–4 words) naming the area:
    `tenant-isolation-rls`, `authn-authz`, `hipaa`, `ai-layer`, `secrets-infra`,
    `data-migrations-tx`, `async-events-jobs`, `web-bff`,
    `observability-resilience`, `testing`, `dependencies`, `conventions`.
  - Keep slugs stable across re-runs — the team links to and diffs these files,
    so a renamed file reads as a lost one.

Every area you reviewed gets a file, **including a clean one** — a file that says
"reviewed, nothing material found" is a signal, and it's the placeholder the team
updates next quarter. A missing file reads as "forgot to review that."

---

## The index — `fable-review.md`

Ordered for a busy reader: verdict and top risks in the first screen; the map and
the system read below. Fill every section; if one is genuinely empty (no
Criticals — a good outcome), say so rather than deleting the heading.

````markdown
# Codebase Review — <repo name>

**Date:** <YYYY-MM-DD> · **Commit:** <short SHA> · **Auditor:** Claude Fable 5
**Scope:** <what was reviewed — dirs/apps included and anything excluded>

## Executive summary

Three to six sentences a tech lead can read in under a minute: overall health,
the shape of the risk (which areas the serious stuff clusters in), and the single
most important thing to do next. Name the standout strength too — an honest audit
isn't only a list of complaints.

**Overall health:** <one line — e.g. "Solid core, but tenant isolation and the
AI layer need work before this scales.">

**Findings at a glance:**

| Severity | Security | Correctness | Architecture | Maintainability | Total |
|----------|---------:|------------:|-------------:|----------------:|------:|
| Critical |          |             |              |                 |       |
| High     |          |             |              |                 |       |
| Medium   |          |             |              |                 |       |
| Low      |          |             |              |                 |       |
| **Total**|          |             |              |                 |       |

## Top risks — act on these first

The 3–7 findings that matter most, in priority order, each in two or three lines.
This is the section people actually act on. Every item links to its full entry in
the relevant area file.

1. **[CRITICAL] <title>** — <one-line why it matters> →
   [`fable-review-01-tenant-isolation-rls.md`](fable-review-01-tenant-isolation-rls.md#sec-01)
2. …

## Review areas

The map of the audit. Each area links to its file. Counts are that area's
findings by severity; "health" is a two- to four-word read.

| # | Area | File | Crit | High | Med | Low | Health |
|--:|------|------|-----:|-----:|----:|----:|--------|
| 01 | Tenant isolation & RLS | [link](fable-review-01-tenant-isolation-rls.md) | | | | | needs work |
| 02 | AuthN / AuthZ | [link](fable-review-02-authn-authz.md) | | | | | mostly solid |
| … | | | | | | | |

## System-level assessment

The architecture read that only a whole-codebase view can produce — this is the
part a single-area agent can never write, so make it count.

- **Architecture & boundaries:** how the system is structured, where the seams
  are clean and where they've eroded, coupling and dependency-direction issues.
- **Cross-cutting patterns:** concerns handled inconsistently across areas (auth,
  error handling, validation, logging, config) — the thing you see only by
  holding all the area reports at once.
- **Tech-debt hotspots:** where churn (from recon) meets complexity — where the
  next bug is most likely to appear. Reference the recon churn data.
- **Testing & safety net:** how much of the risky code is actually covered.

## Coverage & method

- **How it was run:** how the codebase was carved into areas, how many review
  agents ran, what was verified vs. reported at lower confidence.
- **Recon snapshot:** languages, size, module map, churn hotspots (from
  `scripts/recon.sh`) — so the reader can see what "the whole codebase" meant.
- **Out of scope / not reviewed:** be honest about blind spots (generated code,
  vendored deps, a subsystem you couldn't reach). Silent gaps read as "audited
  and clean" when they weren't.
````

---

## An area file — `fable-review-NN-<slug>.md`

Self-contained: someone handed just this file should understand what was reviewed,
how healthy it is, and what to fix. Findings ranked by severity, each tagged with
its dimension (since the file isn't grouped by dimension — the area is the unit).

````markdown
# <NN> · <Area name>

[← back to index](fable-review.md) · **Date:** <YYYY-MM-DD> · **Commit:** <SHA>

**Scope:** <the paths / concern this area covers — e.g. `src/db/**`, every query
path that must be tenant-scoped>
**Area health:** <2–4 sentences: how solid this area is, where the risk sits, and
the one thing to fix first. If clean: "Reviewed across all four dimensions;
nothing material found." Say what's *solid* here too, not only what's broken.>

**Findings in this area:** <n> (Critical <n> · High <n> · Medium <n> · Low <n>)

## Findings

<!-- Ordered by severity. Give each a stable id: <AREASLUG or dimension>-NN,
     e.g. SEC-01, RLS-01 — so the index and other files can link to it. -->

### <ID> · <Severity> · <short title>

- **Dimension:** security | correctness | architecture | maintainability
  (+ secondary, if any)
- **Location:** `path/to/file.ext:line` (+ related locations)
- **What's wrong:** the defect, concretely.
- **How it fails:** the inputs/state/sequence that trigger it and the result.
- **Why it matters:** impact — who/what is affected and how badly.
- **Recommendation:** the fix direction (described, not applied — this is
  read-only).
- **Confidence:** high | medium | low · **Verified:** yes/how

### <ID> · <Severity> · <next finding>
…

## Also worth knowing

Optional: Info-level observations, cross-area notes ("the shared `db.query`
helper this depends on is audited in
[`fable-review-09-data-migrations-tx.md`](fable-review-09-data-migrations-tx.md)"),
and what a clean-but-not-perfect area still leaves you exposed to.
````

---

## Severity discipline (applies to every file)

- Lead with impact, not volume. Three real Criticals across the collection beat
  eighty Lows scattered through fifteen files.
- Every Critical/High must be verified (a skeptic pass confirmed it). Say so in
  the entry. If you couldn't verify a scary-looking one, keep it but mark it
  lower-confidence and explain what would confirm it.
- Group repeated instances of one root cause into a single finding with a list of
  locations, not N near-duplicate entries. Note the count — "this pattern appears
  in 14 handlers" is itself a signal.
- The index's glance table must reconcile with the area files: its totals are the
  sum of the per-area counts. If they don't add up, the reader stops trusting the
  report.

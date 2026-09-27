# Quality Bar

Check the docs against this before presenting them. The goal is a spec an architect can design
from and an agent team can verify against without asking anyone — longer is not better; specific
is better.

## Pass / fail checklist

| Area | Passes when |
|---|---|
| Overview | A newcomer can state what's being built, for whom, and why in one minute |
| Personas | Each role has goals, context, and a clear permission boundary |
| Workflows | Step-by-step happy paths, plus the failure / empty / conflict / permission-denied states that matter |
| Stories | Every story has a stable `US-n`; each is one capability, not an epic |
| Criteria | Every criterion has a stable `AC-n.m` and is Given/When/Then or a checkable assertion with real values |
| Rules | Every rule that gates behavior has a `BR-n` and exact wording (limits, states, who, when) |
| Data | Entities, relationships, ownership and lifecycle described in business terms — no schemas |
| Non-functional | Stated in user terms with numbers where they matter ("search returns in under 1s for 10k items") |
| Boundaries | Out of Scope names the adjacent things a builder might assume |
| Honesty | Open Questions are real unknowns; Assumptions are speed-path guesses, each with the IDs it affects and its change cost, most expensive first |
| Boundary with architecture | No framework, database, API or infra decisions; tech preferences appear only as constraints |
| Findability | Organized by domain, not interview order; short sections, tables and lists dominate |

## Anti-patterns (rewrite before presenting)

- **Feature names instead of behavior** — "Users can manage projects." Manage how? Who? Limits?
- **Untestable criteria** — "works correctly", "is fast", "is intuitive", "handles errors gracefully".
- **Happy path only** — no word on what happens when input is invalid, the network fails, or two
  users collide.
- **Invisible permissions** — capabilities described with no statement of who may use them.
- **Adjectives for numbers** — "lots of users", "large files", "quickly".
- **Architecture creep** — "stores sessions in Redis", "REST endpoint for…", "uses Stripe webhooks".
- **MVP tier theater** — the spec restructured into MVP / v2 / polish; the architect phases by
  dependency, so tiers just scatter related rules across files.
- **Silent assumptions** — a guessed rule written as if the user decided it.
- **Open Questions as a dumping ground** — questions you could have asked in the interview.
- **Clone-by-reference** — "like Trello" as the whole specification of a board.

## Bad → good

**Capability**
- Bad: "Users can manage their profile."
- Good: "Users can change their display name (1–50 characters), email (the new address must be
  verified before it's used for notifications), and photo (JPEG or PNG, max 5 MB, shown as a
  square crop)."

**Acceptance criterion**
- Bad: "AC-2.1 — Password reset works."
- Good: "AC-2.1 — Given a registered email, when the user requests a reset, then an email with a
  single-use link arrives; the link expires after 30 minutes and after first use."
- Good: "AC-2.2 — Given an unregistered email, when a reset is requested, then the screen shows
  the same confirmation as for a registered one (no account enumeration)."

**Business rule**
- Bad: "Invoices can't be changed after sending."
- Good: "BR-4 — Once an invoice's status is Sent, its line items and totals are read-only to every
  role. Corrections are made by issuing a credit note that references the original invoice."

**Workflow edge state**
- Bad: "The user uploads a CSV of contacts."
- Good: "The user uploads a CSV (max 10,000 rows). Rows with a missing email are skipped and listed
  in a downloadable error report; duplicates of existing contacts update the existing record.
  If more than 50% of rows fail, nothing is imported and the user sees the error report."

**Non-functional**
- Bad: "The dashboard should be fast."
- Good: "The dashboard's first meaningful content appears within 2 seconds on a typical laptop
  connection for an account with up to 5,000 projects."

**Out of scope**
- Bad: "Advanced features are out of scope."
- Good: "Out of scope for this release: team workspaces, CSV export, recurring invoices, and any
  mobile app (the web app must still be usable on a phone for approvals only)."

## Right-sizing

| Work | Package | Interview depth |
|---|---|---|
| Small change to an existing feature | One `requirements.md`, a few stories | Phases 1, 3 and 6, compressed |
| New feature, or a small product (≤3 domains) | One `requirements.md`, sections per functional area | All applicable phases, focused on what's new |
| Large product (4+ distinct domains, or one file would pass ~500 lines) | `overview.md` + one file per domain | Full interview |

If a section wouldn't change a build decision, cut it. If the spec is much longer than the product
is complex, look for restated rules and criteria that test the same thing twice.

## Final gate

1. Every primary workflow has its failure and permission states written down.
2. Every capability has at least one testable criterion with an ID.
3. Every rule that gates behavior has an ID and exact wording.
4. Out of Scope exists and names adjacent temptations.
5. Open Questions are real unknowns; Assumptions are labeled and confirmed.
6. None of the anti-patterns above remain.

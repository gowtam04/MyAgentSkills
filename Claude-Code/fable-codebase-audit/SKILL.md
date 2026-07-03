---
name: fable-codebase-audit
description: Run Claude Fable 5 as the orchestrator of a thorough, read-only audit of an entire codebase — security, correctness, architecture, and maintainability — by deriving a set of review areas specific to THIS codebase, fanning out cheaper review subagents over them, adversarially verifying every serious finding, then writing a collection of severity-ranked Markdown reports under docs/review/fable/ (an index plus one file per area). Use this skill whenever the user asks Fable to "audit", "review the whole codebase", "do a code review of the repo", "find bugs/vulnerabilities/security issues across the project", "assess code quality / tech debt / architecture", "health check", or "what's wrong with this codebase" — especially on a Fable-powered session with a large repo. Also trigger when someone wants a comprehensive pre-release, pre-acquisition (due-diligence), or onboarding review of an unfamiliar codebase, even if they don't say the word "audit".
---

# Fable Codebase Audit

You (Claude Fable 5) are the orchestrator of a whole-codebase audit. Your value
here is judgment at scale: deciding how to carve up the repo, reading conflicting
subagent reports and deciding what's real, seeing the system-level patterns no
single file reveals, and writing a review an engineering team will actually act
on. The token-heavy reading is delegated; the thinking is yours.

This is a **read-only audit**. You and your subagents investigate and report —
nobody edits code, runs migrations, or "just fixes this one thing." If the user
later wants fixes, that's a separate, explicitly-authorized fix pass — hand it to
a dedicated fix-oriented skill (e.g. `fable-architect`, if you have it), never to
this audit.

## The deliverable — a collection, not a single file

Write the audit as a set of Markdown files under **`docs/review/fable/`** at the
repo root:

```
docs/review/fable/
├── fable-review.md                       ← the index: verdict, top risks, system read
├── fable-review-01-<slug>.md             ← one file per review area
├── fable-review-02-<slug>.md
└── … (numbered, highest-stakes area first)
```

The area files are **derived from this codebase** — its architecture, domain, and
risk surface — not from a fixed checklist. A multi-tenant healthcare app earns a
`tenant-isolation` file and a `hipaa` file; an LLM product earns an `ai-layer`
file; a payments backend earns `money-handling` and `idempotency`. That
custom taxonomy is what separates this audit from a generic linter dump, and
deriving it well (step 2) is the heart of the job.

One file per area — instead of one monolith — because a team *maintains* this:
they re-run a single area after a refactor, assign `fable-review-02-authn-authz.md`
to whoever owns auth, and diff it next quarter. A 2,000-line single report rots on
first read; fifteen focused files stay useful.

## Bundled resources — read these before you fan out

- `scripts/recon.sh` — deterministic repo inventory (size, languages, module
  map, dependency manifests, tests, secret-ish files, churn hotspots). Run it
  first; it turns "how do I slice this?" from guesswork into data, for zero
  model tokens.
- `references/dimensions.md` — the four audit dimensions and the severity
  rubric. **This is the shared language.** Every area agent reviews its area
  across all four; paste the relevant parts into each brief so findings come
  back comparable.
- `references/agent-briefs.md` — fill-in templates for the area review agents
  and the verifier, plus the finding JSON schema.
- `references/output-templates.md` — the exact structure of the index file and
  the per-area files, plus naming and numbering rules.

---

## Workflow

### 1. Scope & recon

Confirm what "the codebase" means: the current repo by default; ask only if it's
ambiguous (monorepo with many apps, or the user gestures at "the backend"). Note
anything explicitly out of scope.

Record the baseline before you touch anything: capture the short commit SHA
(`git rev-parse --short HEAD`) and the current `git status`. The SHA stamps every
report file (readers need to know which revision was audited), and the clean
starting state is what lets you prove at the end that the audit changed nothing
under review but its own output.

Run recon to get the lay of the land:

```bash
bash <skill-path>/scripts/recon.sh <repo-path>
```

Read the output, then read a little yourself — the top-level README, an entry
point, the largest/churniest files recon flagged. You can't name *this codebase's*
review areas without understanding what the system actually is and does, so spend
ten real minutes here. This orientation is also where you notice the domain: is
there a tenants table? a `phi`/`hipaa` module? an LLM client? a payments service?
Those observations become areas in the next step.

### 2. Derive the review areas (Fable — this is what makes it *this codebase's* audit)

The organizing unit is the **review area**: a named theme that (a) genuinely
matters for *this* system and (b) an agent can review as a coherent unit. Each
area becomes one review agent and one output file, so choosing them well is the
whole game. Draw them from three wells and blend:

- **Domain & compliance surface** — what this software *is* and what rules bind
  it. This is where the high-signal, custom areas come from, the ones a generic
  checklist would never invent. Multi-tenant? → tenant isolation / data-scoping
  (RLS, every query filtered by tenant). Healthcare? → HIPAA / PHI handling.
  Handles money? → money handling, idempotency, ledger integrity. LLM/AI
  features? → the AI layer (prompt injection, unsafe tool/exec, trusting model
  output, cost/runaway). Read enough during recon to name these honestly.
- **Architecture** — the major components from the module map that deserve their
  own read: the web/BFF layer, each significant service, the data layer, the
  async/jobs/events machinery, inter-service boundaries.
- **Cross-cutting concerns** every serious system has — authn/authz, secrets &
  infra/config, input/API validation, data migrations & transactions,
  observability & resilience, testing, dependencies / supply-chain, and a
  conventions/consistency sweep.

Aim for **coverage without overlap**: every meaningful path lands in exactly one
area's remit, and areas don't re-audit each other's code (note a cross-area issue
in passing, don't chase it — the area that owns that code will catch it). Number
the areas and **order them by stakes** — domain- and security-critical areas
first, generic quality areas (testing, dependencies, conventions) last — so
`fable-review-01` is the thing to read first.

Size to the repo: a 5k-LOC service might be 6–8 areas; a large multi-service
monorepo, 15–25. Don't invent areas to pad the list, and don't fold two real
risks into one file to shrink it. If one area is too large for a single agent to
hold, you can still give it several review agents and merge their findings into
that one area file.

Show the user the numbered area list — the paths each covers and a rough
agent/model spend — before a large fan-out, unless they've said run straight
through. **The area list is the audit plan now**; it's their cost and their map,
so let them see it (and catch a domain area you missed) before you spend.

### 3. Fan out the review — one agent per area

Spawn the review agents with the Agent tool, `model: "sonnet"`, **in parallel**
(independent areas in a single message). Build each brief from the templates in
`agent-briefs.md`, pasting in:

- the area's name and its exact scope (paths to review, and the concern to trace
  if it's a cross-cutting area), and what's out of scope,
- the four dimension sections + severity rubric + the finding bar from
  `dimensions.md` (verbatim — don't paraphrase the rubric, or severities drift),
- the finding JSON schema, and the stop conditions.

The dimensions are the **lens** each agent applies; the area is the **unit** it
covers. Demand structured JSON back, not prose — you're going to merge and route
these, and prose doesn't merge. Ask for evidence (quoted lines, file:line),
because the verifier is going to reopen every serious claim.

### 4. Triage, dedup & route (Fable)

Collect the JSON. Before spending verification budget:

- **Dedup** — the same root cause often surfaces from multiple areas (a shared
  helper used everywhere). Collapse into one finding, file it in the area it most
  belongs to, and cross-reference it from the others; note the count, since "this
  appears in 14 handlers" is itself the signal.
- **Route** — assign every surviving finding to its **home area** (the file it
  will live in). Most are obvious; when a finding straddles two areas, put it
  where a reader would look for it and mention it from the other.
- **Prioritize verification** — every Critical/High must be verified. Verify
  Mediums where cheap; accept well-evidenced Lows as-is, marked lower-confidence.

### 5. Adversarial verification

Spawn verifier agents (Brief B, `model: "sonnet"`; escalate the subtle ones to
`"opus"`). Their job is to **refute** — reopen the cited code, check the failure
scenario is real and reachable, check the severity is honest. Batch related
findings per verifier.

Then apply the verdicts yourself — and don't outsource the final call. Treat
subagent reports (reviewers *and* verifiers) as leads, not verdicts: the cheap
models did the token-heavy reading, but the judgment is yours, so for anything
you're about to stamp Critical/High, reopen the file and confirm it with your own
eyes. Drop REJECTED findings (or move to an "investigated, not
confirmed" note if instructive). Apply ADJUST corrections. Keep CONFIRMED.

### 6. System-level synthesis (Fable — the part only you can do)

Now step back from the finding list to the system. The per-area agents can't see
this; you can, because you hold the whole picture:

- Where are the architectural seams clean, and where have they eroded?
- Which concerns are handled inconsistently *across* areas (three auth patterns,
  two HTTP clients)?
- Where does churn (from recon) meet complexity — where is the next bug being
  born?
- How much of the risky code actually has a test safety net?

This becomes the spine of the index file. A linter produces finding lists; the
whole-codebase architectural read is what makes this audit worth running.

### 7. Write the collection

Create `docs/review/fable/` at the repo root and write the files per
`references/output-templates.md`:

- **One `fable-review-NN-<slug>.md` per area.** An area that came back clean
  still gets its file, saying "reviewed, nothing material found" — silence has to
  be explicit, and the file is the placeholder the team keeps updating. Rank
  findings within each file by severity; tag each with its dimension.
- **`fable-review.md`** — the index: verdict, findings-at-a-glance table, the
  area map (each area → its file, finding counts, one-line health), the top risks
  (linking into the area files), and the system-level assessment.

Cross-link both ways: index → area files (and to specific findings via anchors),
area files → back to the index. Link every finding to `file:line` so it's one
click from the code. Lead with impact, not volume — three real Criticals beat
eighty Lows burying them.

If `docs/review/fable/` already holds a prior audit, you're refreshing it —
overwrite, and say so in your summary. Writing these report files is fine under
the read-only rule: that rule is about not changing the software under audit, and
`docs/review/fable/` is the audit's own output, not the software.

### 8. Report back

First confirm the read-only promise held: a `git status` should show only
`docs/review/fable/` added or changed — nothing under audit. If anything else
moved (a subagent that "just tried something"), say so plainly; a silent
violation is worse than an admitted one.

Then summarize for the user in chat: overall health, the top few risks, and point
them at `docs/review/fable/fable-review.md` as the entry point (mention how many
area files there are). Say how the audit was run — how many agents, what was
verified, what you couldn't reach. Be transparent about coverage and cost: they chose an
orchestrated audit to know where their money and their risk actually are.

---

## Guardrails

- **Read-only, always.** No edits, migrations, installs, or "quick fixes" to the
  audited software — by you or any subagent. Running read-only diagnostics
  (search, `git log`, a linter, a build to observe output) is fine. Writing the
  report files under `docs/review/fable/` and scratch notes is fine.
- **Areas from the code, not a template.** The value is a taxonomy that fits
  *this* repo. If your area list would look identical for a payments API and a
  game engine, you haven't read enough — go back to the domain surface.
- **Evidence or it doesn't ship.** Every finding cites `file:line` and a concrete
  failure scenario. "Error handling seems weak" is a theme for an area's summary,
  backed by located instances — not a standalone finding.
- **Severity honesty over drama.** Inflated severities are how a report loses the
  room. When two reviewers would disagree by a level, pick the lower and say why.
- **No silent gaps.** Whatever you sampled, skipped, or couldn't reach goes in
  the index's coverage section, and a clean area still gets its file. A blind spot
  presented as "clean" is worse than an admitted one.
- **Don't over-audit a molehill.** If the target is tiny or the user wants a
  quick once-over, collapse to a handful of areas and say you did — but keep the
  verifier pass. Match the machinery to the job.

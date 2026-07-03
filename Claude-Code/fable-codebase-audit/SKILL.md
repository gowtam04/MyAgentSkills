---
name: fable-codebase-audit
description: Run Claude Fable 5 as the orchestrator of a thorough, read-only audit of an entire codebase — security, correctness, architecture, and maintainability — by fanning out cheaper review subagents across the repo, adversarially verifying every serious finding, then synthesizing a severity-ranked Markdown report. Use this skill whenever the user asks Fable to "audit", "review the whole codebase", "do a code review of the repo", "find bugs/vulnerabilities/security issues across the project", "assess code quality / tech debt / architecture", "health check", or "what's wrong with this codebase" — especially on a Fable-powered session with a large repo. Also trigger when someone wants a comprehensive pre-release, pre-acquisition (due-diligence), or onboarding review of an unfamiliar codebase, even if they don't say the word "audit".
---

# Fable Codebase Audit

You (Claude Fable 5) are the orchestrator of a whole-codebase audit. Your value
here is judgment at scale: deciding how to carve up the repo, reading conflicting
subagent reports and deciding what's real, seeing the system-level patterns no
single file reveals, and writing a report an engineering team will actually act
on. The token-heavy reading is delegated; the thinking is yours.

This is a **read-only audit**. You and your subagents investigate and report —
nobody edits code, runs migrations, or "just fixes this one thing." The
deliverable is a `CODEBASE_AUDIT.md` report. If the user later wants fixes, that's
a separate, explicitly-authorized job (hand it to `fable-architect`).

## Why this shape

A naive "read every file and list problems" pass wastes your most expensive
tokens on mechanical scanning and still misses cross-cutting issues because no
single read holds the whole system in view. Instead:

- **Fan out** cheap review agents (Sonnet) over bounded slices — this is the
  reading-heavy work, and it parallelizes.
- **Verify adversarially** — a skeptic pass tries to *refute* each serious
  finding before it reaches the report. Unverified audits are noise; a report
  with three false Criticals gets the whole thing ignored.
- **Synthesize yourself** — dedup, rank, and write the architecture-level read
  that only a whole-repo view produces. This is the part worth paying Fable for.

## Bundled resources — read these before you fan out

- `scripts/recon.sh` — deterministic repo inventory (size, languages, module
  map, dependency manifests, tests, secret-ish files, churn hotspots). Run it
  first; it turns "how do I slice this?" from guesswork into data, for zero
  model tokens.
- `references/dimensions.md` — the four audit dimensions and the severity
  rubric. **This is the shared language.** Paste the relevant parts into every
  subagent brief so findings come back comparable.
- `references/agent-briefs.md` — fill-in templates for the review agents,
  cross-cutting agents, and the verifier, plus the finding JSON schema.
- `references/report-template.md` — the exact structure of `CODEBASE_AUDIT.md`.

---

## Workflow

### 1. Scope & recon

Confirm what "the codebase" means: the current repo by default; ask only if it's
ambiguous (monorepo with many apps, or the user gestures at "the backend"). Note
anything explicitly out of scope.

Run recon to get the lay of the land:

```bash
bash <skill-path>/scripts/recon.sh <repo-path>
```

Read the output, then read a little yourself — the top-level README, an entry
point, the largest/churniest files recon flagged. Your value over the cheap
agents starts with actually understanding the system, not just dispatching over
it. Ten minutes of orientation here makes every downstream brief sharper.

### 2. Plan the slices

Turn the module map into a concrete fan-out plan. Two kinds of agents:

- **Per-module review agents** — one per coherent slice from the module map.
  Keep each slice to something an agent can hold and reason about (~a few
  thousand LOC; split god-modules, group tiny sibling dirs). Each covers all
  four dimensions *within its files* — local context, focused findings.
- **Cross-cutting review agents** — a handful for risks that don't live in one
  module: security data-flow & secrets, dependency/supply-chain, architecture &
  coupling, and a consistency sweep. See Brief B in `agent-briefs.md`.

Size the fan-out to the repo. A 5k-LOC service might be 3 module agents + 2
cross-cutting; a 500k-LOC monorepo might be 20+ module agents plus cross-cutting
per app. Don't silently cap coverage — if you decide to sample or defer part of
the repo, that limitation goes in the report's "out of scope" section, not into
a blind spot. For a genuinely small repo (recon shows it fits comfortably in
context), it's fine to collapse to one or two agents — but still run the separate
verification pass; self-review without a skeptic is where false positives live.

Show the user the plan (slices, agent count, rough model spend) before a large
fan-out, unless they've said run straight through. This is their cost; let them
see it.

### 3. Fan out the review

Spawn the review agents with the Agent tool, `model: "sonnet"`, **in parallel**
(independent slices in a single message). Build each brief from the templates in
`agent-briefs.md`, pasting in:

- the exact scope (paths), and what's out of scope,
- the relevant dimension sections + severity rubric + the finding bar from
  `dimensions.md` (verbatim — don't paraphrase the rubric, or severities drift),
- the finding JSON schema, and the stop conditions.

Demand structured JSON back, not prose — you're going to merge many of these and
prose doesn't merge. Ask for evidence (quoted lines, file:line), because the
verifier is going to reopen every serious claim.

### 4. Triage & dedup (Fable)

Collect the JSON. Before spending verification budget:

- **Dedup** — the same root cause often surfaces from multiple agents (a shared
  helper used everywhere). Collapse into one finding listing all locations;
  note the count, since "this appears in 14 handlers" is itself the signal.
- **Cross-reference** — a finding tagged `maintainability` by one agent and
  `security` by another about the same code is one finding; pick the primary
  dimension.
- **Prioritize verification** — every Critical/High must be verified. Verify
  Mediums where cheap; you can accept well-evidenced Lows as-is and mark them
  lower-confidence.

### 5. Adversarial verification

Spawn verifier agents (Brief C, `model: "sonnet"`; escalate the subtle ones to
`"opus"`). Their job is to **refute** — reopen the cited code, check the failure
scenario is real and reachable, check the severity is honest. Batch related
findings per verifier.

Then apply the verdicts yourself — and don't outsource the final call. Per
`efficient-fable`, treat subagent reports (reviewers *and* verifiers) as leads:
for anything you're about to stamp Critical/High, reopen the file and confirm it
with your own eyes. Drop REJECTED findings (or move to an "investigated, not
confirmed" note if instructive). Apply ADJUST corrections. Keep CONFIRMED.

### 6. System-level synthesis (Fable — the part only you can do)

Now step back from the finding list to the system. The per-file agents can't see
this; you can, because you hold the whole picture:

- Where are the architectural seams clean, and where have they eroded?
- Which concerns are handled inconsistently across the repo?
- Where does churn (from recon) meet complexity — where is the next bug being
  born?
- How much of the risky code actually has a test safety net?

This section is the report's spine. A linter produces finding lists; the
whole-codebase architectural read is what makes this audit worth running.

### 7. Write the report

Write `CODEBASE_AUDIT.md` at the repo root (or the user's chosen path) following
`references/report-template.md` exactly. Order it for a busy reader: verdict and
top risks first, exhaustive findings below, method and blind spots in an
appendix. Link every finding to `file:line`. Lead with impact, not volume —
three real Criticals beat eighty Lows burying them.

You may write this file yourself: it's a planning/analysis artifact, not code, so
the read-only rule doesn't apply to it (that rule is about not changing the
software under audit).

### 8. Report back

Summarize for the user in chat: overall health, the top few risks, where the
report lives, and how the audit was run (how many agents, what was verified, what
you couldn't reach). Be transparent about coverage and cost — they chose an
orchestrated audit to know where their money and their risk actually are.

---

## Guardrails

- **Read-only, always.** No edits, migrations, installs, or "quick fixes" to the
  audited software — by you or any subagent. Running read-only diagnostics
  (search, `git log`, a linter, a build to observe output) is fine. Writing the
  report and scratch notes is fine.
- **Evidence or it doesn't ship.** Every finding cites `file:line` and a concrete
  failure scenario. "Error handling seems weak" is a theme for the summary,
  backed by located instances — not a standalone finding.
- **Severity honesty over drama.** Inflated severities are how a report loses the
  room. When two reviewers would disagree by a level, pick the lower and say why.
- **No silent gaps.** Whatever you sampled, skipped, or couldn't reach goes in
  the report's out-of-scope section. A blind spot presented as "clean" is worse
  than an admitted one.
- **Don't over-audit a molehill.** If the target is tiny or the user wants a
  quick once-over, collapse the fan-out and say you did — but keep the verifier
  pass. Match the machinery to the job.

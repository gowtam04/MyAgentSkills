# Delegation briefs

Copy-and-fill templates for the subagents Fable spawns. The governing idea
(from `efficient-fable`): the cheap models do the token-heavy reading; Fable
keeps the judgment — slicing, resolving conflicts, verifying, and writing the
report.

Each subagent starts with **no memory of this conversation**. The brief carries
everything: scope, the rubric, the output contract, and the stop conditions. A
vague brief produces vague findings you then have to re-derive — which defeats
the delegation.

Model choice, by default:
- **Review agents** (per-module + cross-cutting): **Sonnet**. Scanning a bounded
  set of files against a checklist is well-specified work.
- **Verification agents:** **Sonnet** for most; escalate a specific finding to
  **Opus** when confirming it needs real reasoning (subtle concurrency, a
  cross-file exploit chain) rather than just rereading the cited lines.
- Never spawn implementation/fix agents from this skill — it's read-only.

Always return findings as **structured JSON** so Fable can merge slices without
parsing prose. Schema at the bottom.

---

## Brief A — per-module review agent

Spawn one per slice from the recon module map. Keep each slice to a coherent set
of files a single agent can hold and reason about (roughly a few thousand LOC;
split larger modules).

```
You are a code auditor. Review ONLY the code in scope below and report defects.
This is a READ-ONLY audit — do not edit, run, or fix anything. Read and analyze.

Repo: <abs path>
Scope (review these, and follow calls into them): <dir/files, e.g. src/auth/**>
Out of scope: everything else (other agents cover it) — note cross-boundary
  issues briefly but don't chase them.

Review across all four dimensions using this rubric verbatim:
<paste the four dimension sections + the severity rubric + "what makes a finding
 worth reporting" from references/dimensions.md>

Method:
- Trace untrusted input from entry points to sinks within scope.
- For each risky spot, ask: what input/state makes this misbehave, and how?
- Prefer a few well-evidenced, located findings over a long shallow list.
- Every finding needs file:line, a concrete failure scenario, evidence (quote
  the lines), a recommended direction, and an honest confidence.

Stop conditions — stop and report what you have if: the scope doesn't exist,
you'd need to edit code to proceed, or a file is generated/vendored (skip it,
note that you did).

Return ONLY JSON matching this schema: <paste schema>. No prose outside the JSON.
```

## Brief B — cross-cutting review agents

Some risks don't live in one module. Spawn a small set of these to cover what
per-module slicing misses. Same output contract as Brief A, but scope is a
concern spanning the whole repo:

- **Security data-flow & secrets** — trace auth/authz and untrusted input across
  module boundaries; scan for committed secrets and unsafe config (use the recon
  "secret-ish files" and manifest lists as leads).
- **Dependency & supply chain** — read the manifests/lockfiles recon found;
  flag known-vulnerable, unmaintained, or suspiciously-named packages and
  lockfile/version drift.
- **Architecture & coupling** — build the module dependency picture; find
  circular deps, layering violations, god files, and churn×complexity hotspots.
- **Consistency sweep** — find concerns implemented N different ways (auth,
  error handling, validation, logging, config) across the codebase.

```
You are auditing ONE cross-cutting concern across an entire repository.
READ-ONLY — analyze, don't modify.

Repo: <abs path>
Concern: <e.g. "authentication & authorization data flow">
Leads from recon: <paste relevant recon lines — manifests, hotspots, entry pts>

<paste the relevant dimension section(s) + severity rubric + finding bar>

Cast wide but report only located, evidenced findings. Group repeated instances
of one root cause into a single finding listing all locations.

Return ONLY JSON matching this schema: <schema>.
```

## Brief C — adversarial verification agent

Runs after review, before anything lands in the report. Its job is to **refute**,
not to agree — this is what keeps false positives out. Batch a handful of related
findings per agent, or give one agent the high-severity ones.

```
You are a skeptical senior reviewer verifying audit findings. For EACH finding,
your default posture is doubt: try to prove it WRONG. READ-ONLY.

Repo: <abs path>
Findings to verify: <JSON array of candidate findings>

For each finding:
1. Open the cited file:line yourself. Does the code actually say what the finding
   claims? (Reject if misquoted or the line moved.)
2. Is the failure scenario real and reachable, or is there a guard/caller/
   framework behavior the reviewer missed that prevents it?
3. Is the severity honest given real impact and likelihood?

Verdict per finding: CONFIRMED (real, severity right), ADJUST (real but severity/
scope wrong — give corrected values), or REJECTED (not a real defect — say why).
Prefer REJECTED when genuinely uncertain; a shipped false positive costs more
than a caught miss here.

Return ONLY JSON: array of {id, verdict, corrected_severity?, corrected_scope?,
reason, evidence}.
```

---

## Finding JSON schema

Every review agent returns:

```json
{
  "findings": [
    {
      "id": "SEC-01",
      "title": "SQL injection in user search",
      "dimension": "security",
      "severity": "Critical",
      "location": "src/api/search.js:42",
      "related_locations": ["src/api/search.js:88"],
      "whats_wrong": "User `q` param is concatenated into the SQL string.",
      "how_it_fails": "GET /search?q=' OR '1'='1 returns all rows; UNION extracts other tables.",
      "why_it_matters": "Unauthenticated full-database read.",
      "recommendation": "Use parameterized queries / the driver's bind API.",
      "evidence": "const sql = `SELECT * FROM users WHERE name LIKE '%${q}%'`",
      "confidence": "high",
      "also_relates_to": "correctness"
    }
  ],
  "notes": "Anything the reviewer couldn't reach, or scope that didn't exist."
}
```

Ids are provisional out of the review agents; Fable renumbers per dimension
(`SEC-01`, `COR-01`, ...) during synthesis after dedup and verification.

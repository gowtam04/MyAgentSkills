# Delegation briefs

Copy-and-fill templates for the subagents Fable spawns. The governing idea: the
cheap models do the token-heavy reading; Fable keeps the judgment — slicing,
resolving conflicts, verifying, and writing the report.

Each subagent starts with **no memory of this conversation**. The brief carries
everything: scope, the rubric, the output contract, and the stop conditions. A
vague brief produces vague findings you then have to re-derive — which defeats
the delegation.

Model choice, by default:
- **Area review agents:** **Sonnet**. Reviewing a bounded area against a rubric
  is well-specified work.
- **Verification agents:** **Sonnet** for most; escalate a specific finding to
  **Opus** when confirming it needs real reasoning (subtle concurrency, a
  cross-file exploit chain) rather than just rereading the cited lines.
- Never spawn implementation/fix agents from this skill — it's read-only.

Always return findings as **structured JSON** so Fable can merge and route them
without parsing prose. Schema at the bottom.

One review agent per **review area** (the areas Fable derived in step 2). An area
is one of two shapes; pick the brief flavor that matches:

- **Module-shaped** — the area is a bounded set of files (a service, the data
  layer, the web/BFF). Scope it by paths.
- **Concern-shaped** — the area is a thread that runs across the repo (tenant
  isolation, authn/authz, secrets, HIPAA/PHI handling, the AI layer, migrations,
  observability, dependencies, consistency). Scope it by *what to trace*, with
  the recon leads (entry points, manifests, hotspots) as starting points.

Both use the same rubric, the same JSON contract, and the same read-only stance —
only the "what's in scope" line differs. Fill Brief A with the flavor that fits.

---

## Brief A — area review agent

Spawn one per area. Keep each area to what a single agent can hold and reason
about (roughly a few thousand LOC of relevant code); if a real area is bigger,
give it several agents and merge their findings into the one area file.

```
You are a code auditor reviewing ONE area of a larger codebase, and reporting
defects. This is a READ-ONLY audit — do not edit, run, or fix anything. Read
and analyze.

Repo: <abs path>
Area: <the area name, e.g. "Tenant isolation & RLS" or "AI layer">
Scope — review these and follow calls into them:
  <for a module-shaped area: the paths, e.g. src/db/**, src/tenancy/**>
  <for a concern-shaped area: what to trace, e.g. "every DB query path — confirm
   each is scoped to the caller's tenant; start from src/db/query.ts and the
   models in src/models/**". Include the recon leads.>
Out of scope: everything else (other agents own it) — note a cross-area issue
  briefly if you spot one, but don't chase it.

Review across all four dimensions using this rubric verbatim:
<paste the four dimension sections + the severity rubric + "what makes a finding
 worth reporting" from references/dimensions.md>

Method:
- Trace untrusted input from entry points to sinks within your area.
- For each risky spot, ask: what input/state makes this misbehave, and how?
- Prefer a few well-evidenced, located findings over a long shallow list.
- Group repeated instances of one root cause into a single finding listing all
  locations.
- Every finding needs file:line, a concrete failure scenario, evidence (quote
  the lines), a recommended direction, and an honest confidence.

Stop conditions — stop and report what you have if: the scope doesn't exist,
you'd need to edit code to proceed, or a file is generated/vendored (skip it,
note that you did).

Return ONLY JSON matching this schema: <paste schema>. No prose outside the JSON.
```

## Brief B — adversarial verification agent

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

Ids are provisional out of the review agents. During synthesis — after dedup,
routing, and verification — Fable assigns each finding to its home area file and
gives it a stable id there (`SEC-01`, `RLS-01`, …) that the index and other files
can link to.

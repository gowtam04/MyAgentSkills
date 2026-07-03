# Audit dimensions & severity rubric

This is the shared rubric every review and verification agent works from. Hand
the relevant slice of it to each subagent so findings come back in one language
and one severity scale — otherwise synthesis turns into translation.

The four dimensions overlap on purpose (a missing auth check is both a security
hole and a correctness bug). Tag the finding with its *primary* dimension and
mention the secondary one in the finding body rather than filing it twice.

---

## Severity rubric (use these exact labels)

Severity is about **impact × likelihood**, not how easy the fix is. A one-line
fix for a bug that silently corrupts payments is still Critical.

- **Critical** — Exploitable or actively harmful now: remote code execution,
  auth bypass, secret leakage, data loss/corruption, money handled wrong. A
  reasonable attacker or a normal user hitting a common path triggers it.
- **High** — Serious bug or vulnerability that will bite under realistic
  conditions: injection reachable behind a login, a race that corrupts state
  under normal concurrency, unhandled errors on a core flow.
- **Medium** — Real defect or risk with meaningful but bounded blast radius, or
  reachable only in narrower conditions: missing validation on a secondary
  path, resource leak under load, fragile design that will break the next time
  someone touches it.
- **Low** — Minor correctness/quality issue, localized and low-impact: sloppy
  error message, small edge case, mild inefficiency.
- **Info** — Not a defect. Observations, style notes, and suggestions worth the
  reader's attention but requiring no action to ship safely.

If two reviewers would plausibly disagree by one level, pick the lower and say
why in the body. Over-inflated severity destroys the report's credibility faster
than a missed Low.

---

## 1. Security & vulnerabilities  (tag: `security`)

Think like an attacker with the source in hand. Trace untrusted input from entry
point to sink.

- **Injection** — SQL/NoSQL, command, LDAP, template, path traversal, SSRF.
  Follow user input into query builders, `exec`/`system`, file paths, URLs.
- **AuthN / AuthZ** — Missing or inconsistent authentication; broken access
  control (can user A act on user B's object?); privilege escalation; IDOR;
  tokens without expiry or verification.
- **Secrets & config** — Hardcoded credentials, API keys, private keys in
  source or committed config; secrets in logs; debug/permissive flags left on.
- **Crypto & data protection** — Weak/legacy algorithms, homemade crypto, static
  IVs/salts, sensitive data unencrypted at rest or in transit, PII in logs.
- **Input handling** — Missing validation, unsafe deserialization, XXE, mass
  assignment, unbounded input causing DoS.
- **Web** — XSS (stored/reflected/DOM), CSRF, open redirect, clickjacking,
  insecure CORS, missing security headers, cookie flags.
- **Dependencies** — Known-vulnerable or unmaintained packages, typosquat-shaped
  names, lockfile drift, install scripts pulling from untrusted sources.

## 2. Correctness & bugs  (tag: `correctness`)

Where does the code do something other than what it clearly intends?

- **Logic errors** — Off-by-one, inverted conditions, wrong operator, wrong
  default, copy-paste that forgot to change a variable.
- **Edge cases** — Empty/null/zero/negative, unicode, very large inputs,
  boundary values, timezone/locale, integer overflow, floating-point money.
- **Error handling** — Swallowed exceptions, errors logged then ignored, bare
  catches, failure paths that leave state half-updated, missing rollback.
- **Concurrency** — Races, unguarded shared mutable state, deadlock, check-then-
  act (TOCTOU), non-atomic read-modify-write, async ordering assumptions.
- **Resource handling** — Leaked files/sockets/connections/locks, missing
  cleanup on the error path, unbounded caches/queues.
- **Contract violations** — API/function used against its documented contract,
  nullable treated as non-null, return values ignored, type coercion surprises.
- **State & data integrity** — Invariants that can be violated, missing
  transactions across writes that must be atomic, cache/store divergence.

## 3. Architecture & design  (tag: `architecture`)

Zoom out from lines to structure. This is the dimension where Fable's own
judgment matters most — reserve the synthesis here for yourself.

- **Boundaries & coupling** — Modules reaching into each other's internals,
  circular dependencies, business logic bleeding into controllers/UI/DB layer,
  no clear seam between domains.
- **Cohesion** — God objects/files, grab-bag "utils", one class doing five jobs.
- **Layering & dependency direction** — Dependencies pointing the wrong way,
  domain logic depending on frameworks/infrastructure.
- **Scalability & performance shape** — N+1 queries, synchronous work that
  should be async, per-request work that should be cached/batched, chatty
  service calls, unbounded in-memory growth, single points of failure.
- **Data model** — Schema that fights the domain, missing indices on hot paths,
  denormalization without a reason, nullable columns hiding states.
- **Consistency** — Multiple ways to do the same thing, competing patterns for
  the same concern (three HTTP clients, two auth schemes), config sprawl.
- **Tech-debt hotspots** — Cross-reference churn hotspots from recon with high
  complexity: files that change often *and* are large/tangled are where the next
  bug will be born. Call these out explicitly.

## 4. Maintainability & quality  (tag: `maintainability`)

Would a new engineer be productive and safe here in a week?

- **Readability** — Misleading names, dense un-obvious logic with no comment on
  the *why*, inconsistent style that the tooling doesn't catch.
- **Duplication** — Copy-pasted logic that will drift; the same bug waiting to be
  fixed in three places.
- **Testing** — Untested critical paths, tests asserting nothing, flaky/skipped
  tests, no tests around the exact code the other dimensions flagged as risky.
- **Dead & speculative code** — Unreachable branches, commented-out blocks,
  unused exports, abandoned feature flags, "we might need it" abstractions.
- **Documentation** — Missing/outdated READMEs and runbooks, no setup steps,
  public APIs without contracts, stale comments that contradict the code.
- **Observability & operability** — No logging where you'd need it to debug prod,
  no metrics on critical flows, secrets-leaking or useless log lines.
- **Error ergonomics** — Failures that surface as unactionable messages; nothing
  to tell an on-call engineer what to do.

---

## What makes a finding worth reporting

Every finding must clear this bar — it's what the verification pass checks:

1. **Specific location** — `path/to/file.ext:line` (or a tight range). "Error
   handling is weak across the app" is not a finding; it's a theme for the
   summary. Back a theme with 2-3 concrete located instances.
2. **Concrete failure scenario** — the inputs/state/sequence that make it go
   wrong, and what goes wrong. If you can't name how it fails, it's an `Info`.
3. **Evidence, not assertion** — quote the offending line(s) or name the missing
   guard. The verifier will reopen the file; the finding must survive that.
4. **A recommended direction** — what to do instead, at the level of a senior
   reviewer's comment. This audit is read-only, so describe the fix; don't apply
   it.
5. **Honest confidence** — `high` / `medium` / `low`. Low-confidence findings are
   allowed but must say what would confirm or kill them.

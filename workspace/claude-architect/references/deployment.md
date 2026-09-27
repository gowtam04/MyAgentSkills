# Deployment, Infrastructure, and Commands

Read this when you reach the Deployment & Infrastructure part of system design. Re-read the budget
tier first: it's a constraint, not a suggestion. If you're recommending managed Kafka on a hobby
tier or a single $5 VM on enterprise, stop and pick again.

## Contents
- [Infrastructure checklist](#infrastructure-checklist)
- [Cost estimate](#cost-estimate)
- [Pinned commands](#pinned-commands)
- [The smoke command](#the-smoke-command)

## Infrastructure checklist

Cover each concern that applies; say explicitly when one doesn't — silence on "where does it run"
is a gap, not a default.

| Concern | Hobby / prototype | Startup / lean | Scaling / growth | Enterprise |
|---|---|---|---|---|
| Hosting / runtime | Free-tier PaaS or serverless, one small VM | Entry PaaS tier (Render, Fly.io, Railway), Cloud Run | Container platform, autoscaling | Multi-region, K8s if the org runs it |
| Database | SQLite on disk, free managed Postgres (Neon, Supabase) | Paid entry managed Postgres | Managed Postgres with replicas, PITR | HA multi-AZ, compliance-scoped |
| Background jobs | Inline, or in-process worker | DB-backed queue (pg-boss) or managed Redis + worker | SQS / Cloud Tasks | Event bus (Kafka, EventBridge) only if replay/fan-out is required |
| Object storage | Local disk | S3 / R2 / GCS standard | CDN-fronted | Replicated, lifecycle policies |
| Caching | None | In-process LRU | Managed Redis | Managed Redis cluster |
| Observability | Structured stdout logs | Logs-as-a-service ($0–50/mo) | APM starter | Full APM, tracing, alerting |
| Secrets | Host env vars | Platform secret store | Parameter/Secret Manager | Secrets manager with rotation, Vault |
| Environments | Prod only | Prod + staging | Prod + staging + PR previews | Full dev/staging/prod with gates |

Add caching only when a requirement demands it. On hobby and startup tiers, "not having it yet"
is often the right answer — say so and name the trigger for adding it later.

For AI/LLM features, `agent-features.md` has the equivalent ladder for vector stores, queues,
tracing and model spend.

## Cost estimate

Close the section with a rough monthly bucket: **$0, ~$50, ~$500, ~$5k, $50k+**. The point is that
the user sees the bill before the build starts. If the bucket doesn't match the tier they picked,
the design is wrong — revisit it. Enterprise tier still gets the estimate; it just doesn't drive
the choices.

## Pinned commands

Record the exact commands in the deployment doc (the source of truth) and mirror them in the
Build Manifest's `commands` block. `claude-build` hands these to its test-runners verbatim — a
runner that has to guess a command wastes a round and sometimes runs the wrong thing.

| Command | Purpose |
|---|---|
| `install` | Install dependencies (optional if obvious) |
| `test` | Full test suite |
| `test_one` | Run specific test files — use `{files}` as the placeholder for space-separated paths |
| `typecheck` | Type check, or `none` for untyped stacks |
| `lint` | Optional |
| `build` | Production build |
| `smoke` | Agent-checkable proof the app runs (below) |
| `run` | Optional: start it for manual use |

For greenfield work, write the intended commands and mark any that depend on scaffolding as
`TBD — set in scaffold`; the scaffold phase must then create and pin them.

## The smoke command

Unit tests can all pass while the assembled app doesn't start, a route isn't mounted, or a page
throws on load. The smoke command catches that without a human. It:

- starts the app (or uses a test build),
- exercises a few real paths end-to-end,
- exits non-zero on any failure,
- finishes in under a couple of minutes,
- leaves evidence where it helps (screenshots, response bodies) under `tmp/smoke/`.

By app type:

- **Web UI:** a Playwright script that starts the dev/preview server, loads the key pages, checks
  for a known element on each and no console errors, and saves screenshots to `tmp/smoke/`.
  Reviewers and integration testers can look at the screenshots.
- **HTTP API:** a script that starts the server against a test database, curls a health endpoint
  and one or two real endpoints, and checks status codes and a field in the body.
- **CLI:** runs a real command against a fixture directory and diffs the output against an
  expected file.
- **Library:** an example consumer script that imports the public API and exercises it.
- **Worker / job:** enqueues a job against a local queue and asserts the side effect.

The scaffold phase creates the smoke runner with one trivial check. Make the runner discover
checks from a folder (for example `smoke/checks/*.mjs` or `tests/smoke/test_*.py`) so each later
phase adds its own check file rather than editing the runner — otherwise the smoke script becomes
a hub file that serializes every phase.

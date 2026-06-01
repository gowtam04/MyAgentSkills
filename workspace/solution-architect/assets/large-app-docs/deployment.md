# {Project Name} — Deployment & Infrastructure

Budget Tier: hobby | startup | scaling | enterprise  ← restate from `overview.md`; every choice below must respect this tier
Backend Topology: monolith | modular-monolith | microservices | serverless | hybrid  ← restate; drives how the runtime section is structured

## Hosting / Runtime
Where the app(s) actually run. For microservices or hybrid topologies, list each service and its runtime separately.

- Choice: {single VM (Hetzner/DO/Linode) | PaaS (Render/Fly.io/Railway/Heroku) | container platform (ECS/Cloud Run/App Runner) | Kubernetes | serverless platform}
- Why it fits this tier: {one line}
- Region(s) and redundancy: {single region / multi-AZ / multi-region — only step up when the tier and the requirements justify it}

## Database Hosting
- Primary datastore choice: {SQLite-on-disk | managed Postgres free tier (Neon/Supabase) | managed Postgres paid tier (RDS/Cloud SQL/Aiven) | self-hosted on same VM | multi-AZ HA setup}
- Replication / backup strategy
- Why it fits this tier

## Background Jobs / Queues *(omit if not needed)*
- Choice: {in-process worker | pg-boss / DB-backed | managed Redis + worker | SQS / Cloud Tasks | event bus (Kafka, EventBridge)}
- Expected job volume and latency budget
- Why it fits this tier

## Object Storage *(omit if not needed)*
- Choice: {local disk | S3 / R2 / GCS | CDN-fronted}
- Access pattern (write-once-read-many vs hot read path)

## Caching *(omit unless a real requirement)*
- Choice and the requirement that demands it. Don't add caching as nice-to-have.

## Observability
- Logs: {structured stdout | logs-as-a-service (Logflare/Axiom/Better Stack) | full APM (Datadog/Honeycomb/New Relic)}
- Metrics: {platform-native | dedicated metrics vendor}
- Tracing: {none | OpenTelemetry to a backend}
- Alerting: {none | platform-native | dedicated}
- Why it fits this tier — default to the cheapest rung that meets the requirement

## Secrets Management
- Choice: {env vars from host | platform-built-in secret store | dedicated secrets manager (AWS Secrets Manager / Vault)}
- Rotation policy (if any)

## Environments
- Set: {just-prod | prod + dev/staging | dev + staging + prod + PR previews}
- Promotion / deploy flow

## CI / CD *(if relevant)*
- Pipeline shape, where it runs, what gates exist before prod

## Cost Estimate

Rough monthly cost in order-of-magnitude buckets. Per concern + a total:

| Concern | Monthly cost |
|---|---|
| Hosting / runtime | $ |
| Database | $ |
| Jobs / queue | $ |
| Storage | $ |
| Observability | $ |
| Secrets | $ |
| Other (LLM API, CDN, etc.) | $ |
| **Total** | **$** |

If the total doesn't match the budget tier on the first line, revisit. The point of this document isn't to show off the most capable stack — it's to architect a deployment the user can actually afford to run.

## Scaling Plan *(scaling / enterprise tiers only)*
- What scales first under load
- Where the next bottleneck is
- What architectural changes (read replicas, sharding, CDN, queue, splitting a service) come next, and at roughly what traffic level

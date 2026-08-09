# Deployment & Infrastructure

Budget Tier: [hobby | startup | scaling | enterprise] — every choice below must be right-sized for this tier.

For each concern: state the **choice**, a one-line **why this fits the tier**, and any **ops notes**.

## Hosting / Runtime

- Choice:
- Why it fits the tier:
- Notes:

## Database Hosting

- Choice:
- Why it fits the tier:
- Backup / retention notes:

## Background Jobs / Queues

- Choice: none | in-process | DB-backed | managed queue | event bus
- Why it fits the tier:
- Notes:

## Object Storage

- Choice: none | local | S3-equivalent | CDN-fronted
- Why it fits the tier:

## Caching

- Choice: none | in-process | Redis | managed cache
- Why it fits the tier:

## Observability

- Choice: stdout logs | logs-as-a-service | full APM
- Why it fits the tier:

## Secrets Management

- Choice: env vars | platform secrets | dedicated secrets manager
- Why it fits the tier:

## Environments & CI/CD

- Environments: just-prod | prod+staging | dev/staging/prod
- CI checks: test / typecheck / lint / build
- Deploy mechanism:

## Rough Monthly Cost Estimate

Bucket: **$0 / $50 / $500 / $5k / $50k+**

Breakdown (order of magnitude only):

| Item | ~$/mo |
|------|-------|
| Compute | |
| Database | |
| Other | |
| **Total bucket** | |

If the estimate does not fit the declared budget tier, revise the architecture.

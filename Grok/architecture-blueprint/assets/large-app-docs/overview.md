# {Project Name} - Architecture Overview

Mode: PM | Developer  - pick one; this line helps `/build-orchestrator` tune subagent prompts and todo scaffolding
Budget Tier: hobby | startup | scaling | enterprise  - from Phase 1; gates every infra recommendation in `deployment.md`
Backend Topology: monolith | modular-monolith | microservices | serverless | hybrid  - drives how implementation phases are sliced

## Vision

What's being built and why, in a few sentences. Trace to requirements goals.

## Requirements Reference

Path(s) to the business requirements this architecture is based on:

- `[path]`

## Tech Stack

Languages, frameworks, datastores, key libraries. (Deployment infra lives in `deployment.md`.)

| Layer | Choice | Why |
|-------|--------|-----|
| Language / runtime | | |
| Web / API framework | | |
| Data store | | |
| Auth | | |
| Frontend (if any) | | |
| Other | | |

For brownfield: list established stack; call out only additions.

## High-Level System Diagram

Describe major pieces and how they connect. For non-monolith topologies, show service/module boundaries explicitly.

Example shape:

```text
[Client] -> [API / BFF] -> [Domain services] -> [DB]
                |                |
                v                v
           [Auth]          [External provider]
```

## Design System / UI Reference (if UI)

- Path if present: `/docs/design-system/...` or "follow existing app patterns + architecture UI notes"
- Do not invent a full visual system in architecture docs unless required by requirements.

## Document Map

- `data-model.md` - entities, relationships, ERD, migrations
- `component-design.md` - component breakdown, interfaces, dependencies
- `api-design.md` - endpoints, request/response shapes, auth, errors
- `implementation-plan.md` - phased build plan with file ownership, integration checkpoints, and Build Manifest
- `decisions.md` - Architecture Decision Records (ADRs)
- `deployment.md` - hosting, datastore, jobs, storage, observability, secrets, environments, cost estimate
- `conventions.md` - *(Developer mode only)* naming, error handling, logging, transactions
- `testing-strategy.md` - *(Developer mode only)* framework, unit/integration split, mocking, coverage

# {Project Name} — Architecture Overview

Mode: PM | Developer  ← pick one; this line is how `dev-team` detects the mode
Budget Tier: hobby | startup | scaling | enterprise  ← from Phase 1; gates every infra recommendation in `deployment.md`
Backend Topology: monolith | modular-monolith | microservices | serverless | hybrid  ← from Phase 2.5; drives how implementation phases are sliced

## Vision
What's being built and why, in a few sentences.

## Requirements Reference
Path(s) to the business requirements this architecture is based on.
(If an `agent-design/` directory informed this design, list its path here too.)

## Tech Stack
Languages, frameworks, datastores, key libraries. (Deployment infra lives in `deployment.md`.)

## High-Level System Diagram
A diagram or description of the major pieces and how they connect. For non-monolith topologies, show the service/module boundaries explicitly.

## Document Map
- `data-model.md` — entities, relationships, ERD
- `component-design.md` — component breakdown, interfaces, dependencies
- `api-design.md` — endpoints, request/response shapes, auth, errors
- `implementation-plan.md` — phased build plan with file ownership, integration checkpoints, and the Build Manifest (machine-readable appendix for autonomous builders)
- `decisions.md` — Architecture Decision Records (ADRs)
- `deployment.md` — hosting, datastore, jobs, storage, observability, secrets, environments, cost estimate
- `conventions.md` — *(Developer mode only)* naming, error handling, logging, transactions
- `testing-strategy.md` — *(Developer mode only)* framework, unit/integration split, mocking, coverage

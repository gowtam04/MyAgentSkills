# {Project Name} — Architecture Overview

Mode: PM | Developer  ← pick one; claude-build reads this line
Budget Tier: hobby | startup | scaling | enterprise  ← gates every choice in `deployment.md`
Backend Topology: monolith | modular-monolith | microservices | serverless | hybrid

## Vision
What's being built and why, in a few sentences.

## Requirements Reference
Path(s) to the requirements this architecture was designed from, e.g. `docs/requirements/`.

## Tech Stack
Languages, frameworks, datastores, key libraries — and, for an existing codebase, what's new.

## High-Level System Diagram
The major pieces and how they connect. For non-monolith topologies, show service or module
boundaries explicitly.

## Design System
Path to `docs/design-system/design-system.md` if one exists; otherwise "none".

## Document Map
- `data-model.md` — entities, relationships, constraints, migrations
- `api-design.md` — endpoints, shapes, auth, errors
- `component-design.md` — components, file structure (ownership map), interfaces
- `implementation-plan.md` — phases, integration checkpoints, Parallel Waves, Build Manifest
- `decisions.md` — Architecture Decision Records; unresolved items
- `deployment.md` — infrastructure, pinned commands (incl. smoke), cost estimate
- `conventions.md` — *(Developer mode only)*
- `testing-strategy.md` — *(Developer mode only)*

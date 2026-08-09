# Pipeline Contract

Shared expectations across `product-discovery` → `architecture-blueprint` → `build-orchestrator`.

## Stage boundaries

| Stage | Skill | Owns | Does not own |
|-------|--------|------|----------------|
| Discovery | `product-discovery` / `/product-discovery` | WHAT / WHY, personas, workflows, rules, acceptance criteria, constraints | Frameworks, schemas, APIs, infra, code |
| Architecture | `architecture-blueprint` / `/architecture-blueprint` | HOW: stack, data model, components, interfaces, phases, ownership map, deployment | Product intent inventing, application code |
| Build | `build-orchestrator` / `/build-orchestrator` | Coordinated implementation from approved architecture | Redesigning architecture or product |

## Doc paths

| Kind | Requirements | Architecture | Progress |
|------|--------------|--------------|----------|
| Feature in existing project | `/docs/features/{name}/requirements/` | `/docs/features/{name}/architecture/` | `/docs/features/{name}/progress/` |
| New application | `/docs/requirements/` | `/docs/architecture/` | `/docs/progress/` |

## What discovery must leave for architecture

- Specific capabilities and business rules (not vague feature names)
- Personas and primary workflows with acceptance criteria
- Non-functional expectations in user terms
- Constraints and out-of-scope
- Open questions honestly listed

## What architecture must leave for build

- Mode line: `Mode: PM | Developer`
- Budget tier: `Budget Tier: hobby | startup | scaling | enterprise`
- Complete file structure with purpose per file (ownership map)
- Implementation phases with depends-on, produces, parallel opportunities, test focus
- Interface contracts scaled to risk
- Requirements reference path(s)

## Skip paths

- Discovery optional when the user already has architecture-ready requirements.
- Architecture optional only for trivial one-file changes the user wants coded immediately (orchestrator should still stop if multi-file ownership is unclear).
- Design system docs under `/docs/design-system/` are optional; if present, architecture and build should reference them for UI work. Do not invoke a separate frontend-design skill.

## Handoff phrases

- After discovery: next is `/architecture-blueprint` (skill: `architecture-blueprint`).
- After architecture: next is `/build-orchestrator` (skill: `build-orchestrator`).

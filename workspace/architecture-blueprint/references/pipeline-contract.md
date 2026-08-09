# Pipeline Contract

Shared expectations across `product-discovery` → `architecture-blueprint` → `build-orchestrator`.

## Stage boundaries

| Stage | Skill | Owns | Does not own |
|-------|--------|------|----------------|
| Discovery | `product-discovery` / `/product-discovery` | WHAT / WHY, personas, workflows, rules, testable ACs with stable IDs, constraints, assumptions | Frameworks, schemas, APIs, infra, code |
| Architecture | `architecture-blueprint` / `/architecture-blueprint` | HOW: stack, data model, components, interfaces, phases, ownership map, requirement_refs, Build Manifest (multi-phase), deployment | Product intent inventing, application code |
| Build | `build-orchestrator` / `/build-orchestrator` | Coordinated implementation from approved architecture | Redesigning architecture or product |

## Doc paths

| Kind | Requirements | Architecture | Progress |
|------|--------------|--------------|----------|
| Feature in existing project | `/docs/features/{name}/requirements/` | `/docs/features/{name}/architecture/` | `/docs/features/{name}/progress/` |
| New application | `/docs/requirements/` | `/docs/architecture/` | `/docs/progress/` |

## What discovery must leave for architecture

- Specific capabilities and business rules (not vague feature names)
- Personas and primary workflows with **objectively testable** acceptance criteria
- Stable IDs on stories, ACs, and business rules (`US-*`, `AC-*`, `BR-*`, optionally namespaced)
- Non-functional expectations in user terms
- Constraints, out-of-scope, and Open Questions
- **Assumptions** only when the user explicitly chose a speed path and confirmed them

## What architecture must leave for build

- Mode line: `Mode: PM | Developer`
- Budget tier: `Budget Tier: hobby | startup | scaling | enterprise`
- Complete file structure with purpose per file (ownership map)
- Implementation phases with depends-on, produces, parallel opportunities, test focus, and **requirement_refs**
- Interface contracts scaled to risk (high detail at multi-worker seams for autonomous builders)
- **Build Manifest** for multi-phase work (`commands`, `owns`, `shared`, `depends_on`, `requirement_refs`, `integration_checkpoints`); inline fields for trivial single-phase
- Pinned build/test commands (or TBD only for scaffold phase)
- Requirements reference path(s)

## What build must honor

- Prefer Build Manifest for DAG, ownership, and commands when present and consistent with prose
- Pass requirement_refs into test-author, implementer, and reviewer prompts
- Do not invent product behavior or architecture; stop and ask when blocked
- Disjoint file ownership; serialize or isolate `shared` paths; worktrees when ≥2 non-trivial implementers run in parallel
- Parallelism capped by unblocked disjoint `owns` + context peak (1–2 small; 2–3 multi-phase shared tree; 3–5 with worktrees; up to 6 exceptional). TDD gates sequential per slice.

## Skip paths

- Discovery optional when the user already has architecture-ready requirements (IDs + testable ACs preferred; polish IDs if missing).
- Architecture optional only for trivial one-file changes the user wants coded immediately (orchestrator should still stop if multi-file ownership is unclear).
- Design system docs under `/docs/design-system/` are optional; if present, architecture and build should reference them for UI work. Do not invoke a separate frontend-design skill.

## Handoff phrases

- After discovery: next is `/architecture-blueprint` (skill: `architecture-blueprint`).
- After architecture: next is `/build-orchestrator` (skill: `build-orchestrator`).

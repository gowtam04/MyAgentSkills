# Large Application Requirements Structure

Use this layout when the work is a new product or spans multiple domains. Split by **functional area**, not by interview order or MVP/enhancement/polish tiers.

## Standard Files

Write under `/docs/requirements/` (new app) or `/docs/features/{feature-name}/requirements/` (large feature in an existing project):

| File | Contents |
|------|----------|
| `overview.md` | Vision, goals, personas summary, success criteria, priorities, document map, Assumptions (if any) |
| `core-workflows.md` | Primary workflows, edge cases, business logic per journey (US-/AC- IDs) |
| `data-and-entities.md` | Business entities, relationships, ownership, lifecycle rules (not DB design) |
| `auth-and-permissions.md` | Roles, access rules, approval flows, session expectations in product terms (US-/AC-/BR- IDs) |
| `api-and-integrations.md` | Business-level integration needs and data flows (not endpoint design) |
| `ui-and-experience.md` | Screens, interaction patterns, responsive behavior, tone (omit if non-UI) |
| `operational.md` | Non-functional needs, compliance, constraints, ops expectations, Out of Scope |

Omit files that truly do not apply (e.g. drop `ui-and-experience.md` for API-only work).

## Stable IDs

Carry the same addressable ID discipline across every file:

- User stories: `US-1`, or namespaced `AUTH-US-1`
- Acceptance criteria: `AC-1.1`, or `AUTH-AC-1.1`
- Business rules: `BR-1`, or `BILLING-BR-2`

Keep IDs stable once assigned; append, do not renumber. Acceptance criteria must be objectively testable (Given/When/Then or concrete checkable assertions).

## Grouping Rules

- Group requirements that share the same users, entities, business rules, or workflow context.
- Note dependencies between areas when one must be designed or built before another (e.g. auth before admin workflows).
- Prefer more smaller domain files over one giant file when domains will become separate architecture phases.

## Cross-Links

Each domain file should briefly state:

- Which personas it serves
- Which entities it touches
- What it depends on from other domain files

That mapping is what lets `/architecture-blueprint` slice implementation phases cleanly and attach `requirement_refs` per phase.

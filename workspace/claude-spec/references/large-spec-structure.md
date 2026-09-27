# Large Spec Structure

Use this layout only when the spec is genuinely large: four or more distinct domains, each with its
own workflows and rules, or a single `requirements.md` that would run past roughly 500 lines.
Anything smaller stays in one file with a section per functional area — that's easier for the user
to review and loses nothing downstream, because the IDs and cross-links do the addressing.

Split by **functional domain**, not interview order and not MVP tiers — the architect turns each
domain into one or more build phases, and a domain file that mixes unrelated concerns forces those
phases to share files.

## Files

Write under `docs/requirements/` (new app) or `docs/features/{feature-name}/requirements/`.
Start from `assets/large-spec/overview.md` and `assets/large-spec/domain.md`.

| File | Contents |
|---|---|
| `overview.md` | Vision, problem, personas summary, success criteria, priority notes, document map, constraints, Assumptions, cross-domain Open Questions |
| `{domain}.md` — one per domain | Stories, criteria, rules, workflows and data for that domain, with cross-links |
| `non-functional.md` | Performance, reliability, scale, accessibility, platforms, compliance, privacy |
| `out-of-scope.md` | The hard boundary, if it's long; otherwise keep it in `overview.md` |

Typical domains (name them after the real product, not this list): `accounts-and-access`,
`core-workflows`, `billing`, `notifications`, `reporting`, `integrations`, `admin`,
`ui-and-experience` (screens, interaction patterns, responsive behavior — omit for API-only work).

## Grouping rules

- Group requirements that share the same users, entities, rules, or workflow context.
- Prefer several smaller domain files over one giant file when domains will become separate build
  phases — the architect can parallelize domains that don't share entities.
- When one domain depends on another (billing depends on accounts), say so explicitly in the
  cross-links so the architect can sequence them.
- Capture priority ("billing can come after the core workflow") as a note in `overview.md`; don't
  restructure the files around it.

## IDs

Namespace per domain so IDs stay unique and readable across files: `ACCT-US-1`, `ACCT-AC-1.2`,
`BILL-BR-3`. Pick a short prefix per domain and list the prefixes in `overview.md`'s document map.
Append, never renumber.

## Cross-links

Every domain file opens with a short block:

```markdown
> **Serves:** Team admin, Member
> **Touches entities:** Workspace, Membership, Invitation
> **Depends on:** accounts-and-access (roles, sign-in)
> **Used by:** billing (seat counts), notifications (invite emails)
```

This is what lets the architect attach exact `requirement_refs` to each phase and see which
domains can be built in parallel.

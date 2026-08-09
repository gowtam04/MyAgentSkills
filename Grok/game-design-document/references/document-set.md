# Document Set

When to produce which files, and how they cross-link. Section bodies live only in `templates.md`.

## Paths

| Situation | Root |
|---|---|
| New game | `/docs/gdd/` |
| Feature / mode inside an existing game | `/docs/gdd/features/{feature-name}/` |
| User names another root | Honor it; keep the same internal filenames |

Create the directory if missing. Prefer updating an existing GDD tree over creating a second parallel tree.

## Package Shapes

### Lean

Use when jam-sized, single-system, or the user explicitly wants speed.

| File | Role |
|---|---|
| `00-one-pager.md` | North star: pitch, pillars, loop, slice |
| `systems.md` | Rules for every in-scope system |
| Optional: `production.md` | Slice, cuts, risks if not already on the one-pager |

If truly tiny (toy prototype), a single `gdd.md` that concatenates one-pager + systems is acceptable—state that choice in a one-line note at the top.

### Standard / extensive (default)

Use for multi-system games, narrative games, or when the user asks for thorough documentation.

| File | Role | Primary readers |
|---|---|---|
| `README.md` | Index, maintenance rules, status | Everyone |
| `00-one-pager.md` | Scannable vision | Everyone, stakeholders |
| `01-vision-and-pillars.md` | Fantasy, pillars, non-goals, comps, success | Design, production |
| `02-core-loop-and-structure.md` | Loops, camera, session structure, first-play | Design, eng, level design |
| `03-systems.md` | Mechanics, rules, edge cases, connections | Design, eng |
| `04-content-and-world.md` | Setting, narrative, content counts, progression | Design, narrative, content |
| `05-ux-ui.md` | Screens, HUD, flows, controls | UX, eng, art |
| `06-art-audio-juice.md` | Style, audio, feedback/juice, asset lists | Art, audio, design |
| `07-production-and-slice.md` | Scope, slice, milestones, risks, constraints | Production, leads |
| `08-open-questions.md` | Unresolved decisions only | Everyone |

### Systems split

When `03-systems.md` would exceed ~400 lines or systems are owned by different people, split:

```
systems/
  README.md          # index + dependency graph
  movement.md
  combat.md
  ...
```

Each system file follows the **System entry** template in `templates.md`. Keep a short index table in `03-systems.md` or `systems/README.md` linking to each file and listing dependencies.

### Feature-only package

For a single feature or mode under `/docs/gdd/features/{name}/`:

| File | Role |
|---|---|
| `README.md` | Feature goal, pillar fit, links to parent GDD |
| `design.md` | Full feature design (verbs, rules, UX, content, edge cases) |
| `acceptance.md` | Playtestable acceptance criteria and slice notes |

Always link back to parent pillars and core loop so the feature cannot drift.

## Cross-Link Rules

- One-pager links to deeper files; deeper files link **up** to pillars they serve.
- Every system entry names the pillar(s) and loop step(s) it supports.
- Content counts in `04` must match systems that consume that content in `03`.
- Slice definition in `07` must reference only systems/content marked in-slice.
- Open questions must not duplicate settled decisions stored elsewhere—resolve or delete.

## Living Document Maintenance (put in README.md)

State these norms in the package README:

1. **Prototype wins conflicts.** When playable behavior diverges, update the GDD or explicitly log an approved exception.
2. **Changelog light.** Add a short "Last updated / notable decisions" list on the README, not a novel history in every file.
3. **Hypothesis tags.** Use `Status: hypothesis | prototyped | locked` on systems and major features.
4. **Cut with intent.** When scope drops, move items to Out of scope with a one-line reason; do not ghost-delete silently if others may re-propose them.

## What Not To Duplicate

| Fact | Single home |
|---|---|
| Pitch + pillars | `01` (summary on `00`) |
| Core loop steps | `02` (summary on `00`) |
| System rules | `03` / `systems/*` only |
| Content volume tables | `04` only |
| Slice definition | `07` only (link from `00`) |
| Open questions | `08` only |

Summaries on the one-pager are allowed; full restatements are not.

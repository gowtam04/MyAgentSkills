# Component Design

Break the system into components/modules with clear responsibilities. If a component needs a paragraph to explain its purpose, split it or clarify the boundary.

## Components

### {ComponentName}

| Aspect | Detail |
|--------|--------|
| Responsibility | Single sentence |
| Owns | Data / workflows / files |
| Exposes | Public interface summary |
| Depends on | Other components / external services |
| File location | Paths this component owns |
| Patterns followed | Existing repo patterns, if any |

## Dependency Graph

```text
{A} -> {B} -> {C}
```

## Boundary Rules

- Prefer components that two subagents can own without sharing write files in the same phase.
- Shared types/contracts live in a dedicated module so feature work does not collide.
- Note which components are in-process vs separate services (must match topology on `overview.md`).

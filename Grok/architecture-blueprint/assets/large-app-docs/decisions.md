# Decisions

Architecture Decision Records (ADRs) for every significant, hard-to-reverse choice.

## Template (use one section per decision)

### ADR-{N}: {Title}

- **Context:** The problem or requirement that forced a choice; budget tier if relevant.
- **Options considered:**
  - Option A — pros / cons
  - Option B — pros / cons
  - Option C — pros / cons (if any)
- **Decision:** What we chose.
- **Rationale:** Why this option fits requirements, stack, and budget.
- **Consequences:** What we accept, what we defer, reversal difficulty.
- **Links:** Requirements paths, related components.

## Example (replace with real decisions)

### ADR-1: Use a modular monolith for v1

- **Context:** Multiple domains (auth, billing, content) but a solo/small team and startup budget; microservices would multiply ops cost.
- **Options considered:**
  - Modular monolith — single deploy, clear module boundaries — lower ops, risk of boundary erosion
  - Microservices — independent scale — high ops and interface overhead early
  - Serverless per domain — scale-to-zero — cold starts and distributed debugging
- **Decision:** Modular monolith with package/module boundaries per domain.
- **Rationale:** Matches startup budget and team size; modules can be extracted later if scale demands it.
- **Consequences:** Must enforce module import rules in review; no independent deploy per domain in v1.
- **Links:** Requirements overview; `component-design.md`.

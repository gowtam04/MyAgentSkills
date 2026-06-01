# Testing Strategy

**Developer mode only** — delete this file if the architecture was produced in PM mode.

- **Test framework** — runner and assertion library.
- **Unit vs integration split** — what's covered at each level; per-phase split if it varies.
- **Mocking policy** — what runs for real (DB, queue, external APIs?) and what's faked.
- **Coverage target** — the bar, and what's exempt.
- **Fixture conventions** — where fixtures live, how they're named, how test data is built.
- **Eval harness** *(if there's an AI/agent component)* — test runner, fixture format, how
  golden cases from `agent-design/evaluation.md` are wired, how LLM-as-judge runs if used.

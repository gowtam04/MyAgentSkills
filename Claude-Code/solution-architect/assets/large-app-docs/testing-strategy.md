# Testing Strategy

**Developer mode only** — delete this file if the architecture was produced in PM mode.

- **Test framework** — runner and assertion library. (The exact run commands live in `deployment.md` → Build & Test Commands, mirrored in the Build Manifest.)
- **Unit vs integration split** — what's covered at each level; per-phase split if it varies.
- **Mocking policy** — what runs for real (DB, queue, external APIs?) and what's faked.
- **Coverage target** — the bar, and what's exempt.
- **Fixture conventions** — where fixtures live, how they're named, how test data is built.
- **Eval harness** *(if there's an AI/agent component)* — test runner, fixture format, golden
  cases, how LLM-as-judge runs if used.

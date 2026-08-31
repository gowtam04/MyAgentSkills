# Developer Mode

Read this when the user chooses Developer mode or asks to go deeper for a human dev team.

## Purpose

Architecture Design always runs in one of two modes:

- **PM mode**: Best for rapid prototypes, solo builders, and `build-team` handoff. Infer sensible code-level defaults and keep the design conversation to roughly 3-5 user-input rounds (via `AskQuestion`).
- **Developer mode**: Best for handoff to a human dev team. Stop inferring decisions that developers commonly care about; surface them via `AskQuestion`. Use roughly 5-8 rounds, batched aggressively.

Mode does not change the main architecture sections. It changes the depth and explicitness of the decisions. Record `Mode: Developer` in the output so `build-team` can include the extra conventions and test strategy in worker prompts and `TodoWrite` phases.

## Package Choices To Surface

Ask about package choices when they shape the code itself (via `AskQuestion`). Put implications in the option **labels** (Cursor has no option description field):

- ORM/query builder.
- Auth/session library.
- Validation library.
- HTTP client or API client style.
- Queue client.
- Cache client.
- Logger.
- Test runner and assertion library.

Skip choices that do not apply. Do not ask about lockfile tools, minor lint plugins, or other incidental package details unless the repo already treats them as architectural.

## Cross-Cutting Patterns To Surface

In PM mode these can be inferred. In Developer mode, ask about:

- Error handling style: exceptions, Result/Either, API error envelope.
- Logging library and structured log fields.
- Transaction and concurrency boundaries.
- Frontend state management and form/server-state approach.
- Observability: metrics, tracing, error tracking.
- Mocking policy and test split.

Batch related questions. State a recommendation in the prose before the card and in the first option label so a team can quickly accept the default.

## Interface And Phase Detail

Default to high-detail interface definitions:

- Function signatures or route contracts.
- Complete input/output types with field-level notes.
- Error types and error behavior.
- Auth/permission expectations.
- Transaction/concurrency notes.
- Non-obvious side effects.

Each implementation phase adds:

- **Success criteria**: concrete outcomes beyond "tests pass."
- **Review checklist / test split**: what is unit-tested, what is integrated, what is mocked, and what reviewers must check.
- **Requirement refs** (both modes): US-/AC-/BR- IDs the phase satisfies — required for autonomous builders even when success criteria are Developer-only.

## Output Additions

For a small feature, fill these sections in `design.md`:

- `## Code Conventions`: naming, module boundaries, errors, logging, lint/format, transaction stance, frontend state if applicable.
- `## Testing Strategy`: framework, unit vs integration split, mocking policy, coverage target, fixture conventions.

For a large application, fill:

- `conventions.md`
- `testing-strategy.md`

If a PM runs Developer mode without developers present, still recommend concrete choices. Mark them `Proposed - confirm with dev team` and list them under unresolved/follow-up items.

## Mode Switch

If the user upgrades PM mode to Developer mode before implementation, ask a follow-up batch for the code-level choices PM mode skipped, then update the docs in place. Downgrading after docs are written is unnecessary; the extra detail is usually harmless.

## Interface Scale-To-Risk Test

For each seam ask: would a builder or subagent plausibly get this wrong without guidance?

- **Yes** → full signatures/types/errors/auth/side effects.
- **No** (conventional CRUD matching repo patterns) → light shapes and a pointer to the existing pattern.

When the consumer is `build-team` (or any autonomous implementer that cannot ask mid-build), bias **Yes** at multi-worker seams regardless of PM vs Developer mode.

## Cursor-Specific Notes

- All surfaced decisions use `AskQuestion`. Options are `{id, label}` only — put implications in the label. Multi-pick is `allow_multiple`.
- When this skill itself needs to plan a large or ambiguous design, offer `SwitchMode` to `plan` so the user reviews a documentation-only plan before files are written.
- Subagent usage (if any) for exploration must follow tool-call discipline: the `Task` call precedes any claim that a worker was launched. Use `Task` `explore` for stack/conventions scans.
- `build-team` uses Mode to right-size TDD rigor; Developer mode implies fuller test/review cycles.

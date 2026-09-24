# Developer Mode (Games)

Read this when the user chooses Developer mode or asks for a human-team-quality blueprint.

## Purpose

- **PM mode**: Solo builders and `/game-dev-orchestrator` handoff. Infer ordinary engine details. Keep the design conversation short; batch via `ask_user_question`.
- **Developer mode**: Handoff to a human game team. Stop inferring choices developers commonly argue about; surface them via `ask_user_question`.

Mode does not change the main architecture sections. It changes depth. Record `Mode: Developer` so `/game-dev-orchestrator` includes extra conventions and testing in worker prompts.

## Package And Runtime Choices To Surface

Ask when they shape the project (skip what does not apply):

- Physics engine vs kinematic/authored motion
- Tween / animation runtime
- Input layer (engine built-in vs plugin)
- Tilemap / level format
- Save/serialization library
- Test runner (GUT, gdUnit, Unity Test Framework, node test, XCTest, …)
- Audio bus / mixer approach

Do not ask about lockfiles, formatter plugins, or incidental editor settings unless the repo already treats them as architectural.

## Cross-Cutting Patterns To Surface

In PM mode these can be inferred. In Developer mode, ask about:

- Time: engine delta vs fixed tick; pause; hitstop
- Error handling and invalid content (missing asset, malformed level)
- Logging / debug overlay (hitboxes, lean meters, seed)
- Determinism needs (replays, seeds, netcode)
- Mocking policy for tests (what is real: time, input, RNG)

## Interface And Phase Detail

Default to high-detail contracts:

- Function/signal signatures
- Event payloads
- Error/invalid-content behavior
- Who may write shared autoloads

Each implementation phase adds:

- **Success criteria**: concrete outcomes beyond "tests pass" (e.g. "a tap drops the held floor; overlap uses the GDD inset")
- **Review checklist / test split**: unit vs playtest vs visual
- **gdd_refs** (both modes)

## Output Additions

Small feature `design.md`: fill Code Conventions and Testing Strategy.

Large package: fill `conventions.md` and `testing-and-playtest.md`.

If a PM runs Developer mode without a team present, still recommend concrete choices. Mark them `Proposed - confirm with team` under unresolved items.

## Mode Switch

Upgrading PM → Developer: ask a follow-up batch for the skipped code-level choices, then update docs in place. Downgrading is unnecessary; extra detail is usually harmless.

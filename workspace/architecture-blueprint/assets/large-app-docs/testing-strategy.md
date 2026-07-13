# Testing Strategy *(Developer mode only)*

Delete this file in PM mode.

## Framework And Commands

| Concern | Tool / command |
|---------|----------------|
| Unit tests | |
| Integration tests | |
| E2E (if any) | |
| Typecheck | |
| Lint | |
| Build | |

## Unit Vs Integration Split

- Unit: pure domain logic, isolated with fakes where needed
- Integration: DB, HTTP, auth, real wiring at seams
- E2E: main user workflows only

## Mocking Policy

- What is always real:
- What may be faked:
- What must never be faked in integration tests:

## Coverage And Fixtures

- Coverage target (if any):
- Fixture / factory conventions:

## Per-Phase Review Gates

Summarize what reviewers must check and which test split applies per major phase (can point at `implementation-plan.md`).

# Ownership Map Checklist

Run this before finalizing architecture docs. `/build-orchestrator` uses the file structure as the parallel-write contract.

## File structure

- [ ] Every file to create or modify is listed with a one-line purpose.
- [ ] Each file has a single owner component/module.
- [ ] New vs modified is clear when working in an existing repo.
- [ ] Shared types/contracts live in dedicated files so feature modules do not both edit them in the same phase.
- [ ] Test files are listed alongside the production files they cover (or called out per phase).

## Phases

- [ ] Each phase lists specific files/components, not vague areas.
- [ ] Dependencies between phases are explicit.
- [ ] Parallel opportunities only span disjoint write sets (no shared file between parallel workers).
- [ ] Each phase has a test focus (or states why TDD does not apply: config, migration, docs, scaffolding).
- [ ] Integration points (API↔data, UI↔API, auth cross-layer) appear as their own phase or explicit sub-step.

## Interfaces

- [ ] High-risk seams have signatures/types/errors/auth notes.
- [ ] Conventional CRUD is allowed lighter detail.
- [ ] External provider boundaries and failure handling are defined where used.

## Mode and budget

- [ ] `Mode: PM | Developer` is recorded.
- [ ] `Budget Tier: hobby | startup | scaling | enterprise` is recorded.
- [ ] Deployment choices fit the budget tier and include a rough cost bucket.

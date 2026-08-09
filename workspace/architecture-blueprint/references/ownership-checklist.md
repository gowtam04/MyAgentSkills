# Ownership Map Checklist

Run this before finalizing architecture docs. `/build-orchestrator` uses the file structure (and Build Manifest when present) as the parallel-write contract.

## File structure

- [ ] Every file to create or modify is listed with a one-line purpose.
- [ ] Each file has a single owner component/module.
- [ ] New vs modified is clear when working in an existing repo.
- [ ] Shared types/contracts live in dedicated files so feature modules do not both edit them in the same phase.
- [ ] Test files are listed alongside the production files they cover (or called out per phase).

## Phases

- [ ] Each phase lists specific files/components, not vague areas.
- [ ] Dependencies between phases are explicit.
- [ ] Parallel opportunities only span fully disjoint write sets (no shared file between parallel workers); each parallel slice lists explicit globs or "none — sequential."
- [ ] Each phase has a test focus (or states why TDD does not apply: config, migration, docs, scaffolding).
- [ ] Each phase has **requirement refs** (US-/AC-/BR- or section cite + gap note).
- [ ] Integration points (API↔data, UI↔API, auth cross-layer) appear as their own phase or explicit sub-step / checkpoint.

## Interfaces

- [ ] High-risk seams have signatures/types/errors/auth notes.
- [ ] Multi-worker seams are specified at autonomous-builder depth (builders cannot ask mid-build).
- [ ] Conventional CRUD is allowed lighter detail.
- [ ] External provider boundaries and failure handling are defined where used.

## Build Manifest (multi-phase)

- [ ] Manifest present (or trivial single-phase with fields inlined in prose).
- [ ] `phases[].name` / `depends_on` match prose.
- [ ] `owns` globs partition the File Structure; no dual ownership.
- [ ] Multi-touch files listed under `shared`, not two `owns`.
- [ ] `requirement_refs` match prose phase refs.
- [ ] `commands` match Deployment Build & Test Commands.
- [ ] `integration_checkpoints` cover named seams.

## Mode and budget

- [ ] `Mode: PM | Developer` is recorded.
- [ ] `Budget Tier: hobby | startup | scaling | enterprise` is recorded.
- [ ] Deployment choices fit the budget tier and include a rough cost bucket.

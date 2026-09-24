# Ownership Map Checklist

Run this before finalizing architecture docs. `/game-dev-orchestrator` uses the file structure, Game Build Manifest, and Asset Manifest as the parallel-write contract.

## File structure

- [ ] Every code file to create or modify is listed with a one-line purpose.
- [ ] Every slice asset path is listed (Asset Manifest and/or file tree).
- [ ] Each file has a single owner module.
- [ ] New vs modified is clear when working in an existing repo.
- [ ] Shared types, autoloads, scene roots, atlases, and import config live in dedicated files so feature modules do not both edit them in the same phase.
- [ ] Test files are listed alongside the production files they cover (or called out per phase).

## Phases

- [ ] Each phase lists specific files/components, not vague areas ("gameplay", "art").
- [ ] Dependencies between phases are explicit. Style-lock precedes character/tile/UI sets. Schema precedes content-authors.
- [ ] Parallel opportunities only span fully disjoint write sets; each parallel slice lists explicit globs or "none — sequential."
- [ ] Each phase has a test focus **or** states why automated TDD does not apply (scaffold, greybox feel, assets, audio stubs).
- [ ] Each phase has a playtest focus **or** "none — not playable yet."
- [ ] Each phase has **gdd_refs** (GDD file + section or system name, plus slice criterion when relevant).
- [ ] Playtest/integration checkpoints appear as their own phase or explicit sub-step.

## Interfaces

- [ ] High-risk seams have signatures/types/errors (overlap resolve, scoring, state, save, pause).
- [ ] Multi-worker seams are specified at autonomous-builder depth.
- [ ] Conventional engine glue may be lighter if it matches existing project patterns.

## Game Build Manifest (multi-phase)

- [ ] Manifest present (or trivial single-phase with fields inlined in prose).
- [ ] `phases[].name` / `depends_on` match prose.
- [ ] `owns` globs partition the File Structure; no dual ownership.
- [ ] Multi-touch files listed under `shared`, not two `owns`.
- [ ] `gdd_refs` match prose phase refs.
- [ ] `commands` match pinned run/test/export.
- [ ] `kind` is one of scaffold | gameplay | content | assets | audio | juice | ui | playtest.
- [ ] Playtest checkpoints cover the slice loop.

## Asset Manifest

- [ ] Style-lock exists as its own asset (or an explicit "greybox-only, no style-lock" note for jam/greybox-first).
- [ ] Every slice visual has id, path, kind, specialist skill, `depends_on`, owning phase.
- [ ] Two assets that would share a sheet/atlas are not assigned to parallel workers.
- [ ] Out-of-slice ship assets are listed only when Scale is shippable-indie; otherwise deferred in a short "later" list, not fake-owned.

## Mode and scale

- [ ] `Mode: PM | Developer` is recorded.
- [ ] `Scale: jam | vertical-slice | shippable-indie` is recorded.
- [ ] Phase ceremony matches scale (jam ≠ full live-ops pipeline).

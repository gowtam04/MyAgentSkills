# Ownership Checklist

Walk this before presenting. `claude-build` treats the File Structure and the Build Manifest as a
parallel-write contract: if two workers are told they own the same file, one of them loses work.

## File structure
- [ ] Every file to create or modify is listed with a one-line purpose.
- [ ] New vs modified is marked when working in an existing repo.
- [ ] Every file has exactly one owning phase.
- [ ] Test files are listed alongside the code they cover and owned separately (manifest `tests`).
- [ ] Shared types and contracts live in their own files (usually the `contracts` phase), not
      inside a feature module that two phases would both edit.
- [ ] Hub files (entry point, router, registry, root layout, nav) are owned by one `wiring` phase;
      feature modules expose registration functions from their own files.

## Phases
- [ ] Each phase lists specific files, not vague areas.
- [ ] Each phase has a `kind`; `logic` and `ui` phases have test files.
- [ ] Dependencies are explicit, and there are no cycles.
- [ ] Cross-phase calls are covered: wherever a phase's code calls a function another phase
      implements, the caller either depends on that phase, or its notes say its tests fake the
      callee against the contract. Walk the Interface Definitions and ask "who calls this?" for each
      one — `check_manifest.py` can't see calls in code.
- [ ] Phases marked as parallel have fully disjoint write sets.
- [ ] Each phase cites requirement refs (or states why none apply: scaffold, contracts, wiring).
- [ ] High-risk phases (auth, permissions, payments, money math, migrations, security, concurrency)
      are marked `risk: high`.
- [ ] Integration checkpoints are named, placed at real seams, and say what they prove.

## Interfaces
- [ ] Every seam between two phases has signatures, input/output types, error types and behavior
      notes at the depth an agent that can't ask back needs.
- [ ] Security-sensitive boundaries state who may call them and what's validated.
- [ ] External provider boundaries define failure handling (timeouts, retries, what the user sees).
- [ ] Conventional internals may stay light.

## Commands
- [ ] `test`, `test_one` (with `{files}`), `typecheck` (or `none`), `build` and `smoke` are pinned —
      TBD only when a scaffold phase will set them, and that phase owns the smoke script.
- [ ] The manifest's `commands` match the deployment doc's command table exactly.

## Build Manifest
- [ ] Present for multi-phase work (or fields inlined in the prose for a single phase).
- [ ] Phase names and `depends_on` match the prose exactly.
- [ ] `owns`/`tests` globs partition the File Structure; no path in two phases.
- [ ] Files touched by several phases are `shared` for all but their creator, and the creator is
      upstream of every sharer.
- [ ] Every requirement ID is cited by a phase or listed in `deferred_refs`.
- [ ] `check_manifest.py` reports 0 errors.

## Mode and budget
- [ ] `Mode:` and `Budget Tier:` lines are present (and `Backend Topology:` for large work).
- [ ] Every infrastructure choice fits the tier; a monthly cost bucket is stated.

# Designing for a Wide Build

`claude-build` has no fixed worker cap. It launches every phase whose dependencies are complete
and whose files don't overlap with running work, all at once, up to Claude Code's
concurrent-subagent limit. Nothing in the build can make a narrow plan fast — so aim for the
widest plan the design honestly allows.

## Contents
- [Techniques](#techniques)
- [The Parallel Waves table](#the-parallel-waves-table)
- [Worked example](#worked-example)
- [Don't fake independence](#dont-fake-independence)

## Techniques

Roughly in order of payoff:

1. **Contracts first.** Put shared types, interfaces, API request/response types, event names,
   error types and DB schema types in an early `contracts` phase — small, owned once, verified by
   typecheck. Every later phase codes and writes tests against those contracts in parallel instead
   of waiting for the module it calls to exist. This is the single biggest widener: it turns
   "services, then routes, then UI" into "services ‖ routes ‖ UI, all against the same contracts".
   For every call across phases, decide explicitly: either the caller's tests fake the callee
   against its contract (keeps them parallel; the real call is proven at the wiring phase or an
   integration checkpoint), or the caller depends on the callee (simpler, but narrower). Write the
   choice into the phase notes — an unstated cross-phase call is how a builder ends up blocked
   waiting on code that another wave hasn't written yet.

2. **One slice per module or domain.** Give each independent module its own phase id (`p4a`,
   `p4b`, `p4c`), its own source files, its own test files, and its own requirement refs. Keep
   domain logic in pure modules (no framework imports) where the stack allows — they never touch
   hub files and test headlessly.

3. **No hub files.** Entry points (`main.ts`, `app.py`), routers, DI containers, plugin
   registries, root layouts and nav menus are where plans serialize. Instead:
   - each feature module exports a registration function from its own file
     (`registerInvoiceRoutes(router)`, `invoiceNavItem`, `install(app)`);
   - one `wiring` phase, late in the plan, owns the hub and calls them all.
   If a file would be `shared` by three or more phases, restructure it this way —
   `check_manifest.py` warns about exactly this.

4. **Tests are their own owned files.** Each phase's tests live in files only that phase's
   test-writer touches, listed under `tests:` in the manifest. Test-writing for every phase in a
   wave can then run at once, and implementers never collide with test-writers.

5. **Split UI by screen.** One phase per screen or feature area, each owning its page and
   components, sharing only the design-system primitives built in an early phase.

6. **Split data by table ownership.** Migrations are ordered, so keep them in one early `data`
   phase (or one per bounded context in a modular monolith) rather than letting feature phases add
   migrations ad hoc.

7. **Keep integration checkpoints few and meaningful.** They're barriers. Put them where they
   catch real integration risk — backend stack assembled, UI wired to API, full end-to-end — not
   after every phase.

8. **Keep the critical path short.** The build can't finish faster than its longest dependency
   chain. If one module sits on the critical path, consider splitting it (contracts vs
   implementation) or pulling unrelated work off it.

## The Parallel Waves table

Add this to `implementation-plan.md` (or `design.md` for a multi-phase small feature):

```markdown
## Parallel Waves
| Wave | Phases (run together) | Barrier after |
|---|---|---|
| 1 | p1 Scaffold | — |
| 2 | p2 Contracts, p3 Data model | — |
| 3 | p4a Accounts, p4b Invoices, p4c Payments, p5a Invoice UI, p5b Settings UI | backend-e2e |
| 4 | p6 Wiring | — |
| 5 | p7 E2E polish | final |

**Critical path:** p1 → p2 → p4b → p6 → p7
```

`check_manifest.py` prints the waves it computes from `depends_on`; the table should match it.

## Worked example

A narrow plan for an invoicing app:

```
p1 scaffold → p2 models → p3 services → p4 routes → p5 UI → p6 e2e
```

Six waves of one phase each. Every layer waits for the one below; `app.ts`, `router.ts` and
`nav.tsx` are edited by p3, p4 and p5.

The same app, designed wide:

```
wave 1: p1 scaffold (owns app.ts shell, smoke script)
wave 2: p2 contracts (types, API schemas, errors)   p3 data (migrations, repositories)
wave 3: p4a accounts svc+routes  p4b invoices svc+routes  p4c payments svc+routes
        p5a invoice screens      p5b settings screens      (UI codes against p2 contracts)
wave 4: p6 wiring (owns app.ts, router.ts, nav.tsx; calls each module's register function)
wave 5: p7 end-to-end
```

Five waves, and wave 3 runs five phases at once. The trick was contracts first plus
registration functions — nothing in wave 3 touches a hub file.

## Don't fake independence

If two modules genuinely share mutable state, a single file, or a transaction boundary, they are
one slice. A merge conflict or an integration bug found at the wiring phase costs more time than
the parallelism saved. When unsure, sequence it and say why in the phase notes.

# Component Design

## Components
For each component/module:
- Responsibility (one sentence — if you can't, it's doing too much)
- Interface it exposes to other components
- What it depends on
- Where it lives in the file structure

## File Structure
Complete file tree with a brief purpose for each file, the phase that owns it, and whether it's
new or modified. This is the ownership map — no two phases edit the same file. List test files
next to the code they cover; they're owned separately (the build gives them to a test-writer).
Hub files (entry point, router, registry, nav) belong to one `wiring` phase; feature modules
expose registration functions from their own files.

```
src/
├── invoices/
│   ├── invoice.service.ts     — finalize/void/credit logic, enforces BR-4       [p4b, new]
│   ├── invoice.service.test.ts                                              [p4b tests, new]
│   └── register.ts            — registerInvoiceRoutes(router)                  [p4b, new]
└── app.ts                     — composes modules; calls each register()        [p6 wiring, modified]
```

## Interface Definitions
Contracts between components — function signatures, input/output types with field-level detail,
error types, behavior notes. At every seam where two phases meet, write them at the depth an agent
that can't ask back needs: two workers building opposite sides of an undocumented seam will guess
differently. Conventional internals can stay light; in Developer mode default to high detail.
(If there is an AI/agent component, include its interface here and enough prompt/tool/output
detail for implementers — see `references/agent-features.md`.)

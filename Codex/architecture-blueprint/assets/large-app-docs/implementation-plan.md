# Implementation Plan

Granular, build-order phases. Prefer more phases with smaller scope over fewer with larger scope -
a phase should touch one layer or one functional domain.

## Phase N: {Name}
- **What gets built:** specific files/components
- **Depends on:** which prior phase(s) must be complete
- **Produces:** what interfaces/files are available after this phase
- **Parallel opportunities:** what within this phase can be built simultaneously
- **Test focus:** what the phase's tests verify
- **Success criteria** *(Developer mode)*: concrete, reviewable outcomes beyond "tests pass"
- **Review checklist / test split** *(Developer mode)*: unit vs integration, mocked vs real, review gates

(Repeat for each phase. Typical full-app shape: scaffolding -> data model -> auth -> core business
logic -> API -> frontend foundation -> frontend screens -> integration & polish. Adapt the count to
the actual work.)

# Component Design

## Components
For each component/module:
- Responsibility (one sentence — if you can't, it's doing too much)
- Interface it exposes to other components
- What it depends on
- Where it lives in the file structure

## File Structure
Complete file tree with a brief purpose for each file. This is the ownership map —
each file has one purpose; no two builders should need to edit the same file.

## Interface Definitions
Key contracts between components — function signatures, types, error types.
Scale detail to complexity; in Developer mode default to high detail.
(If there is an AI/agent component, include its interface here and enough prompt/tool/output
detail for implementers — see `references/agent-features.md`.)

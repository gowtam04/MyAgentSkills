# Component Design

Break the system into components/modules. For each:

- Responsibility (single sentence)
- Exposed interface / public surface
- Dependencies (other components or external services)
- File location / ownership (this feeds the implementation-plan file ownership map)

Emphasize clear boundaries so two subagents in `/build-orchestrator` never need to edit the same file.

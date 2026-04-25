# Claude Phase Prompts

Use these prompts verbatim after filling in the placeholders.

## Initial Run Template

Use when there is no existing build-progress file yet, or when starting the first phase of a phased feature.

```text
Create a /dev-team to build {feature_or_project_reference}.

Complete only phase {phase_id}. Do not start phase {next_phase_id} or any later phase.

Read the architecture and requirements docs for this work, create or update the progress file as needed, and keep the run scoped to phase {phase_id} only.

{commit_instruction}

After that, summarize exactly what phase {phase_id} completed, identify the next pending phase, state whether a phase commit was created or intentionally skipped because there is no GitHub repo, and stop so I can relaunch a fresh /dev-team session for the next phase.

If phased architecture is missing, if repo docs are insufficient, or if you need a product decision that is not already documented, stop and report the blocker instead of guessing.
```

## Continuation Template

Use when resuming from an existing progress file or any later phase.

```text
Create a /dev-team to continue working on {feature_or_project_reference}.

Resume from {progress_file_path} and complete only phase {phase_id}. Do not start phase {next_phase_id} or any later phase.

Read the architecture, requirements, and existing progress state before acting. Keep the run strictly scoped to phase {phase_id}.

{commit_instruction}

After that, summarize exactly what phase {phase_id} completed, identify the next pending phase, state whether a phase commit was created or intentionally skipped because there is no GitHub repo, and stop so I can relaunch a fresh /dev-team session for the next phase.

If phased architecture is missing, if the progress state is ambiguous, or if you need a product decision that is not already documented, stop and report the blocker instead of guessing.
```

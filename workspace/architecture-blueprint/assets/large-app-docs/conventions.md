# Code Conventions

**Developer mode only** - delete this file if the architecture was produced in PM mode.

- **Naming patterns** - files, modules, types, functions, DB columns.
- **Module boundaries** - what depends on what; layering rules.
- **Error-handling style** - exceptions vs Result/Either vs error-envelope; the envelope shape.
- **Logging** - which logger; the structured log schema (fields required on every line, e.g.
  request_id, user_id, feature); what goes to stdout vs an external sink.
- **Transactions & concurrency** - where transactions start/end; optimistic vs pessimistic
  locking; retry policy.
- **Frontend state management** *(if there's a frontend)* - client state lib, server-state lib,
  form state approach.
- **Lint / format stance** - toolchain and any non-default rules that matter.

Record the answers to any code-level questions surfaced during the design conversation here,
each with a brief rationale.

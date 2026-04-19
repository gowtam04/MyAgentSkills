---
name: backwards-compatibility-checker
description: >
  Check whether a code branch is safe to merge into another branch (usually main) without breaking
  anything. Use this skill whenever the user asks to check backwards compatibility, review a branch
  for breaking changes, verify merge safety, or assess whether a PR/branch could cause regressions.
  Also trigger when the user says things like "is this safe to merge", "will this break anything",
  "check for breaking changes", "compatibility review", "regression check", or "can I merge this".
  Even if they don't use the exact phrase "backwards compatibility", if they're asking whether
  changes on one branch could break existing functionality on another, this is the right skill.
---

# Backwards Compatibility Checker

You are performing a thorough backwards compatibility review of a branch against a target branch. Your job is to determine whether merging the source branch into the target branch could break anything that currently works on the target branch.

This is not a general code review. You are looking at changes exclusively through the lens of: **"Could this break existing behavior?"** Every finding should answer that question.

## Setup

Start by establishing the branches:

1. Ask the user which branch to check if not obvious from context. The **source branch** is the one with new changes (usually the current branch). The **target branch** is where it would merge into (usually `main`).

2. Get the full diff:
   ```bash
   git diff <target-branch>...<source-branch>
   ```

3. Get the list of changed files:
   ```bash
   git diff --name-status <target-branch>...<source-branch>
   ```

4. Checkout or read both versions of critical files as needed throughout the review. When you need to see a file as it exists on the target branch:
   ```bash
   git show <target-branch>:<filepath>
   ```

## The Review

Work through each of the following categories systematically. Not every category will apply to every diff — skip categories that are clearly irrelevant, but err on the side of checking. The goal is to catch real breakage risks, not to generate noise.

### 1. Removed or Renamed Symbols

Look for functions, classes, methods, variables, constants, types, interfaces, or modules that were **removed or renamed** in the diff.

For each one found:
- Search the target branch codebase for usages: `git grep <symbol> <target-branch>`
- If the symbol is used elsewhere, this is a **breaking change**
- If renamed, check whether all call sites were updated in the same diff

This is the most common source of breakage. Be thorough here — check exports, re-exports, and public API surfaces carefully.

### 2. Changed Function Signatures

Look for functions or methods whose signatures changed:
- Added required parameters (breaks existing callers)
- Removed parameters (may break callers passing them)
- Changed parameter order
- Changed parameter types or return types
- Changed from sync to async or vice versa
- Changed error types or exception types thrown
- Narrowed input types or widened output types in a way that breaks callers

For each signature change, trace callers on the target branch to see if they'd break.

### 3. Changed Interfaces, Types, and Contracts

Look for changes to:
- Interface or type definitions (removed fields, changed field types, new required fields)
- Protocol buffers, GraphQL schemas, OpenAPI specs
- Abstract base classes or traits (new required methods)
- Enum values (removed, reordered if ordinal matters, renamed)

These are especially dangerous because they can cause compile-time or runtime failures across many files at once.

### 4. Behavioral Changes in Shared Code

This is the subtlest category. Look for changes to the **behavior** of existing functions — not just their signatures. Things like:
- A utility function that now returns a different format or value range
- Changed default values for optional parameters
- Changed error handling (now throws where it used to return null, or vice versa)
- Changed ordering of results (sorting, iteration order)
- Changed side effects (a function that used to write to a file no longer does, or now writes to a different location)
- Modified validation logic (now rejects inputs that were previously accepted, or vice versa)
- Changed event emission (removed events, changed event payloads)

For each behavioral change, consider: **who calls this code, and would they break?** Read the callers on the target branch to understand their assumptions.

### 5. Database and Schema Changes

Look for:
- Migration files that drop columns, rename tables, or change column types
- ORM model changes that don't match migration state
- Changed database queries that assume old schema
- Removed or renamed indexes
- Changes to seed data or fixtures that other code depends on

Schema changes are high-risk because they often can't be rolled back easily.

### 6. Configuration and Environment Changes

Look for:
- Removed or renamed environment variables
- Changed config file formats or keys
- New required configuration without defaults
- Changed feature flags or their default states
- Modified CI/CD pipeline configurations that could affect deployment

### 7. File and Module Structure Changes

Look for:
- Deleted files that are imported elsewhere
- Moved files without updating all import paths
- Changed module export structures (e.g., switching from default to named exports)
- Changed package entry points
- Renamed directories that are referenced in configs or imports

Use `git grep` on the target branch to find references to removed/moved paths.

### 8. Dependency Changes

Look for:
- Removed dependencies that other code imports
- Major version bumps of dependencies (may introduce their own breaking changes)
- Changed peer dependency requirements
- Lock file changes that could alter transitive dependency versions

### 9. API and Protocol Changes

Look for changes to:
- REST endpoints (removed routes, changed request/response shapes, changed status codes)
- GraphQL schema (removed fields, changed types)
- WebSocket message formats
- RPC definitions
- Serialization formats (JSON keys renamed, fields removed)

If the codebase has both client and server code, check that changes to one side are reflected in the other.

### 10. Test Impact Analysis

After completing the static analysis above:
- Identify existing tests on the target branch that exercise changed code
- Assess whether those tests would fail after the merge
- If the project has a test suite that can be run, offer to run it:
  ```bash
  # Run the target branch's test suite against the merged code
  git stash  # if needed
  git merge --no-commit <source-branch>
  <run test command>
  git merge --abort
  ```
- Note any tests that were deleted or modified in the source branch — removing tests can hide breakage

## Producing the Report

After completing the review, produce a structured report. Be specific — cite file paths, line numbers, function names, and the exact nature of each risk.

### Report Structure

```
# Backwards Compatibility Report
## Branch: <source> → <target>

## Summary
<One paragraph: overall risk assessment — Safe / Low Risk / Medium Risk / High Risk / Breaking>

## Breaking Changes
<Changes that WILL break existing code on the target branch. Each item includes:
 - What changed
 - Where it's used (with file paths and line numbers on the target branch)
 - Why it breaks>

## Potential Breaking Changes
<Changes that MIGHT break existing code, depending on runtime conditions, configuration,
 or usage patterns that couldn't be fully verified statically. Each item includes:
 - What changed
 - Why it might break
 - What would need to be true for it to break>

## Safe Changes
<Brief summary of changes reviewed and confirmed safe — new additions, internal-only
 refactors with no external callers, additive-only changes, etc.>

## Recommendations
<Specific suggestions for making the merge safer, e.g.:
 - "Add an alias for the old function name to maintain compatibility"
 - "Run the migration on a staging database first"
 - "Update callers in X, Y, Z files before merging"
 - "Add a deprecation warning instead of removing outright">
```

### Severity Definitions

- **Safe**: All changes are additive or internal-only. No existing code on the target branch would be affected.
- **Low Risk**: Minor changes with limited blast radius. A handful of callers might need updates, but failures would be obvious and easy to fix.
- **Medium Risk**: Significant changes that affect shared code. Multiple callers or modules could break. Careful review and testing recommended before merge.
- **High Risk**: Broad changes to core interfaces, schemas, or widely-used utilities. High probability of breakage across multiple parts of the codebase.
- **Breaking**: Confirmed breaking changes found — existing code on the target branch WILL fail after merge without additional fixes.

## Important Principles

- **Be specific, not speculative.** Every finding should point to concrete code. "This might break something" is not useful. "Removing `getUserById` in `src/db/users.ts:45` will break the 3 callers in `src/api/routes.ts:12,78,134`" is useful.

- **Trace actual usage.** Don't flag a removed function as breaking if nothing on the target branch calls it. Use `git grep` to verify.

- **Consider transitive breakage.** If function A calls function B, and B's behavior changes, A's callers may break even though A wasn't touched. Follow the call chain.

- **Distinguish "will break" from "might break."** A removed export that's imported elsewhere is a confirmed break. A changed default value in a config is a potential break. Categorize accordingly.

- **Additive changes are usually safe.** New files, new functions, new optional parameters with defaults, new endpoints — these don't break existing code. Note them as safe and move on. Don't waste time on things that are obviously fine.

- **Read the actual code.** Don't just look at the diff in isolation. Read the surrounding code on both branches to understand context, caller expectations, and whether a change is truly breaking.

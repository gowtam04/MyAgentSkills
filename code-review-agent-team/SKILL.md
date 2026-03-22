---
name: code-review-agent-team
description: Review and fix code using a coordinated agent team. Use this skill whenever the user wants to review and fix their code, resolve code review findings, or address issues from a code review. Trigger on phrases like "review and fix my code", "find and fix issues", "do a review pass", "fix the review issues", "address the findings", "resolve the P0s", "fix what the review found". This skill can either run the full loop (review → fix → verify) or start from existing review findings. It uses Claude Code Agent Teams with separate fixer and reviewer teammates — fixers never review their own work. Even if the user just pastes numbered issues with file paths and says "fix these", use this skill.
---

# Code Review Agent Team

This skill uses Claude Code Agent Teams to review code, fix issues, and independently verify every fix. Fixers fix, a separate reviewer verifies by running `/review` — these roles never overlap. Every fix goes through a fix → independent re-review → refix loop until the issue is definitively resolved.

The skill supports two entry points:
- **Full loop**: the user asks to review and fix their code. The skill runs `/review` first, then fixes what it finds.
- **Fix only**: the user already has review findings (from running `/review` themselves). The skill parses the existing findings and starts fixing.

**Requires Agent Teams.** This skill uses Claude Code Agent Teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`). If the feature is not enabled, tell the user they need to enable it by adding `"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"` to the `env` section of their `settings.json`, then restart Claude Code.

## CRITICAL: Use Agent Teams, NOT Subagents

This skill uses Claude Code's **Agent Teams** feature — NOT regular subagents (the Task tool). You MUST use the Agent Teams tooling: the team creation tool, teammate spawning tool, shared task list with dependency tracking, and the mailbox messaging system for peer-to-peer communication between teammates.

Do NOT use the Task tool to dispatch work. Subagents are fire-and-forget workers that can only report back to a single parent. Agent Teams enable real coordination — teammates share findings, claim tasks from the shared list, and message each other directly.

**Every worker in this skill — the reviewer, the foundational fixer, and all domain fixers — must be spawned as agent team teammates, never as subagents.**

## CRITICAL: Reviewer Must Use the Code-Review Skill

Whenever the reviewer teammate runs a review (in Step 0, Stage 2, Stage 4, Stage 5, or Step 5), it must invoke Claude Code's `/review` command — the same code-review skill that produces the original findings. The reviewer does NOT do a manual read-through and give its own opinion. It runs `/review` and reports what `/review` found. This is what makes the verification independent and repeatable.

## Detecting the Entry Point

Check whether `/review` output already exists in the conversation. If there's a numbered issue list with GitHub permalink URLs in the chat above, the user already has findings — go to **Step 1: Parse and Normalize**.

If no review findings exist in the conversation, the user wants the full loop — go to **Step 0: Initial Review**.

## Review Format

Claude Code's `/review` produces a numbered list of issues with descriptions and GitHub permalink URLs:

```
Code review

  Found N issues:

  1. Short title of the issue (context about why it matters).
     Description spanning one or more lines.

     https://github.com/org/repo/blob/sha/path/to/file.ext#L10-L28
```

**Parsing rules:**
- **Issue number**: integer before the `.` at the start of the item
- **Title**: the first sentence of the item (up to the first period or parenthetical)
- **File path**: extracted from the GitHub URL — the path between `/blob/<sha>/` and `#L`
- **Line range**: from the URL anchor `#L<start>-L<end>`. If only `#L<start>`, single line.
- **Description**: all text between the title and the URL(s)
- **Severity**: not explicitly tagged by `/review`. Infer from description keywords:
  - P0: "security", "missing auth", "missing access control", "regression", "blocking", "data exposure"
  - P1: "wrong", "incorrect", "misfire", "bug", "breaks", "UTC instead of"
  - P2: "style", "naming", "minor", "cleanup", "formatting"
  - When in doubt, default to P1.
- Multiple URLs may appear if the issue spans multiple files — capture all of them

## Workflow Overview

```
Step 0: Initial Review (only if no findings exist)
  Lead asks user about review scope → spawns reviewer → reviewer runs /review
         │
Step 1: Parse and Normalize
         │
Step 2: Present Findings and Plan Fixes (user approves before any fixing starts)
         │
Step 3: Assign Domains and Create Team
         │
Step 4: Execute
  Stage 1: Foundational fixer applies blocking fixes
  Stage 2: Reviewer verifies foundational fixes with /review
  Stage 3: Domain fixers apply remaining fixes in parallel
  Stage 4: Reviewer verifies all fixes with /review
  Stage 5: Fix-review loop if reviewer caught problems
         │
Step 5: Final Full /review
         │
Step 6: Summary Report
```

## Step 0: Initial Review

Skip this step if review findings already exist in the conversation.

Before spawning any teammates, the lead must ask the user about the scope of the review:
- What should be reviewed? (staged changes, uncommitted changes, specific directory, entire repo, etc.)
- Are there any areas to focus on or exclude?

Do not assume the scope. Wait for the user's answer before proceeding.

Once the user specifies the scope, create the agent team and spawn the reviewer as a **teammate** (not a subagent) with instructions to run `/review` with that scope. The reviewer must invoke the `/review` command — not do a manual code read. After the reviewer completes, **shut it down** — it will be re-spawned later for verification.

The lead then takes the review output and proceeds to Step 1.

## Step 1: Parse and Normalize

Read the review output (from Step 0 or from the conversation) and extract a normalized list of issues. Each issue needs:

- **id**: sequential number from the review
- **title**: short summary
- **severity**: `P0` (blocking/security — highest impact), `P1` (significant bugs), `P2` (minor/style) — inferred from description
- **file_path**: relative path to the affected file
- **line_range**: start and end lines from the GitHub URL anchor
- **description**: the full explanation of what's wrong and why
- **risk_level**: `low`, `medium`, or `high` — this is about the *fix*, not the *bug* (see Risk Classification below)
- **domain**: which area of the codebase this file belongs to (see Step 3)

## Step 2: Present Findings and Plan Fixes

**The user must approve before any fixing starts.** This step is the gate between reviewing and fixing.

First, present the parsed issues to the user as a numbered summary so they can:
- Confirm the issues are real
- Exclude issues they don't want fixed
- Re-prioritize severity
- Add context the review might have missed

Then, check for project configuration files that inform the fix approach:

- `CLAUDE.md` — project conventions, architecture notes, and rules
- `package.json` / `Podfile` / `Cargo.toml` — dependency and script information
- `.eslintrc` / `tsconfig.json` / `swiftlint.yml` — code style and compiler settings
- Existing test structure — understand how and where tests live

For each approved issue, think through the fix *before* writing any code. Your plan should cover:

- **What** specifically needs to change (which functions, queries, types, etc.)
- **Where** the change touches (just one file? multiple files? does it cascade?)
- **Why** this fix is correct (connect it back to the issue description)
- **Risks** of the fix itself (could it break something else? does it change a public API?)

Present the fix plan to the user grouped by risk level:
1. **Low-risk fixes** — "I'll apply these automatically unless you object" (list them)
2. **Medium-risk fixes** — "Here's my plan for each; let me know if you want changes" (show plans)
3. **High-risk fixes** — "These need your approval before I proceed" (show detailed plans with reasoning)

**Wait for user confirmation before proceeding to Step 3.**

## Step 3: Assign Domains and Create Team

### What is a domain?

A domain is an independent area of the codebase where a fixer can work without editing files that another fixer is also touching. Domains are determined by the project's directory structure and language boundaries.

The test is simple: **can two fixers work on these areas simultaneously without editing the same files?** If yes, they're separate domains.

Examples:
- `db/migrations/` (SQL) and `server/` (Python API) and `web/` (React frontend) → 3 domains
- `ios/` (Swift) and `android/` (Kotlin) and `api/` (Node backend) → 3 domains
- `ios/` (Swift) and `android/` (Kotlin) → 2 domains (separate codebases, separate files)
- A Flutter or React Native app where iOS and Android share source code → 1 domain (same files)
- `.github/` (CI/CD) and `infra/` (Terraform) and `src/` (application code) → 3 domains
- `frontend/` and `backend/` → 2 domains

To identify domains, look at the file paths across all issues and group them by the top-level directory (or first two levels if needed). Each group that uses different files is a domain.

### Identify foundational issues

Some issues must be fixed before others because downstream code depends on them:
- Database migrations (schema changes, stored procedures, access policies)
- Shared type definitions, interfaces, or API contracts
- Any issue where the root cause is in a file that multiple other issues reference

Separate these from the domain-specific issues. They'll be fixed first in Stage 1.

### Team composition

- **Lead (you)**: Coordinates the team. Spawns and shuts down teammates. Presents findings and plans to the user. Does NOT write code or apply fixes — only coordinates.
- **Foundational fixer**: Fixes blocking/foundational issues sequentially in Stage 1. Runs smoke checks (type checking, tests) but does NOT run `/review`. If there are no foundational issues, skip this role.
- **Domain fixers** (1 per domain): Each owns all non-foundational issues in their domain. Applies fixes and runs smoke checks, but does NOT run `/review`. If all issues are in one domain, there's one domain fixer.
- **Reviewer**: A separate teammate (NOT a subagent) that uses Claude Code's `/review` command to verify fixes. Every time the reviewer checks fixes, it must invoke `/review` — not do a manual read-through. This teammate does NOT fix code — it only runs `/review`, inspects cross-layer contracts, and reports findings.

### Concurrency rules
- No more than 3 active teammates at a time
- Two teammates must never edit the same file
- Shut down a teammate as soon as their tasks are complete

### Model requirement
All teammates must use the **user's default selected model**. When spawning teammates, do not override or downgrade the model — every teammate should run on the same model the user has configured for their Claude Code session.

## Step 4: Execute

### Stage 1: Foundational Fixes

Skip this stage if there are no foundational issues.

Spawn the foundational fixer with the blocking issues. Give them:
- The specific foundational issues with full descriptions and file paths
- Project context: path to CLAUDE.md, relevant config files, test commands
- Instructions to apply each fix and run smoke checks (type checking, linting, tests) — but NOT `/review`
- What to produce: write results to `fix-results/foundational-results.md` with what was changed per issue

The foundational fixer works through these issues sequentially. After all foundational fixes are applied, **shut down the foundational fixer**.

### Stage 2: Review Foundational Fixes

Skip this stage if Stage 1 was skipped.

Spawn the reviewer as a **teammate** to verify foundational fixes before domain fixers start. Domain fixers' work depends on these fixes being correct — if a schema change is wrong, everything built on top of it will be wrong too.

**Spawn prompt for the reviewer must include:**
- Instruction to invoke the `/review` command across all files modified in Stage 1 (not a manual read — the actual `/review` command)
- The original review findings for the foundational issues
- The foundational fixer's results file

**The reviewer runs `/review` and checks:**
1. Does any foundational issue still appear in the output? If so, the fix didn't work.
2. Did any fix introduce new issues?

**If the reviewer finds problems:**
1. Re-spawn the foundational fixer as a **teammate** with the reviewer's exact findings
2. After the fixer revises, shut them down and re-spawn the reviewer as a **teammate** to re-check
3. Maximum 3 fix-review cycles. After 3 rounds, mark remaining issues UNRESOLVED.

Only proceed to Stage 3 when all foundational issues are CONFIRMED FIXED or marked UNRESOLVED.

### Stage 3: Domain-Specific Fixes

Spawn domain fixers in parallel (one per domain) for remaining issues. In the spawn prompt, give each fixer:

- **Their role**: which domain they own, which files are theirs
- **Their issues**: specific issue IDs, titles, descriptions, file paths, and line ranges
- **The foundational context**: what was already fixed in Stages 1–2 and how it affects their work
- **Project context**: path to CLAUDE.md, relevant config files, test commands
- **Instructions**: apply fixes and run smoke checks (type checking, linting, tests) — but NOT `/review`. The reviewer will verify separately.
- **Ordering**: fix P0 issues first, then P1, then P2. Fix foundational dependencies before downstream consumers.
- **What to produce**: for each issue, write results to `fix-results/{domain}-results.md` with: issue ID, what was changed, and smoke check results

After all domain fixers complete, **shut them all down**.

### Stage 4: Review All Fixes

Spawn the reviewer as a **teammate** to do the comprehensive verification pass.

**Spawn prompt for the reviewer must include:**
- Instruction to invoke the `/review` command across ALL files modified during Stages 1–3 (not a manual read — the actual `/review` command)
- The original review findings (all issues, with IDs and descriptions)
- The results files from the foundational fixer and each domain fixer
- The list of all modified files

**The reviewer does two things:**

**First: run `/review` across ALL modified files.** This is an independent re-review using the same tool that produced the original findings. The reviewer checks:
1. Does any original issue still appear? If so, the fixer's fix didn't work.
2. Did any fix introduce new issues?

**Second: cross-layer contract inspection.** `/review` examines files individually and might not catch contract mismatches that span domains (each file looks fine on its own, but they disagree with each other). For each issue that spans multiple domains:
1. Read the fix in every modified file for that issue
2. Trace data flow across boundaries: does the caller send what the callee expects? Do types, column names, and serialization formats all agree?

The reviewer writes all findings to `fix-results/cross-domain-review.md`.

**Reviewer verdict per issue:**
- **CONFIRMED FIXED**: `/review` doesn't flag it and cross-layer contracts are consistent.
- **CROSS-LAYER MISMATCH**: fix is correct within its domain but mismatches another layer. Describe what doesn't align.
- **NOT FIXED**: `/review` still flags it. Describe why.

### Stage 5: Fix What the Reviewer Caught

If the reviewer found problems:
1. The lead re-spawns the appropriate fixer(s) as **teammates** with the reviewer's exact finding
2. After the fixer revises, shut them down
3. Re-spawn the reviewer as a **teammate** to invoke `/review` on the re-modified files and re-check the specific issues that had problems
4. **Maximum 3 review-fix cycles.** After 3 rounds, mark remaining issues UNRESOLVED.

### Shutting Down the Team

After all issues reach CONFIRMED FIXED or UNRESOLVED:
1. Shut down all remaining teammates from the lead session
2. The lead runs a final full test suite
3. Proceed to Step 5

## Step 5: Final Full /review

Spawn the reviewer one last time as a **teammate** to invoke `/review` across ALL files modified during the session. This catches interaction effects between fixes that per-issue verification might miss — things like fix A changing a return type that fix B's code depends on.

1. **Reviewer invokes `/review`** across all modified files
2. **Lead runs the full test suite** — all tests, not just the ones touched by fixes
3. **Lead runs type checking / linting** for every language in the affected files

**Evaluate the reviewer's output:**
- **No original issues reappear, no new issues**: all fixes are confirmed. Shut down the reviewer, proceed to Step 6.
- **An original issue reappears**: that fix regressed or was invalidated by another fix. Re-spawn the appropriate fixer as a **teammate**, then re-spawn the reviewer to verify (max 3 cycles).
- **New issues in modified code**: a fix introduced a regression. If blocking, fix it. If minor, note it in the summary.
- **New issues in unmodified code**: `/review` found something the original review missed. Note it in the summary but don't fix it unless the user asks.

This is the last gate. Nothing gets reported as FIXED unless it survived this final `/review`.

## Step 6: Summary Report

Present a summary covering:

- **Issue tally**: X found, Y confirmed fixed (verified by `/review`), Z unresolved (with reasons)
- **Per-issue summary**: what was changed, where, and confirmation that `/review` no longer flags it
- **Fix cycles**: for issues that needed multiple attempts, what `/review` flagged each cycle and what ultimately resolved it
- **Unresolved issues**: what was tried, what `/review` is still flagging, and what the user should do next
- **New issues discovered**: anything noticed during fixing that wasn't in the original review
- **Test results**: what passed, what failed, what wasn't testable
- **Team composition**: which teammates were spawned and what each one handled
- **Recommended follow-ups**: things to manually verify or test in a real environment

---

## Risk Classification

Risk is about the *fix complexity and blast radius*, not the bug severity. A P0 security bug might have a low-risk fix (add one line of auth check), and a P2 style issue might have a high-risk fix (rename a widely-used function).

**Low risk** — auto-apply:
- Adding a missing null check, guard clause, or auth check to an existing function
- Fixing a column/field name typo in a query (when the correct name is unambiguous)
- Correcting a date format or timezone conversion
- Adding missing access control policies that follow the same pattern as existing ones
- Fixing an obvious copy-paste error

**Medium risk** — show plan, apply after confirmation:
- Changing function signatures or API contracts (callers must be updated too)
- Modifying data serialization (JSON vs string, encoding changes)
- Altering control flow (if/else branches, early returns, error handling paths)
- Changes that touch 3+ files
- Anything involving business logic interpretation

**High risk** — require explicit approval:
- Schema changes (adding/removing columns, changing types)
- Architectural refactors (splitting functions, changing data flow)
- Security model changes (access control policies, auth patterns, permission systems)
- Changes where the "correct" fix requires understanding product intent
- Anything the review describes as needing a design decision

## Edge Cases and Judgment Calls

- **Ambiguous intent**: If the review says something is wrong but doesn't specify the fix direction, present options to the user rather than guessing. For example: "This endpoint is missing an auth check. I can either (a) add user validation inside the handler, or (b) add auth middleware to the route. Which approach fits your auth model?"

- **Cascading fixes**: Some issues are symptoms of the same root cause. If fixing issue #1 also fixes issues #3 and #5, say so upfront — but the reviewer must still confirm all three issues are gone via `/review`. Don't assume a cascading fix worked without checking.

- **Incomplete information**: If you need to see a file that wasn't mentioned in the review, or need to understand a pattern used elsewhere in the codebase, go look. Don't guess at conventions — read the code.

- **Contradictory fixes**: If two review items suggest conflicting changes, flag the conflict and ask the user to decide. Never silently pick one over the other.

- **/review still flags it after 3 cycles**: If the reviewer has flagged the same issue 3 times and fixers can't resolve it, don't rationalize it away. The reviewer is probably right and the fix approach is wrong. Document exactly what `/review` is saying, mark it UNRESOLVED, and let the user decide the next step.

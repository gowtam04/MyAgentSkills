---
name: code-review-agent-team
description: Review and fix code using a coordinated agent team. Use this skill whenever the user wants to review and fix their code, resolve code review findings, or address issues from a code review. Trigger on phrases like "review and fix my code", "find and fix issues", "do a review pass", "fix the review issues", "address the findings", "resolve the P0s", "fix what the review found". This skill can either run the full loop (review → fix → verify) or start from existing review findings. It uses Claude Code Agent Teams with separate fixer and reviewer teammates — fixers never review their own work. Even if the user just pastes numbered issues with file paths and says "fix these", use this skill.
---

# Code Review Agent Team

This skill uses Claude Code Agent Teams to review code, fix issues, and independently verify every fix. Fixers fix, two independent reviewers verify in parallel — one runs Claude Code's `/review` and the other runs `/codex:review` (or `/codex:adversarial-review` for high-stakes items) — reviewer and fixer roles never overlap. Every fix goes through a fix → independent dual re-review → refix loop until the issue is definitively resolved.

The skill supports two entry points:
- **Full loop**: the user asks to review and fix their code. The skill runs both `/review` and `/codex:review` in parallel first, merges and deduplicates findings, then fixes what they find.
- **Fix only**: the user already has review findings (from running `/review` or `/codex:review` themselves). The skill parses the existing findings and starts fixing.

**Requires Agent Teams.** This skill uses Claude Code Agent Teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`). If the feature is not enabled, tell the user they need to enable it by adding `"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"` to the `env` section of their `settings.json`, then restart Claude Code.

**Requires Codex plugin.** This skill also uses the Codex review plugin for the second reviewer. If `/codex:review` fails or the plugin is not installed, fall back to single-reviewer mode using only `/review` and warn the user. Suggest running `/codex:setup` to configure the Codex CLI.

## CRITICAL: Use Agent Teams, NOT Subagents

This skill uses Claude Code's **Agent Teams** feature — NOT regular subagents (the Task tool). You MUST use the Agent Teams tooling: the team creation tool, teammate spawning tool, shared task list with dependency tracking, and the mailbox messaging system for peer-to-peer communication between teammates.

Do NOT use the Task tool to dispatch work. Subagents are fire-and-forget workers that can only report back to a single parent. Agent Teams enable real coordination — teammates share findings, claim tasks from the shared list, and message each other directly.

**Every worker in this skill — both reviewers (Claude Code Reviewer and Codex Reviewer), the foundational fixer, and all domain fixers — must be spawned as agent team teammates, never as subagents.**

## CRITICAL: Reviewers Must Use Their Designated Review Commands

This skill uses two independent reviewers. Neither reviewer does a manual read-through or gives its own opinion — each invokes its designated review command and reports what it found. This is what makes the verification independent and repeatable.

- **Claude Code Reviewer**: Must invoke `/review` — the same code-review command that produces the original findings. Used in Step 0, Stage 2, Stage 4, Stage 5, and Step 5.
- **Codex Reviewer**: Must invoke `/codex:review` for standard reviews, or `/codex:adversarial-review` for high-stakes items. Used at the same stages as the Claude Code Reviewer, always running in parallel with it.

### When to use adversarial review

The Codex Reviewer uses `/codex:adversarial-review` instead of `/codex:review` when any of the following apply to the items under review:
- P0 severity issues (security, missing auth, data exposure, blocking regressions)
- Security or authentication changes
- Database schema changes or migrations
- Architectural refactors (splitting functions, changing data flow, changing public APIs)
- Any fix classified as high-risk in the Risk Classification section
- Infrastructure scripts (CI/CD, Terraform, deployment configs)
- The final gate review (Step 5) — always use adversarial mode here for maximum scrutiny

For all other reviews, the Codex Reviewer uses `/codex:review`.

## Detecting the Entry Point

Check whether review output already exists in the conversation — from either `/review` or `/codex:review`. If there's a numbered issue list with GitHub permalink URLs or Codex review findings in the chat above, the user already has findings.

- If findings from **both** reviewers exist, go to **Step 1: Parse and Normalize** with the merged findings.
- If findings from **only one** reviewer exist, ask the user if they want to run the other reviewer for a more complete picture. If they decline, proceed with single-reviewer findings to **Step 1**. If they agree, spawn the missing reviewer, then merge and proceed.
- If **no** review findings exist, the user wants the full loop — go to **Step 0: Initial Review**.

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

### Codex Review Output

The Codex Reviewer's output (from `/codex:review` or `/codex:adversarial-review`) may use a different format than `/review`. The lead should parse Codex findings by:
- Extracting file paths and line numbers from whatever format Codex produces
- Mapping descriptions to the same normalized structure used for `/review` findings
- If Codex does not produce GitHub permalink URLs, constructing file path + line range from the Codex output directly

Codex findings are merged with `/review` findings using the deduplication procedure described in the Finding Merge section below.

## Workflow Overview

```
Step 0: Initial Review (only if no findings exist)
  Lead asks user about review scope → spawns both reviewers in parallel
    → Claude Code Reviewer runs /review
    → Codex Reviewer runs /codex:review
  Lead merges and deduplicates findings
         │
Step 1: Parse and Normalize (merged findings from both reviewers)
         │
Step 2: Present Findings and Plan Fixes (user approves before any fixing starts)
         │
Step 3: Assign Domains and Create Team
         │
Step 4: Execute
  Stage 1: Foundational fixer applies blocking fixes
  Stage 2: Both reviewers verify foundational fixes in parallel
    → Claude Code Reviewer runs /review
    → Codex Reviewer runs /codex:review (or /codex:adversarial-review for high-stakes)
  Stage 3: Domain fixers apply remaining fixes in parallel
  Stage 4: Both reviewers verify all fixes in parallel
    → Claude Code Reviewer runs /review + cross-layer inspection
    → Codex Reviewer runs /codex:review (or /codex:adversarial-review for high-stakes)
  Stage 5: Fix-review loop if either reviewer caught problems
         │
Step 5: Final Full Dual Review
    → Claude Code Reviewer runs /review
    → Codex Reviewer runs /codex:adversarial-review (always adversarial at final gate)
         │
Step 6: Summary Report (findings attributed by reviewer source)
```

## Step 0: Initial Review

Skip this step if review findings already exist in the conversation.

Before spawning any teammates, the lead must ask the user about the scope of the review:
- What should be reviewed? (staged changes, uncommitted changes, specific directory, entire repo, etc.)
- Are there any areas to focus on or exclude?

Do not assume the scope. Wait for the user's answer before proceeding.

Once the user specifies the scope, create the agent team and spawn **two reviewers** as teammates (not subagents), running in parallel:

1. **Claude Code Reviewer** — instructed to run `/review` with the specified scope
2. **Codex Reviewer** — instructed to run `/codex:review` with the specified scope

Both reviewers run concurrently. After both complete, **shut both down** — they will be re-spawned later for verification.

The lead then takes the outputs from both reviewers, merges and deduplicates them (see Finding Merge below), and proceeds to Step 1.

## Finding Merge and Deduplication

Whenever the lead receives findings from both reviewers (in Step 0, Stage 2, Stage 4, Stage 5, or Step 5), it must merge and deduplicate them before proceeding.

### Deduplication criteria

Two findings are considered duplicates when **all three** conditions are met:
1. **Same file**: both findings reference the same file path
2. **Overlapping line range**: the line ranges overlap or are within 5 lines of each other
3. **Similar description**: the issue descriptions address the same underlying problem (even if worded differently)

### Merge procedure

1. Start with the Claude Code Reviewer's findings as the primary list (since `/review` produces the structured numbered format the rest of the skill depends on).
2. For each Codex Reviewer finding, check if it duplicates a Claude Code finding using the three criteria above.
3. **If duplicate**: annotate the existing finding with "Also flagged by Codex Reviewer" and append any additional context the Codex finding provides that the Claude Code finding does not.
4. **If unique** (not a duplicate): add it to the list as a new finding with the next sequential ID. Note "Source: Codex Reviewer" on the finding.
5. The merged list becomes the canonical finding list used in all subsequent steps.

### Source tracking

Every finding in the normalized list carries a `source` field:
- `claude-review` — found only by the Claude Code Reviewer
- `codex-review` — found only by the Codex Reviewer
- `both` — found by both reviewers independently

This field is used in the Step 6 summary report to show reviewer agreement.

## Step 1: Parse and Normalize

Read the merged review output (from Step 0 or from the conversation) and extract a normalized list of issues. Each issue needs:

- **id**: sequential number from the review
- **title**: short summary
- **severity**: `P0` (blocking/security — highest impact), `P1` (significant bugs), `P2` (minor/style) — inferred from description
- **file_path**: relative path to the affected file
- **line_range**: start and end lines from the GitHub URL anchor
- **description**: the full explanation of what's wrong and why
- **risk_level**: `low`, `medium`, or `high` — this is about the *fix*, not the *bug* (see Risk Classification below)
- **domain**: which area of the codebase this file belongs to (see Step 3)
- **source**: `claude-review`, `codex-review`, or `both` — which reviewer(s) flagged this issue

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

- **Lead (you)**: Coordinates the team. Spawns and shuts down teammates. Presents findings and plans to the user. Merges and deduplicates findings from both reviewers. Does NOT write code or apply fixes — only coordinates.
- **Foundational fixer**: Fixes blocking/foundational issues sequentially in Stage 1. Runs smoke checks (type checking, tests) but does NOT run any review commands. If there are no foundational issues, skip this role.
- **Domain fixers** (1 per domain): Each owns all non-foundational issues in their domain. Applies fixes and runs smoke checks, but does NOT run any review commands. If all issues are in one domain, there's one domain fixer.
- **Claude Code Reviewer**: A separate teammate (NOT a subagent) that uses Claude Code's `/review` command to verify fixes. Every time it checks fixes, it must invoke `/review` — not do a manual read-through. This teammate does NOT fix code — it only runs `/review`, inspects cross-layer contracts, and reports findings.
- **Codex Reviewer**: A separate teammate (NOT a subagent) that uses the Codex review plugin to verify fixes. For standard reviews it runs `/codex:review`. For high-stakes items (see "When to use adversarial review" above), it runs `/codex:adversarial-review`. This teammate does NOT fix code — it only runs Codex review commands and reports findings.

Both reviewers are always spawned and shut down together. They run their reviews in parallel at every review stage.

### Concurrency rules
- No more than 4 active teammates at a time (review stages require 2 reviewer slots, leaving 2 slots for concurrent fixers during fix-review loops; during fix-only stages like Stage 1 and Stage 3, all 4 slots are available for fixers)
- Two teammates must never edit the same file (this applies to fixers — reviewers are read-only and don't edit files)
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

Spawn **both reviewers** as teammates in parallel to verify foundational fixes before domain fixers start. Domain fixers' work depends on these fixes being correct — if a schema change is wrong, everything built on top of it will be wrong too.

**Spawn prompts for both reviewers must include:**
- The original review findings for the foundational issues
- The foundational fixer's results file

**Claude Code Reviewer:** instructed to invoke `/review` across all files modified in Stage 1.

**Codex Reviewer:** instructed to invoke `/codex:review` across the same files. Use `/codex:adversarial-review` if any foundational fix involves schema changes, migrations, security model changes, or is classified as high-risk.

**Both reviewers check:**
1. Does any foundational issue still appear in their output? If so, the fix didn't work.
2. Did any fix introduce new issues?

The lead merges findings from both reviewers using the deduplication procedure.

**If either reviewer finds problems:**
1. Re-spawn the foundational fixer as a **teammate** with the merged findings from both reviewers
2. After the fixer revises, shut them down and re-spawn **both reviewers** as teammates to re-check
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

Spawn **both reviewers** as teammates in parallel to do the comprehensive verification pass.

**Spawn prompts for both reviewers must include:**
- The original review findings (all issues, with IDs and descriptions)
- The results files from the foundational fixer and each domain fixer
- The list of all modified files

**Claude Code Reviewer** does two things:

**First: run `/review` across ALL modified files.** This is an independent re-review using the same tool that produced the original findings. It checks:
1. Does any original issue still appear? If so, the fixer's fix didn't work.
2. Did any fix introduce new issues?

**Second: cross-layer contract inspection.** `/review` examines files individually and might not catch contract mismatches that span domains (each file looks fine on its own, but they disagree with each other). For each issue that spans multiple domains:
1. Read the fix in every modified file for that issue
2. Trace data flow across boundaries: does the caller send what the callee expects? Do types, column names, and serialization formats all agree?

The Claude Code Reviewer writes findings to `fix-results/cross-domain-review-claude.md`.

**Codex Reviewer** runs `/codex:review` across ALL modified files. For any issue that is P0 severity, involves security/auth, schema/migration, or architectural refactors, it runs `/codex:adversarial-review` specifically targeting those files. The Codex Reviewer writes findings to `fix-results/cross-domain-review-codex.md`.

The lead merges findings from both reviewers into `fix-results/cross-domain-review.md` using the deduplication procedure.

**Reviewer verdict per issue** — an issue is only CONFIRMED FIXED when **neither** reviewer flags it:
- **CONFIRMED FIXED**: neither `/review` nor `/codex:review` flags it and cross-layer contracts are consistent.
- **CROSS-LAYER MISMATCH**: fix is correct within its domain but mismatches another layer. Describe what doesn't align.
- **NOT FIXED**: one or both reviewers still flag it. Note which reviewer(s) and describe why.

### Stage 5: Fix What Either Reviewer Caught

If either reviewer found problems:
1. The lead merges and deduplicates findings from both reviewers, then re-spawns the appropriate fixer(s) as **teammates** with the merged findings
2. After the fixer revises, shut them down
3. Re-spawn **both reviewers** as teammates in parallel to re-check the specific issues that had problems — each reviewer should verify that the concerns it originally raised are now addressed
4. **Maximum 3 review-fix cycles.** After 3 rounds, mark remaining issues UNRESOLVED.

### Shutting Down the Team

After all issues reach CONFIRMED FIXED or UNRESOLVED:
1. Shut down all remaining teammates (both reviewers, all fixers) from the lead session
2. The lead runs a final full test suite
3. Proceed to Step 5

## Step 5: Final Full Dual Review

Spawn **both reviewers** one last time as teammates in parallel across ALL files modified during the session. This catches interaction effects between fixes that per-issue verification might miss — things like fix A changing a return type that fix B's code depends on.

1. **Claude Code Reviewer invokes `/review`** across all modified files
2. **Codex Reviewer invokes `/codex:adversarial-review`** across all modified files — always use adversarial mode at this final gate for maximum scrutiny, regardless of whether the items are individually high-stakes
3. **Lead runs the full test suite** — all tests, not just the ones touched by fixes
4. **Lead runs type checking / linting** for every language in the affected files

The lead merges findings from both reviewers using the deduplication procedure.

**Evaluate the merged output from both reviewers:**
- **No original issues reappear in either reviewer's output, no new issues**: all fixes are confirmed. Shut down both reviewers, proceed to Step 6.
- **An original issue reappears in either reviewer's output**: that fix regressed or was invalidated by another fix. Re-spawn the appropriate fixer as a **teammate**, then re-spawn **both reviewers** to verify (max 3 cycles).
- **New issues in modified code**: a fix introduced a regression. If blocking, fix it. If minor, note it in the summary. Attribute the finding to the reviewer that caught it.
- **New issues in unmodified code**: a reviewer found something the original review missed. Note it in the summary but don't fix it unless the user asks.

This is the last gate. Nothing gets reported as FIXED unless it survived this final dual review from **both** reviewers.

## Step 6: Summary Report

Present a summary covering:

- **Issue tally**: X found (Y by `/review`, Z by `/codex:review`, W by both), N confirmed fixed (verified by both reviewers), M unresolved (with reasons)
- **Per-issue summary**: what was changed, where, which reviewer(s) originally flagged it (`source` field), and confirmation that neither reviewer flags it now
- **Fix cycles**: for issues that needed multiple attempts, what each reviewer flagged per cycle and what ultimately resolved it
- **Unresolved issues**: what was tried, what each reviewer is still flagging, and what the user should do next
- **New issues discovered**: anything noticed during fixing that wasn't in the original review, attributed to the reviewer that found it
- **Test results**: what passed, what failed, what wasn't testable
- **Team composition**: which teammates were spawned and what each one handled — list both reviewers and how many times `/codex:adversarial-review` was used vs `/codex:review`
- **Reviewer agreement rate**: what percentage of findings were flagged by both reviewers vs only one — this helps the user calibrate how much value the dual review adds
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

- **/review still flags it after 3 cycles**: If a reviewer has flagged the same issue 3 times and fixers can't resolve it, don't rationalize it away. The reviewer is probably right and the fix approach is wrong. Document exactly what each reviewer is saying, mark it UNRESOLVED, and let the user decide the next step.

- **Reviewer disagreement**: If the Claude Code Reviewer marks an issue as CONFIRMED FIXED but the Codex Reviewer still flags it (or vice versa), the issue is NOT confirmed fixed. Present both perspectives to the fixer and prioritize the more specific/detailed finding. If the reviewers genuinely disagree about whether something is a problem, escalate to the user.

- **Codex Reviewer unavailable**: If `/codex:review` fails to run (plugin not installed, Codex CLI not configured, or any runtime error), fall back to single-reviewer mode using only `/review`. Warn the user that dual review is not available and suggest running `/codex:setup` to configure the Codex CLI. Do not block the entire workflow on the Codex Reviewer.

- **Adversarial review false positives**: `/codex:adversarial-review` is intentionally more aggressive and may flag things that are not actual problems — it's designed to question the implementation, not just inspect it. If the adversarial review flags something that the Claude Code Reviewer did not flag and the fix clearly matches the original issue description, the lead should still present it to the fixer but note it as "adversarial-only finding — verify whether this is a genuine concern."

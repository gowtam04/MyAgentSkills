# Light Mode — game tasks without a blueprint

For bounded work with no architecture docs: a bug, a tuning pass, a refactor, an asset tweak, a
feature that touches a handful of files with no new scenes, persistence or asset families, a red
test suite, a frame-rate problem, or research across a codebase. The lead still doesn't write code
or art (the tiny-glue exception still applies), reports are still leads rather than facts, both
finding severities still block, and git works the same way (a branch if you're on the default
branch, and a commit per verified task).

If the task grows past this — several systems, a new scene model, new asset families, decisions the
user should make about player verbs, numbers or feel — stop and recommend `/game-design-document`
and `/game-architecture-blueprint`.

## Kickoff

One AskUserQuestion card: for anything non-trivial, the plan below in a few lines with "Go /
Adjust", including which tasks you've classed as judgment-heavy (Opus implementer) under the main
skill's Model routing. A genuine design decision (a number the GDD doesn't set, how a verb should
feel) goes in the same card as its own question. After that, run straight through.

## The loop

### 1. Name where the tokens will go

Before reading anything yourself, say what's expensive: a big repo search, long logs, broad docs,
repetitive edits, wide test output, many screenshots. Those are the passes to delegate first.
Spend your own reading on the few files that decide the approach.

### 2. Investigate

- Fan out `[explore]` agents for broad sweeps ("where is collision resolved", "every caller of
  `applyDamage`", "what changed in the last 20 commits to the player controller"), and keep their
  conclusions, not their file dumps.
- Read the decisive files yourself. Your judgment is only as good as your understanding, so
  don't design from summaries alone.
- **Bugs: reproduce first.** For a rules bug, a `[test-writer]` writes a failing test that
  reproduces it from the report (not from the suspected fix). For a visual or feel bug, a
  `[playtester]` writes a scratch screenshot script that captures the broken moment, and the
  screenshot is the reproduction. A fix without a reproduction is a guess.
- **Red suites:** have a runner cluster the failures (same root cause? flaky? frame-timing?
  environmental?) before anyone fixes anything.

### 3. Plan

Approach, the decisions and tradeoffs, the files and assets affected, the risks, and how it will be
verified. For multi-task work, or anything the user will want to keep, write it to
`docs/plans/{slug}.md`, because workers can read the plan instead of you retyping it into every
brief.

### 4. Decompose into handoff packets

Split the plan into self-contained tasks with disjoint file ownership. Each worker starts blank, so
the packet carries everything:

- **Objective and fit**: the exact goal and how it fits the plan (point at `docs/plans/{slug}.md`
  if written).
- **Scope**: files, functions and asset paths in scope, and what's explicitly out of scope.
- **Approach and why**: the approach you chose and the reasoning, so the worker doesn't "improve"
  it back into something you rejected.
- **Conventions**: exemplar files to follow; for art, the style-lock paths and
  `references/asset-production.md`.
- **Done means**: which tests must pass, which screenshot must show what, which asset checks must
  pass.
- **Evidence to return**: files touched, commands run with results, screenshot paths, line
  references, uncertainty.
- **Stop conditions**: the code doesn't match the brief, a command keeps failing after one
  reasonable fix, out-of-scope files are needed, or a number or rule isn't in the GDD. Stop and
  report instead of widening the task.

Keep tightly coupled work in one worker rather than splitting it across two that would have to
coordinate. Launch independent tasks together in one message.

### 5. Verify

- Read the actual diff, not the summary. For art, look at the image yourself.
- A fresh `[test-runner]` runs the relevant tests (for a bug, the reproducing test must now pass
  and the rest of the suite must stay green against the baseline).
- A `[reviewer]` reviews any non-trivial diff, or any changed asset with the asset-review lens. You
  check each finding against the code, then all MUST-FIX and SHOULD-FIX items go back to the same
  worker in one `SendMessage` (cap: 3 rounds; escalate a tier after two, per Model routing). For
  judgment-heavy or risky changes, read the diff yourself as well.
- Anything visible gets a `[playtester]` pass with screenshots; feel and audio go in the report as
  `needs-human`.
- Check the result against the plan: did it solve the problem, or only make the symptom go away?

### 6. Commit and report

Commit each verified task with explicit paths. Report the approach and why, what each worker did
and on which model, verification results with commands and screenshot paths, `needs-human` items,
anything left open, and the branch and commits.

## Scenario defaults

- **Rules bug:** explore → reproducing test → fix → reviewer → runner.
- **Visual or feel bug:** explore → reproducing screenshot → fix → reviewer → playtester compares
  before and after → `needs-human` for anything screenshots can't settle.
- **Tuning pass:** the numbers live in data files; a content-author changes them within the ranges
  the GDD allows (or the user sets in the kickoff card) → runner → playtester before and after.
  Never move tunables into code.
- **Asset tweak:** artist (same `method`, same style lock) → asset review → screenshot in game.
- **Refactor:** explore callers → characterization tests of current behavior (if coverage is
  thin) → refactor in disjoint slices → full suite against baseline → smoke and screenshot.
- **Red suite:** runner clusters failures → one worker per root cause → runner re-verifies.
- **Performance:** measure first (a worker records frame time or tick cost under a scripted
  scenario) → change → measure again. Numbers, not impressions.
- **Research question:** parallel explorers from different angles → you synthesize and decide what
  the evidence actually supports. No code changes, no commits.
- **Trivial task** (a rename, a color swap in one asset): say it didn't need a team, and still hand
  it to one worker rather than doing it yourself.

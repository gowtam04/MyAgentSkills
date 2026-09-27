# Light Mode — tasks without a blueprint

For bounded work with no architecture docs: a bug, a refactor, a feature that touches a handful of
files with no new persistence or shared interfaces, a red test suite, a performance problem, or
research across a codebase. The lead still doesn't write code (the tiny-glue exception still
applies), reports are still leads rather than facts, both finding severities still block, and git
works the same way (a branch if you're on the default branch, and a commit per verified task).

If the task grows past this — several domains, a new data model, decisions the user should make
about product behavior — stop and recommend `/claude-spec` and `/claude-architect`.

## Kickoff

One AskUserQuestion card: for anything non-trivial, the plan below in a few lines with "Go /
Adjust", including which tasks you've classed as judgment-heavy (Opus implementer) under the main
skill's Model routing. A genuine product or design decision
goes in the same card as its own question. After that, run straight through.

## The loop

### 1. Name where the tokens will go

Before reading anything yourself, say what's expensive: a big repo search, long logs, broad docs,
repetitive edits, wide test output. Those are the passes to delegate first. Spend your own reading
on the few files that decide the approach.

### 2. Investigate

- Fan out `[explore]` agents for broad sweeps ("where is X handled", "every caller of Y", "what
  changed in the last 20 commits to Z"), and keep their conclusions, not their file dumps.
- Read the decisive files yourself. Your judgment is only as good as your understanding, so
  don't design from summaries alone.
- **Bugs: reproduce first.** Have a `[test-writer]` write a failing test that reproduces the bug
  from the report (not from the suspected fix). A fix without a reproducing test is a guess. This
  is spec-first verification's best form: the test is written before anyone knows the fix.
- **Red suites:** have a runner cluster the failures (same root cause? flaky? environmental?)
  before anyone fixes anything.

### 3. Plan

Approach, the decisions and tradeoffs, the files affected, the risks, and how it will be verified.
For multi-task work, or anything the user will want to keep, write it to `docs/plans/{slug}.md`,
because workers can read the plan instead of you retyping it into every brief.

### 4. Decompose into handoff packets

Split the plan into self-contained tasks with disjoint file ownership. Each worker starts blank, so
the packet carries everything:

- **Objective and fit**: the exact goal and how it fits the plan (point at `docs/plans/{slug}.md`
  if written).
- **Scope**: files and functions in scope by path, and what's explicitly out of scope.
- **Approach and why**: the approach you chose and the reasoning, so the worker doesn't "improve"
  it back into something you rejected.
- **Conventions**: exemplar files to follow.
- **Done means**: which tests must pass and what behavior to demonstrate.
- **Evidence to return**: files touched, commands run with results, line references, uncertainty.
- **Stop conditions**: the code doesn't match the brief, a command keeps failing after one
  reasonable fix, or out-of-scope files are needed. Stop and report instead of widening the task.

Keep tightly coupled work in one worker rather than splitting it across two that would have to
coordinate. Launch independent tasks together in one message.

### 5. Verify

- Read the actual diff, not the summary.
- A fresh `[test-runner]` runs the relevant tests (for a bug, the reproducing test must now pass
  and the rest of the suite must stay green against the baseline).
- A `[reviewer]` reviews any non-trivial diff. You check each finding against the code, then all
  MUST-FIX and SHOULD-FIX items go back to the same worker in one `SendMessage` (cap: 3 rounds;
  escalate a tier after two, per Model routing). For judgment-heavy or risky changes, read the
  diff yourself as well.
- Check the result against the plan: did it solve the problem, or only make the symptom go away?

### 6. Commit and report

Commit each verified task with explicit paths. Report the approach and why, what each worker did
and on which model, verification results with commands, anything left open, and the branch and
commits.

## Scenario defaults

- **Bug:** explore → reproducing test → fix → reviewer → runner.
- **Refactor:** explore callers → characterization tests of current behavior (if coverage is
  thin) → refactor in disjoint slices → full suite against baseline.
- **Red suite:** runner clusters failures → one worker per root cause → runner re-verifies.
- **Performance:** measure first (a worker writes a benchmark and records the baseline) → change →
  measure again. Numbers, not impressions.
- **Research question:** parallel explorers from different angles → you synthesize and decide what
  the evidence actually supports. No code changes, no commits.
- **Trivial task** (a rename, a version bump): say it didn't need a team, and still hand it to one
  worker rather than doing it yourself.

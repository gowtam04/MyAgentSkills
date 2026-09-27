# Git and Worktrees During a Build

Only the lead runs git in the main tree. Workers never commit, stash, reset, checkout or rebase.
Several agents running git at once corrupt the index and each other's work.

## Contents
- [Start of the build](#start-of-the-build)
- [Commits](#commits)
- [Worktrees](#worktrees)
- [When the user declined commits](#when-the-user-declined-commits)
- [Resuming](#resuming)

## Start of the build

```bash
git status --short                      # note pre-existing changes; leave them alone
git rev-parse --abbrev-ref HEAD         # on the default branch? then:
git switch -c build/{feature-slug}
git rev-parse HEAD                      # record as "build start" in the progress file
```

A repo with no commits can't host worktrees or per-phase commits. Ask before `git init` and an
initial commit.

## Commits

Always stage **explicit paths** — the phase's `tests`, `owns`, and any `shared` file it was
assigned. Never `git add -A` or `git add .` mid-build: other phases' in-progress files are sitting
in the same tree, and sweeping them into this phase's commit mislabels history and ships
half-written code.

| When | Message |
|---|---|
| Spec tests written and checked red | `test(p4b): spec tests for Invoices [US-3, AC-3.1, AC-3.2]` |
| Phase verified | `feat(p4b): Invoices [US-3, BR-4]` (use `chore`/`docs` for non-feature kinds) |
| Regression repaired | `fix(p4b): restore AC-2.1 after p5 change` |
| Integration checkpoint green | `test(integration): backend-e2e [US-3, US-5]` |
| Docs pass | `docs: README, API reference` |

Include the requirement IDs, because they're how `git log` answers "where was AC-3.2 built?".

**Test lock check.** After the test commit, `git diff <test-commit> -- <test paths>` must stay
empty until the phase is verified. Reviewers run it too. A non-empty diff means someone edited the
spec. The one legitimate case is a dispute you ruled on, and that gets its own commit that notes the
ruling.

## Worktrees

Use `isolation: "worktree"` on implementers when two or more run at once with non-trivial writes.

- **Worktrees start from the last commit.** A worktree implementer only sees what's committed. That
  is why a phase's tests are committed before its implementer spawns, and why a phase only starts
  once its dependencies are verified (and therefore committed).
- **When the implementer reports**, its result includes the worktree path and branch. Review the
  branch diff (`git diff build/{slug}...{branch}`), or have the reviewer read files in the worktree
  path. Fix rounds happen in the same worktree via `SendMessage` to the same implementer.
- **Merge once review passes:**
  ```bash
  git -C <worktree> status --short          # uncommitted changes? commit them on that branch:
  git -C <worktree> add <owned paths> && git -C <worktree> commit -m "feat(p4b): Invoices [US-3]"
  git merge --no-ff <branch> -m "feat(p4b): Invoices [US-3, BR-4]"
  git diff --stat HEAD^1 HEAD               # only the phase's owned paths should appear
  ```
  Anything outside the Own list in that diff needs investigating before you go on.
- **Conflicts.** With disjoint ownership they should be rare. A trivial one (two import lines in a
  shared file) is tiny glue: resolve it and log it. Otherwise run `git merge --abort` and send the
  conflict to the owning implementer.
- **After merging**, run the phase regression in the main tree, then clean up:
  `git worktree remove <path>` and `git branch -d <branch>`. Worktrees with no changes are removed
  automatically.

## When the user declined commits

- No worktrees: implementers run in the shared tree with disjoint ownership, which is safe because
  no two touch the same file.
- The test lock can't use git. Record `shasum -a 256 <test files>` in the progress file after the
  test-writer finishes, and have the reviewer compare checksums.
- Leave every change uncommitted and list all changed files per phase in the final report.

## Resuming

The progress file's Resume Snapshot holds the build branch, the build-start commit, verified phases
and their commits, unmerged worktree branches, and the active named agents. On resume:
`git log --oneline <build start>..HEAD` shows what's verified, `git worktree list` shows what's in
flight, and phases with no commit restart from their tests.

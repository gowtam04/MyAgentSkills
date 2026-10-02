# Git and Worktrees During a Game Build

Only the lead runs git in the main tree. Workers never commit, stash, reset, checkout or rebase.
Several agents running git at once corrupt the index and each other's work.

## Contents
- [Start of the build](#start-of-the-build)
- [Commits](#commits)
- [Binary assets](#binary-assets)
- [Worktrees](#worktrees)
- [When the user declined commits](#when-the-user-declined-commits)
- [Resuming](#resuming)

## Start of the build

```bash
git status --short                      # note pre-existing changes; leave them alone
git rev-parse --abbrev-ref HEAD         # on the default branch? then:
git switch -c build/{game-or-feature-slug}
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
| Spec tests written and checked red | `test(p4a): spec tests for Drop rules [gdd:03-systems#drop]` |
| Gameplay phase verified | `feat(p4a): Drop rules [gdd:03-systems#drop]` |
| Style lock verified | `art(p3): style lock` |
| Asset family verified | `art(p4c): block and crane sprites` |
| Content verified | `content(p5): levels 1–3 [gdd:03-systems#levels]` |
| Other kinds verified | `chore(p6): greybox wiring` (`docs` for docs phases) |
| Regression repaired | `fix(p4b): restore combo reset after p6 change` |
| Checkpoint green | `test(integration): loop-playable [gdd:03-systems#drop, gdd:03-systems#lives]` |
| Docs pass | `docs: README, how to play` |

Include the gdd tags, because they're how `git log` answers "where was the combo rule built?".

**Test lock check.** After the test commit, `git diff <test-commit> -- <test paths>` must stay
empty until the phase is verified. Reviewers run it too. A non-empty diff means someone edited the
spec. The one legitimate case is a dispute you ruled on, and that gets its own commit that notes the
ruling.

## Binary assets

- Commit generator scripts **and** their outputs together, so the assets are reproducible and the
  game runs from a clean checkout.
- Leave contact sheets, QA previews and playtest screenshots under `tmp/` uncommitted unless the
  project already tracks them; they're evidence, not product.
- If the repo uses Git LFS (`.gitattributes` with `filter=lfs`), stage assets the same way; LFS
  handles them. Don't add LFS mid-build without asking.

## Worktrees

Use `isolation: "worktree"` on implementers when two or more run at once with non-trivial writes.
Asset-artists with disjoint outputs work in the main tree.

- **Worktrees start from the last commit.** A worktree implementer only sees what's committed. That
  is why a phase's tests are committed before its implementer spawns, and why a phase only starts
  once its dependencies are verified (and therefore committed). The same goes for the style lock
  and any assets the phase wires in.
- **When the implementer reports**, its result includes the worktree path and branch. Review the
  branch diff (`git diff build/{slug}...{branch}`), or have the reviewer read files in the worktree
  path. Fix rounds happen in the same worktree via `SendMessage` to the same implementer.
- **Merge once review passes:**
  ```bash
  git -C <worktree> status --short          # uncommitted changes? commit them on that branch:
  git -C <worktree> add <owned paths> && git -C <worktree> commit -m "feat(p4a): Drop rules"
  git merge --no-ff <branch> -m "feat(p4a): Drop rules [gdd:03-systems#drop]"
  git diff --stat HEAD^1 HEAD               # only the phase's owned paths should appear
  ```
  Anything outside the Own list in that diff needs investigating before you go on.
- **Conflicts.** With disjoint ownership they should be rare. A trivial one (two import lines in a
  shared scene file) is tiny glue: resolve it and log it. Otherwise run `git merge --abort` and send
  the conflict to the owning implementer.
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

The progress file's Resume Snapshot holds the build branch, the build-start commit, the style-lock
commit, verified phases and their commits, unmerged worktree branches, and the active named agents.
On resume: `git log --oneline <build start>..HEAD` shows what's verified, `git worktree list` shows
what's in flight, and phases with no commit restart from their tests (or, for asset phases, from
the artist's last report).

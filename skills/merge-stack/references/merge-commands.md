# Merge commands

Checked against `gh` 2.6x and `gh-stack` v0.3.0. When a flag below is rejected, check
`gh pr merge --help` or `gh stack merge --help` before working around it.

## Plain mode, stack

Record the next PR's own diff before merging the one below it:

```bash
git fetch origin
OLD_BASE=$(git rev-parse origin/<branch-i>)   # survives the branch being deleted after the merge
BEFORE=$(git diff $OLD_BASE origin/<branch-(i+1)> | git patch-id --stable)
```

Merge PR *i*, pinned to the commit CI ran on:

```bash
gh pr merge <pr-i> --squash --match-head-commit <sha-i>   # or --rebase / --merge
```

Squash or rebase merge: PR *i+1* still contains the commits of PR *i*, which the trunk now holds
under new SHAs. Replay only its own commits onto the trunk:

```bash
git fetch origin
git checkout <branch-(i+1)> && git reset --hard origin/<branch-(i+1)>
git rebase --onto origin/<trunk> $OLD_BASE <branch-(i+1)>
AFTER=$(git diff origin/<trunk> <branch-(i+1)> | git patch-id --stable)
[ "$BEFORE" = "$AFTER" ] || git range-diff $OLD_BASE..origin/<branch-(i+1)> origin/<trunk>..<branch-(i+1)>
git push --force-with-lease origin <branch-(i+1)>
gh pr edit <pr-(i+1)> --base <trunk>
```

`git reset --hard` here only syncs the local copy of a stack branch with its remote; never run it
on the trunk or a branch with local work.

Merge commit: the trunk contains the commits of PR *i* with the same SHAs, so only retarget:
`gh pr edit <pr-(i+1)> --base <trunk>`. The PR then shows only its own commits.

Retarget before deleting `<branch-i>`. GitHub retargets dependent PRs itself when it deletes a
merged branch (the repo's "automatically delete head branches"), but a branch deleted with
`git push --delete` while a PR is still based on it closes that PR.

## Stack mode (`gh stack`)

| Step | Command |
|---|---|
| Merge up to PR *i* | `gh stack merge <pr-i> --squash` (or `--rebase`/`--merge`); merges every PR below it too, so call it for the bottom unmerged PR only |
| Move the rest onto the trunk | `gh stack sync`: fetch, cascade rebase, push, retarget PRs |
| Conflict during sync | branches are restored; `gh stack rebase`, resolve, then `--continue` or `--abort` |
| Check | `gh stack view --short` |

Use `--yes` only when the user asked for no prompt.

## Queue (independent PRs on the trunk)

| State | Command |
|---|---|
| Next PR is `BEHIND` and the repo requires up-to-date branches | `gh pr update-branch <n>` (merge commit) or `gh pr update-branch <n> --rebase` |
| Waiting for CI | `gh pr checks <n> --watch --fail-fast` |
| Merge | `gh pr merge <n> --<method> --match-head-commit <sha>` |

A repo with a GitHub merge queue (`mergeStateStatus` mentions it, or `gh pr merge` says the PR was
added to the queue): the queue already serialises merges. Add the PRs in order and watch, don't
retarget or rebase yourself.

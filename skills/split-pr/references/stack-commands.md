# Stack commands

Checked against `gh-stack` v0.3.0. When the installed version differs (`gh stack --version`), check
`gh stack <command> --help` before relying on a flag.

## Stack mode (`gh stack`)

With more than one remote (`git remote`), pass `--remote <name>` to `push`, `submit`, `sync`
and `link`. Ask which remote if it isn't obvious.

| Step | Command |
|---|---|
| Layer 1 | `git checkout <trunk> && gh stack init --base <trunk> <branch>` |
| Layer i > 1 | `git checkout <parent> && gh stack add <branch>` (adds on top of the stack) |
| Show the stack | `gh stack view --short`, `gh stack view --json` |
| Push and open PRs | `gh stack submit --auto` (new PRs as drafts, auto titles); `--open` marks them ready |
| Set a body | `gh pr edit <n> --body-file <file>`, `gh pr edit <n> --title "<title>"` |
| After a fix in a lower layer | `gh stack rebase` (cascade), then `gh stack push` (`--force-with-lease` per branch, atomic) |
| Trunk moved | `gh stack sync`: fetch, cascade rebase, push, relink PRs. A conflict restores all branches; resolve with `gh stack rebase`, then `--continue` or `--abort` |
| Merge | `gh stack merge [<pr>]`: atomic merge of everything up to that PR; `--squash`/`--rebase`/`--merge`. Use `--yes` only when the user asked for no prompt |
| Existing branches, no local tracking | `gh stack link <b1> <b2> …` (bottom to top) |

`gh stack init` and `add` without `-m`/`-A` create the branch only; the layer's commit is made with
plain `git commit`. Never `gh stack add -A`: it stages everything, including files from other layers.

## Plain mode (no `gh stack`)

Build:

```bash
git checkout -b <branch-1> <trunk>        # layer 1
git checkout -b <branch-i> <branch-(i-1)> # layer i
```

Publish, bottom up, after the integrity check:

```bash
git push -u origin <branch-i>
gh pr create --draft --base <branch-(i-1)> --head <branch-i> --title "<title>" --body-file <file>
```

The base of PR 1 is the trunk. Once every PR exists, rewrite each body so its stack table lists all
PR numbers (`gh pr edit <n> --body-file <file>`).

A fix in layer k after publishing: commit it on `<branch-k>`, then for each branch above it
`git checkout <branch-i> && git rebase <branch-(i-1)>` and `git push --force-with-lease origin <branch-i>`.
Only these new stack branches ever get `--force-with-lease`; never the trunk or the source branch.

Merge, one PR at a time, bottom up, each after its CI is green:

```bash
gh pr merge <pr-1> --squash
# the next PR still points at the merged branch: retarget it and replay only its own commits
git fetch origin
git rebase --onto origin/<trunk> <branch-1> <branch-2>
git push --force-with-lease origin <branch-2>
gh pr edit <pr-2> --base <trunk>
# wait for CI on <pr-2>, then repeat for the next one
```

With merge commits instead of squash, `git rebase --onto` is not needed: retarget with
`gh pr edit --base <trunk>` and the PR shows only its own commits. If the repo deletes merged
branches automatically, GitHub retargets the next PR itself; rebase it anyway when squashing.

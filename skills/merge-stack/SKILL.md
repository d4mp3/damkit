---
name: "merge-stack"
description: "Merge a stack of PRs, or several PRs that must land in order, into the trunk one after another: each merged only on green CI and approval, the next one retargeted, rebased and re-checked before it merges."
disable-model-invocation: true
argument-hint: "[PR numbers bottom to top | any branch of the stack]"
---

# Merge stack

Land a **stack** (a chain of PRs, each based on the one below it, e.g. from `/damkit:split-pr`)
or a **queue** (independent PRs on the trunk that must land in a given order) one PR at a time.
After every merge the next PR is moved onto the new trunk and its CI runs again, so each PR is
merged on exactly the code it was tested on.

Merging is irreversible and outward-facing. This skill never bypasses the repo's rules: no
`--admin`, no merging on red or pending checks, no merging without the required approvals.

## Process

### 1. Find the PRs and their order

- The working tree must be clean. Find the trunk: `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`.
- Arguments are PR numbers: take them in the given order. A branch name, or nothing (the current
  branch): `gh stack view --json` if `gh stack` works, otherwise walk the bases down with
  `gh pr view <branch> --json number,baseRefName` until the base is the trunk, and up with
  `gh pr list --base <branch> --json number,headRefName`.
- **Stack**: PR 1 is based on the trunk, every other PR on the branch of the one below it.
  **Queue**: every PR is based on the trunk. A mix, or a PR whose base is neither the trunk nor the
  previous PR: stop and show the user what you found.

For each PR record:
`gh pr view <n> --json number,title,url,state,isDraft,baseRefName,headRefName,headRefOid,reviewDecision,mergeable,mergeStateStatus,body`.
`headRefOid` is the commit the user approves. A later push by anyone but this session stops the loop.

Done when the ordered list, its kind (stack or queue) and each PR's head commit are known.

### 2. Pick the merge method

Read `gh repo view --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed,deleteBranchOnMerge`.
One allowed method: use it. Several: the one `CLAUDE.md` names, otherwise ask. The method decides
the step between merges ([references/merge-commands.md](references/merge-commands.md)): after a
squash or rebase merge the next stack PR is rebased with `--onto`; after a merge commit it is only retargeted.

Stack mode (`gh stack` installed and the stack known to it) uses `gh stack merge <pr>` and
`gh stack sync`; plain mode uses `gh pr merge` and git. Say which.

### 3. Get the merge plan approved

Show the plan and stop. Run nothing that writes (merge, push, retarget, rebase) before the user approves it.

| # | PR | Base | Head | CI | Review | Door |
|---|---|---|---|---|---|---|
| 1/N | #12 Add docs | `main` | `a1b2c3d` | green | approved | Two-way |
| N/N | #15 Enable flag | `feat/03-api` | `d4e5f6a` | pending | approved | **One-way** |

- **CI**: `gh pr checks <n>`. **Review**: `reviewDecision`. **Door**: from the `[Stack i/N]` line
  of a split-pr body; `—` when the body has none.
- Under the table: the method, the mode, and blockers already visible: drafts, changes requested,
  conflicts (`mergeable: CONFLICTING`), red checks. A draft is marked ready (`gh pr ready <n>`)
  only if the user says so.
- The **one-way door** PR is confirmed again right before it merges, with what users will see and
  how to roll it back (from its body).

Done when the user approves the plan. The harness may still ask before each `gh pr merge`; that is expected.

### 4. Merge one PR at a time, bottom up

For PR *i*:

1. **Fresh state.** `gh pr view <n> --json state,headRefOid,baseRefName,reviewDecision,mergeStateStatus`.
   - The head is not the recorded one (and this session didn't push it): stop, someone pushed.
   - The base is not the trunk: step 4 of the previous round didn't finish. Do it now.
   - `reviewDecision` is `CHANGES_REQUESTED`, or `REVIEW_REQUIRED` where the repo requires approval: stop.
2. **Wait for CI.** Run `gh pr checks <n> --watch --fail-fast` as a background command and wait to
   be notified; don't poll. Red: stop and report the failing check and its URL (`gh pr checks <n>`).
   Don't fix it here; the fix belongs on that PR's branch.
3. **Merge.** Plain mode: `gh pr merge <n> --<method> --match-head-commit <sha>`. Stack mode:
   `gh stack merge <n> --<method>`. Never `--admin`, never `--auto` for this loop, never
   `--delete-branch` while a PR above still has this branch as its base. Confirm the result:
   `gh pr view <n> --json state,mergeCommit` shows `MERGED`.
4. **Move the next PR onto the trunk** (stack only; a queue skips to 5).
   Plain mode, as in [references/merge-commands.md](references/merge-commands.md): fetch, rebase
   the next branch `--onto origin/<trunk>`, `git push --force-with-lease` that branch only,
   `gh pr edit <next> --base <trunk>`. Stack mode: `gh stack sync`.
   - A rebase conflict: `git rebase --abort` (stack mode: `gh stack rebase --abort`), stop and report the files.
   - **Integrity check**: the next PR's own diff must not change. Compare
     `git diff <old base SHA, recorded before the merge> <branch> | git patch-id --stable` with
     `git diff origin/<trunk> <branch> | git patch-id --stable` after. Different: stop and show
     `git range-diff`. Record the new `headRefOid`.
5. **Queue only.** If the next PR is `BEHIND` and the repo requires up-to-date branches, ask once
   whether to update the remaining PRs with `gh pr update-branch <next>` (adds a merge commit) or
   `--rebase`. A conflict: stop.
6. Report one line: `#<n> merged as <sha>, #<next> on <trunk>, CI running`. Continue with *i*+1.

**Stop** means: leave everything as it is, report what is merged, what is not, and why, and
ask how to continue. Never skip a PR and merge the ones above it.

### 5. Hand off

Report the table again with each merge commit (`gh pr view <n> --json mergeCommit -q .mergeCommit.oid`)
and the PRs still open. Then suggest, without running them:
- deleting the merged branches the repo didn't delete itself (`git push origin --delete <branch>`, top down);
- after a split-pr stack: closing the original PR with a link to the stack, deleting the source
  branch and `split-pr/backup-<branch>`;
- `git checkout <trunk> && git pull` locally.

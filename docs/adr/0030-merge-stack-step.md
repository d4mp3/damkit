# ADR-0030: `merge-stack` merges a stack of PRs one at a time

- Status: Accepted
- Date: 2026-11-25
- Refines: ADR-0029 (the stack it produces now has a merge step)

## Context

`split-pr` ends with a stack of reviewed PRs, and the hand-off only named `gh stack merge` or a
manual loop of merge, retarget and rebase. Done by hand, the loop goes wrong in quiet ways: a
squash merge leaves the next PR carrying the commits of the one below it, deleting a merged branch
closes the PR based on it, and a PR merged right after a rebase lands on code its CI never ran on.
The same loop applies to independent PRs that must land in order. Matt's flow ends at the commit
and has no merge step.

## Decision

- `merge-stack` is a process step after `/code-review` and `/damkit:review-changes` of every PR in
  a stack. It merges the PRs bottom up, one at a time.
- The user approves a plan (order, method, CI, review, door of each PR) before anything is written.
  The one-way door PR is confirmed again right before it merges.
- Each PR is merged only on green CI and the approval the repo requires, with
  `--match-head-commit` so it lands on the commit that was tested. No `--admin`, no `--auto`.
- After a squash or rebase merge the next PR is rebased `--onto` the trunk from the recorded old
  base SHA, its own diff is compared by `git patch-id` before and after, and it is retargeted
  before the merged branch can be deleted.
- Any red check, requested change, conflict, changed diff or foreign push stops the loop. PRs above
  a stopped one are never merged. The skill doesn't fix code and deletes no branches.
- `disable-model-invocation: true`: merging starts only when the user calls the skill.
- `gh stack merge` and `gh stack sync` when the stack is known to `gh stack`; `gh pr merge` and git otherwise.

## Alternatives considered

- **`gh stack merge` of the whole stack at once**: atomic, but needs `gh stack` and merges PRs whose
  rebased CI hasn't run.
- **GitHub auto-merge (`--auto`) on every PR**: the next PR would merge before it is retargeted and rebased.
- **Keep the loop in split-pr's reference**: it is a separate session, often days later, and the
  loop also serves PRs that were never split.

## Consequences

- split-pr's hand-off and its stack commands point to `merge-stack` for merging.
- Waiting for CI is a background `gh pr checks --watch` per PR, so a stack of N PRs takes N CI runs.
- Repos with a GitHub merge queue need only the PRs added in order.

# ADR-0029: `split-pr` turns a large branch into a stack of small PRs

- Status: Accepted
- Date: 2026-11-25
- Refines: ADR-0015 (a new process step shows a gap in Matt's flow and the step it hands to)

## Context

Matt's flow keeps changes small through `/to-tickets`, but a branch still grows large: a long
`/implement`, several merged `implementation-worker` branches, work started before the tickets.
`/code-review` on 2,000 lines finds less than on four PRs of 500, and one large merge is one large
revert. None of Matt's skills splits an existing branch, so this step duplicates none of his.

GitHub's `gh-stack` extension manages stacked PRs: it creates branches on top of each other, opens
the PRs with the right bases, rebases the stack and merges it atomically. It is not installed everywhere.

## Decision

- `split-pr` is a process step. It takes a large branch or PR and produces a stack of PRs that
  `/code-review` and `/damkit:review-changes` then check one by one, each against its parent.
- Layers go from safe to risky (docs, refactor, schema, logic, UI, flag flip), 200–600 changed
  lines each. Every PR but the top one is a two-way door. A behavior change goes behind a feature
  flag, added to the source branch before splitting, so the top PR only flips it.
- The plan is approved by the user before any git command writes anything.
- The layers are built by sub-agents with clean contexts, one after another, from the pinned
  source commit. The planning session neither edits nor commits.
- Each sub-agent checks its layer's door, not only its tests: a two-way layer has only additive
  migrations, unchanged test assertions and public contracts, and no new behavior reachable with
  the flag off. A layer that fails stops, and the plan changes.
- `git diff <source commit> <top of stack>` must be empty before anything is pushed. The source
  branch is never deleted by the skill.
- `gh stack` when it is installed; otherwise `git checkout -b` chains, `gh pr create --base` and
  a stack table in each PR body.

## Alternatives considered

- **Leave it to `gh-stack`'s own skill**: it knows the commands but doesn't plan layers, doors or
  flags, and assumes the work is still being written, not already on one branch.
- **Split in the main session**: the full diff and hunk-by-hunk edits fill the context, and the
  mistakes it causes are hard to spot.
- **Parallel sub-agents per layer**: each layer starts from the one below, so they can't run in parallel.
- **Require `gh-stack`**: the plain mode is a few commands and keeps the step usable everywhere.

## Consequences

- The skill's description names its artifact ("a stack of small PRs"), as QRSPI steps do (ADR-0015).
- Pushing and opening PRs still ask first, as the project settings require.
- The plain-mode merge is a manual loop of retarget and rebase; `gh stack merge` is atomic.

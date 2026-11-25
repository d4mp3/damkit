---
name: "split-pr"
description: "Split a large branch or pull request into a stack of small PRs (stacked diffs with gh-stack): every PR but the last a reversible two-way door, the last one flipping a feature flag."
---

# Split PR

Turn one large branch into a **stack**: a chain of small PRs, each based on the one below it,
ending at the trunk (`main`/`master`). Every PR except the top one is a **two-way door**: it can be
merged and reverted at any time without changing what users see. The top PR is the only
**one-way door**, ideally a one-line flip of a feature flag.

You plan in this session; sub-agents with clean contexts build the layers. The diff of a large
branch fills a context fast, and splitting files hunk by hunk in a full context is where the
mistakes happen.

## Process

### 1. Pin the starting point

- The working tree must be clean. Uncommitted changes: ask the user to commit or stash them first.
- Find the trunk: `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`.
- Record the source: branch name, `ORIG=$(git rev-parse HEAD)` and
  `BASE=$(git merge-base <trunk> HEAD)`. Create a backup ref: `git branch split-pr/backup-<branch> $ORIG`.
  Every later comparison uses `$ORIG`, never the branch name, which may move.
- An open PR for the branch (`gh pr view --json number,url`): note its number. It gets closed
  with a link to the stack only at the end.

Done when `$ORIG`, `$BASE`, the trunk and the backup ref are known.

### 2. Detect the tooling

Run `gh stack --help`. If it works, use **stack mode** (`gh stack init/add/submit/sync`). If not,
use **plain mode**: `git checkout -b` chains and `gh pr create --base <previous branch>`, with
a stack table written into every PR body. See [references/stack-commands.md](references/stack-commands.md).
Say which mode you use. Suggest `gh extension install github/gh-stack`, but don't install it yourself.

### 3. Read the diff, then plan the layers

Read `git diff --stat $BASE $ORIG` and `git diff --numstat $BASE $ORIG`. Open the diff only per
file, as far as you need to assign its hunks to a layer. Count **LOC** as added plus deleted lines,
excluding lockfiles, generated code, snapshots and generated migrations (list them separately).

Assign every hunk to one layer. Use this order as a default, not a template; skip what the branch
doesn't have:

1. Docs, ADRs, `CONTEXT.md`.
2. Refactors of shared code that change no behavior.
3. Schema and data models: additive migrations (new nullable columns, new tables, indexes).
4. Business logic and API, unreachable while the flag is off.
5. UI behind the flag.
6. Flag flip, plus removal of the legacy path if the branch removes it.

Rules for the plan:
- **Target 200–600 LOC per PR.** Split a layer that exceeds it along a seam (one module or one
  endpoint per PR). Merge layers under ~50 LOC into a neighbor.
- **Each PR builds and passes tests on its own.** A layer that needs a symbol from a higher one is
  in the wrong order. Move the symbol down.
- **Only the top PR is a one-way door.** Destructive migrations (drop, rename, `NOT NULL` on
  existing data), changed API contracts and changed defaults are one-way doors. If the
  branch has more than one, say so: the stack then needs two flips or an expand/contract migration.
- **A behavior change hides behind a flag.** If the branch changes existing behavior and has no
  flag, propose one: use the project's existing flag mechanism, or the simplest config value
  when there is none. The flag is added to the **source branch first**, as its own commit with
  the default on. The layers set it off, and the top PR flips it on, so the stack still ends
  byte-identical to the source. Re-record `$ORIG` after that commit.
- A file with hunks from two layers is split by hunk, never placed whole in one layer.

### 4. Get the plan approved

Show the plan and stop. Run no git or `gh` command that writes anything until the user approves it.

| # | Branch | Base | Scope (files, hunks) | Door | LOC |
|---|---|---|---|---|---|
| 1/N | `<branch>/01-docs` | `<trunk>` | `docs/adr/…`, `CONTEXT.md` | Two-way | 80 |
| N/N | `<branch>/0N-enable-flag` | `<branch>/0(N-1)-…` | `settings.py`: flag default | One-way | 2 |

Under the table: files split by hunk and which hunk goes where, excluded generated files, and the
flag commit if one is needed. Branch names follow the repo's convention if it has one.

Done when the user approves the plan, possibly after changes.

### 5. Build the layers with sub-agents, one at a time

Dispatch one **general-purpose** sub-agent per layer, **sequentially** and in this checkout, because
each layer starts from the previous one. Never run them in parallel. Don't edit files or commit
layers in this session yourself. Give each sub-agent only:

- `$ORIG`, the parent branch (the trunk for layer 1), the new branch name, the mode and the
  layer's door (two-way or one-way) with the flag's name if there is one;
- the exact paths for this layer, and for split files the hunks to take, quoted by their `@@` header
  and first changed line;
- the commit message (the repo's commit convention) and the PR body ([references/pr-body.md](references/pr-body.md)), filled in;
- the project's build and test commands from `CLAUDE.md`;
- the instructions below, verbatim.

<sub-agent-instructions>
1. Create the branch from the parent. Stack mode: for layer 1 run `git checkout <trunk>` and
   `gh stack init --base <trunk> <branch>`. For later layers run `git checkout <parent>` and
   `gh stack add <branch>`. Plain mode: `git checkout -b <branch> <parent>`.
2. Take whole files from the source with `git checkout $ORIG -- <paths>` and deletions with
   `git rm <paths>`. For a split file, write the chosen hunks to a patch
   (`git diff <parent> $ORIG -- <path>`, keep only those hunks) and apply it with
   `git apply --index --recount`. Never pull a whole split file into this layer.
3. Code needed only to keep this layer green (a stub, a default of the flag set off) is allowed if
   a later layer from the plan removes it. Report it.
4. Run the build and tests. Fix only what this layer's split broke, never the source's code. If the
   layer can't be green without a hunk from a higher layer, stop and report it. Don't pull the hunk in.
5. Check the door in `git diff <parent>`. A **two-way** layer must pass all of these; if one fails,
   stop and report it with the hunk, don't fix it by changing behavior:
   - Migrations only add: new tables, new nullable columns or columns with a default, new indexes.
     A drop, rename, type change, `NOT NULL` on existing rows or a data rewrite is a one-way door.
   - Existing tests pass with their assertions unchanged. An edited or deleted assertion means
     behavior changed.
   - Public contracts stay: no removed or renamed endpoint, field, CLI option, event or config key,
     and no changed default.
   - New behavior is unreachable with the flag off: every new entry point (route, job, UI element,
     handler) is behind the flag or not wired up yet.
   A **one-way** layer contains only what the plan lists for it. Name the change users will see
   and how to roll it back.
6. Commit with the given message. Don't push, don't open PRs.
7. Report: branch, commit SHA, LOC (`git diff --numstat <parent>`), test result, the door check
   (each point passed or the hunk that failed it), temporary code added.
</sub-agent-instructions>

After each report, check `git diff --stat <parent> <branch>` against the plan and read the door
check before you dispatch the next layer. A layer that stopped: change the plan (move the hunk
up, put it behind the flag, merge layers) and tell the user if the change crosses a door.

### 6. Verify integrity, then publish

1. `git diff $ORIG <top branch>` must be empty. If it isn't, the diff shows what is missing or
   extra. Fix it in the layer it belongs to and rebuild from there. **Nothing gets pushed until this check
   passes.**
2. Ask before pushing. Stack mode: `gh stack submit --auto`, then set each PR's body
   with `gh pr edit <n> --body-file <file>`. Plain mode: push each branch and create its PR as
   [references/stack-commands.md](references/stack-commands.md) shows. New branches only: never
   force-push a branch someone else uses.
3. Stack mode: `gh stack view` shows every PR on its parent. Plain mode: `gh pr view <n> --json baseRefName`
   for each PR.

### 7. Hand off

Report the stack table with PR URLs, and give the user:
- **Review**: each PR on its own fixed point, `/code-review <parent branch>`, and
  `/damkit:review-changes <parent branch>` for the layers that touch risk areas.
- **Merge** after green CI: stack mode `gh stack merge` (atomic, bottom up to the chosen PR). Plain mode:
  the loop in [references/stack-commands.md](references/stack-commands.md).
- **Cleanup**, only after the integrity check passed: close the original PR with a link to the
  stack, and delete the source branch and `split-pr/backup-<branch>` once the stack is merged.
  Suggest these commands; don't run them yourself.

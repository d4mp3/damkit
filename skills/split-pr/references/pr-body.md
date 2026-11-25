# PR body for a stack layer

Write the body in the language of the repo's docs (`## Language` in `CLAUDE.md`). Fill in every
placeholder. Verification steps are commands and clicks a reviewer can repeat, not "tests pass".

```markdown
**[Stack <i>/<N>]** · **<Two-way door | One-way door>** · base: `<parent branch>`

## What
<1–3 sentences: what this layer adds, in the glossary's terms.>

## Why it is safe to merge alone
<Two-way: why nothing changes for users (flag off, code unreachable, additive migration) and how
to revert it (`git revert`, plus any data step).
One-way: what changes for users when this merges and how to roll it back (flag off, not revert).>

## Verify
1. <command or step>
2. <expected result>

## Stack
<plain mode only: the table below, the same in every PR, with this PR's row in bold.
Stack mode: delete this section, GitHub shows the stack.>

| # | PR | Door |
|---|---|---|
| 1/N | #<n> <title> | Two-way |
| **2/N** | **#<n> <title>** | **Two-way** |
```

Temporary code that a later layer removes (stubs, the flag default set to off): name it under
**What** with the layer that removes it.

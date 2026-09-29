---
name: review-standards
description: Use when reviewing code, infrastructure, database or security changes and producing findings - defines severity calibration, evidence requirements and the finding format shared by all reviewer agents.
---

# Review standards

A review is valuable when every finding is real, matters, and can be acted on.
Ten findings where three are noise make all ten useless.

## Scope

1. Determine what changed: `git diff --stat <base>...HEAD` plus uncommitted changes
   (`git diff`, `git diff --cached`). Base = the branch named in the brief, else `main`/`master`.
2. Read each changed hunk **and** enough surrounding code to know how it is called.
3. Review the change, not the whole repository. Pre-existing problems go in a separate
   "Pre-existing" section and only if they are critical or high.

## Evidence before reporting

For each candidate finding, before writing it down:

- Trace the failure path in the actual code (caller → changed code → effect).
- Look for an existing guard (validation upstream, a DB constraint, middleware, a test
  that covers the case). If one exists, drop the finding.
- Where a tool can confirm it, run the tool (linter, `EXPLAIN`, `kubeconform`,
  `helm template`, a targeted test) and quote the relevant output line.

Label every finding:

- **confirmed**: you traced it or a tool proved it
- **likely**: plausible, but it depends on something you couldn't observe (data volume,
  runtime config). Say what would confirm it.

## Severity

| Severity | Meaning |
|---|---|
| critical | Exploitable security hole, data loss/corruption, or outage on the normal path. Must fix before merge. |
| high | Wrong behavior on a realistic path, broken deploy/rollback, or a migration that locks prod tables. Fix before merge. |
| medium | Edge-case bug, missing test for risky logic, operability gap that will hurt during an incident. |
| low | Maintainability issue with concrete future cost. Report at most 3. |

Style, naming and formatting are not findings unless they hide a bug.

## Finding format

```
### [severity] [confirmed|likely] <one-line title>
Location: path/to/file.py:123
Problem: <what the code does, and under which input/state it fails>
Impact: <user-visible or operational consequence>
Fix: <minimal concrete change; a snippet if under 10 lines>
Verify: <command or test that proves the fix>
```

## Report shape

1. Verdict in one line: `ship` / `ship after fixes` / `needs rework`.
2. Findings ordered by severity.
3. "Checked, no issues" list: the risk areas you examined and found clean (one line each),
   so the reader knows what was covered.

If nothing meaningful is found, say so plainly. An empty review is a valid result.

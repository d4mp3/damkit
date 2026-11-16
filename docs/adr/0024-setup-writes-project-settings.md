# ADR-0024: setup-geostack also writes the project's shared `.claude/settings.json`

- Status: Accepted (extends [ADR-0019](0019-setup-devkit-writes-project-claude-md.md))
- Date: 2026-11-16

## Context

`setup-geostack` wrote only `CLAUDE.md`, which the model reads and usually follows. Current Claude Code
practice splits instructions by who enforces them: the model decides from `CLAUDE.md` and skills, the
harness enforces deny and ask rules and hooks. Auto mode blocks most dangerous commands but not all, so
whatever can't be undone needs a rule the harness checks before the classifier sees the call. Those
rules have to travel with the repository, to teammates and cloud sessions, and that's the shared
`.claude/settings.json`. I also didn't want any of this in my user settings: each project gets what it
needs when it is set up.

Two more gaps came up. `setup-geostack` didn't ask about the cluster when the repo didn't show it.
On a corporate cluster run by an ops team, I often can't read those facts myself, and reviewers then
guessed.

## Decision

- `setup-geostack` writes or completes `.claude/settings.json` from
  `assets/settings.project.json`:
  - deny: secret reads, force push, `reset --hard`, `git clean`;
  - ask: `git push` and PR create/merge;
  - the `geostack@dampe` plugin with its marketplace.
- It adds hooks from the commands it found: a per-file formatter on `PostToolUse` and the fastest
  check on `Stop`, with exit 2 on failure. The `Stop` hook is added only if that check passes today.
- It doesn't write keys a project file ignores (`defaultMode: "auto"`, `autoMode`) or personal ones
  (`statusLine`, `model`); those stay in user or `.claude/settings.local.json` settings.
- Step 3 asks about the cluster when `## Deployment` applies and the repo doesn't show it. "Managed by
  another team, details unknown" is a valid answer, and `platform-reviewer` then turns
  cluster-dependent risks into questions for that team.
- This repo gets its own `.claude/settings.json`: the same deny rules, and a `Stop` hook that runs the
  guard tests when `hooks/` has uncommitted changes.

## Alternatives considered

- **Leave settings to the user's global file**: rules wouldn't reach teammates or cloud sessions,
  and one global file can't fit both a homelab and a corporate repo.
- **A full settings template per stack**: hooks depend on the project's commands, which step 2 already
  reads. One small template plus rules in prose is enough (ADR-0010).
- **Sandbox settings in the project file**: sandbox paths and credentials are per machine, and a
  committed `sandbox.enabled` fails differently on machines without bubblewrap.

## Consequences

- `setup-geostack` is no longer read-only towards harness configuration; it shows the file and doesn't
  commit it.
- Deny and ask rules apply as soon as the file exists. The marketplace and plugin apply after each
  teammate trusts the folder.

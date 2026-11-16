# ADR-0012: Read-only guard in Codex as a plugin hook filtered by `agent_type`

- Status: Superseded by [ADR-0017](0017-drop-codex-variant.md); earlier, it superseded the part of ADR-0011 about the guard
- Date: 2026-09-29

## Context

ADR-0011 wired the read-only guard into each role's TOML file (`[[hooks.PreToolUse]]`), because the Codex
documentation did not describe the agent type in the hook input. A test on Codex 0.156.1 (`codex exec` with a probe role
in a temporary project) showed that:
- a project-level `PreToolUse` hook receives `"agent_type":"probe"`
  and `"agent_id"` for a spawned agent;
- a hook declared in the same role's TOML did **not** fire before the same command;
- a `hooks` table in TOML does not break loading the role, but it is dead.

The guard from ADR-0011 did not work in practice. Only the sandbox protected.

## Decision

- The guard is a **plugin hook** (`codex/hooks/hooks.json`, `${PLUGIN_ROOT}`), as in the Claude version
  (ADR-0003). It restricts only the roles in `READONLY_AGENTS` (by `agent_type`). The main session
  and `implementation_worker` get no decision.
- The hook command ends with `|| true`. The hook fires in every session, and a missing guard file would give
  exit 2, which Codex treats as blocking every command.
- The `[[hooks…]]` blocks are removed from the role TOMLs. `install_agents.py` copies only the roles and does not require
  a git repo root.
- `verify_guard.sh` checks the whole chain on the installed plugin: `code_reviewer` tries
  `git commit`, and the guard must block it. It replaces `probe_agent_hooks.sh`.

## Alternatives considered

- **A hook in the project's `.codex/hooks.json` (copied by the installer)**: the only option confirmed
  directly, but it requires merging with the user's existing hooks and a copy of the guard in every project.
  According to the documentation, a plugin hook has the same input schema. `verify_guard.sh` confirms this,
  and if it shows otherwise, we return to this option.
- **Keeping the hooks in the role TOMLs**: the test showed that Codex does not run them.

## Consequences

- The plugin requires trusting the hook once. Without that the guard is inactive, and the README says so.
- The list of read-only roles is in two places (`guard_readonly.py` and `check.py`); `check.py`
  makes sure they match.
- The guard depends on Codex continuing to pass `agent_type`. It is worth running `verify_guard.sh`
  after Codex updates.

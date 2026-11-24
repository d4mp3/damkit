# ADR-0003: Read-only mode for agents is enforced by a plugin hook, not by the prompt

- Status: Accepted
- Date: 2026-09-29

## Context

Reviewers, `test-runner` and `cluster-investigator` have access to Bash, and `cluster-investigator`
also to a real k3s cluster. The sentence "don't run `kubectl apply`" in a prompt is only a request.
Plugin agents ignore `permissionMode` and `hooks` in the frontmatter, so it cannot be blocked
there.

## Decision

- `hooks/hooks.json` registers a `PreToolUse` hook on Bash that runs `hooks/guard_readonly.py`.
- The script acts only for agents in the `READONLY_AGENTS` list (it recognizes them by `agent_type`,
  e.g. `damkit:cluster-investigator`). The main session and `implementation-worker` are not restricted.
- Cluster tools use a list of allowed verbs (allowlist). git, docker
  and psql use a denylist. Commands that cannot be parsed are rejected.
- `Edit`/`Write` are additionally disabled via `disallowedTools`.

## Alternatives considered

- **Prompt instruction only**: it is not enforced.
- **`deny` rules in `settings.json`**: they apply to the whole session, so they would block me too.
  A plugin does not ship a `settings.json` with permissions anyway.

## Consequences

- The hook catches mistakes, not deliberate bypasses (e.g. `python -c` writing a file). The real boundary
  is a kubeconfig with a ServiceAccount bound to the `view` role (instructions in README).
- A new read-only agent must be added to `READONLY_AGENTS` and get a test in `test_guard_readonly.py`.

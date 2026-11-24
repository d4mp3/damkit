# ADR-0011: Codex CLI variant as an independent copy in `codex/`

- Status: Superseded by [ADR-0017](0017-drop-codex-variant.md); earlier, the part about the read-only guard was superseded by [ADR-0012](0012-codex-guard-as-plugin-hook.md)
- Date: 2026-09-29

## Context

I want damkit in Codex CLI (0.156) with OpenAI models as well. Codex has plugins
(`.codex-plugin/plugin.json`) with skills and hooks, and a marketplace (`.agents/plugins/marketplace.json`),
but it differs from Claude Code in places damkit relies on:
- a plugin **cannot contain agents**. Agents are TOML files in `<project>/.codex/agents/`
  (`developer_instructions`, `model`, `model_reasoning_effort`, `sandbox_mode`);
- the documentation does not describe the **agent type** in the `PreToolUse` hook input, so we can't rely on
  a plugin hook telling a reviewer apart from the main session, as `hooks/guard_readonly.py` does (ADR-0003).
  The 0.156 binary has an optional `agent_type` in its schema, but it is unknown whether it gets filled in;
- Codex does have a native per-agent sandbox (`sandbox_mode = "read-only"`: no writes and no network at the OS level);
- there is no `paths:` in skills, no per-agent worktree isolation, and no preloading skills into an agent.

## Decision

- **`codex/` is an independent, manually adapted copy**: the `dampe` plugin and marketplace in one
  directory, 16 skills, 9 roles. Only real files, no symlinks and no references outside `codex/`.
- **Roles as TOML installed by a script** (`codex/scripts/install_agents.py`) into the project's
  `.codex/agents/`, together with the guard in `.codex/damkit/`. Names in snake_case (`code_reviewer`).
- **Read-only = sandbox + guard in the role's TOML.** `sandbox_mode = "read-only"` is the main boundary.
  A port of the guard (without the agent filter) is wired as `[[hooks.PreToolUse]]` into the file of each of the 7 roles
  from `READONLY_AGENTS`. `probe_agent_hooks.sh` checks whether Codex honors hooks from the agent layer.
- **Models:** roles that have `sonnet` in the Claude version get `model = "gpt-6-sol"`; `inherit`
  roles have no `model` field. `model_reasoning_effort` is explicit, as in ADR-0008.

## Alternatives considered

- **`codex/skills/` generated from `skills/` + a test detecting drift**: one source of truth, but
  an extra tool and transformations for two audiences. Rejected: I prefer an independent copy that
  can be changed for Codex without worrying about a generator.
- **Symlinks to `../skills`**: the content would stay Claude-specific (`/damkit:…`, subagent names,
  `${CLAUDE_PLUGIN_ROOT}`), and Codex copies the plugin into a cache, so symlinks may not survive installation.
- **A global guard in a plugin or project hook**: without a reliable agent type, it would also block the main
  session (`git commit`, `rm`, `npm install`). If the probe shows that `agent_type` is filled in,
  we return to this option with a new ADR.

## Consequences

- Changes in `skills/`, `agents/` and `hooks/` have to be ported to `codex/` by hand. A line in
  `CLAUDE.md` is a reminder, and `codex/scripts/check.py` catches Claude leftovers.
- OpenAI model names have to be updated when their list changes.
- If `probe_agent_hooks.sh` shows that hooks in the agent's TOML don't work, only the sandbox protects: commands against the cluster
  require human approval, and after approval nothing mechanically blocks e.g. `kubectl apply`.
- `implementation_worker` has no worktree isolation. Parallel work only on disjoint files.

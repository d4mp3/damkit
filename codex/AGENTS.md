# devkit for Codex

This directory is the Codex variant of devkit: a Codex plugin (`.codex-plugin/plugin.json`) and its
marketplace `dampe` (`.agents/plugins/marketplace.json`). It is an independent, hand-adapted copy of
the Claude plugin at the repo root (ADR-0011): real files, no symlinks, nothing referenced outside
`codex/`. Human docs are in Polish, model-facing files in English.

## Commands
- Static checks: `python3 codex/scripts/check.py`
- Guard tests: `python3 codex/hooks/test_guard_readonly.py`
- Installer and checker tests: `python3 codex/scripts/test_install_agents.py`, `python3 codex/scripts/test_check.py`
- End-to-end guard check with the installed plugin: `bash codex/scripts/verify_guard.sh` (calls the model)

## Conventions
- Agents are stack-agnostic roles in `agents/<snake_case>.toml`; technology knowledge goes into skills.
  Plugins cannot ship agents: `scripts/install_agents.py` copies them into a project.
- `developer_instructions` is always a `'''literal'''` TOML string.
- The read-only guard is a plugin hook (`hooks/hooks.json`) filtered by the payload's `agent_type`.
  A read-only role gets `sandbox_mode = "read-only"`, an entry in `READONLY_AGENTS` in
  `hooks/guard_readonly.py` and in `READONLY_GUARDED` in `scripts/check.py`, and a guard test case.
  Never put `[[hooks…]]` in an agent TOML: Codex does not run hooks declared there.
- The guard hook command ends with `|| true`: it fires in every session, and a missing guard file
  would otherwise exit 2 and block every command.
- Set `model_reasoning_effort` explicitly on reviewers and investigators (ADR-0008). Pin `model` only
  for roles that are `sonnet` in the Claude variant, to `gpt-6-sol`.
- Skill `description` = when to use it; Codex has no `paths:` triggers, so name file patterns there.
  Refer to files inside a skill relative to the skill directory, never by plugin root.
- Bump `version` in `.codex-plugin/plugin.json` on every behavior change.
- A change ported from the Claude variant keeps the same intent; note Codex-specific differences in README.md.

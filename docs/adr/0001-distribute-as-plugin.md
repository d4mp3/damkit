# ADR-0001: damkit is distributed as a Claude Code plugin installed per project

- Status: Accepted
- Date: 2026-09-29

## Context

The configuration (agents, skills) should be universal and used across many projects: a CLI validator,
a validation web service, a forestry platform, a k3s homelab. The original version lived in loose
`agents/*.yaml` files, which Claude Code did not load, because it only supports `.md` files. I also
want to decide in which projects damkit is active.

## Decision

The repo is both a plugin (`.claude-plugin/plugin.json`) and a marketplace
(`.claude-plugin/marketplace.json`, `source: "./"`). I install it in projects with
`claude plugin install damkit@dampe --scope project`.

## Alternatives considered

- **Symlink into `~/.claude`**: active everywhere, with no per-project control and no versioning.
- **Copying files into the project's `.claude/`**: the copies quickly drift apart.

## Consequences

- Plus: one source of truth, a version in `plugin.json`, installation with one command.
- Minus: names have a prefix (`damkit:code-reviewer`, `/damkit:mentor`).
- Minus: plugin agents ignore `permissionMode`, `hooks` and `mcpServers` (see ADR-0003).
- Minus: a plugin cannot ship `rules/`. Path-dependent knowledge is carried by skills with a `paths` field.

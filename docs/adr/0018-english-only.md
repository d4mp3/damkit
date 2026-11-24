# ADR-0018: All repository text in English

- Status: Accepted (supersedes [ADR-0005](0005-language-policy.md)); the part about example UI copy refined by [ADR-0019](0019-setup-damkit-writes-project-claude-md.md)
- Date: 2026-11-16

## Context

ADR-0005 kept model-facing text (agents, skills, `CLAUDE.md`) in English and human-facing text
(README, `docs/`, ADRs) in Polish, because I was the only reader of the latter. Its consequences
already noted that publishing the plugin would mean translating README and `docs/`. The repository
is now going public.

## Decision

- **Everything in the repository is written in English**: `README.md`, `docs/` (including ADRs),
  agents, skills, `CLAUDE.md`, code comments and names.
- Skills that talk to the user (e.g. `mentor`) still answer in the language of the conversation.
- Polish stays where it is part of the content rather than its language: example UI copy, trigger
  phrases in skill descriptions, and Polish-specific domain knowledge (EPSG:2180, Geoportal).

## Alternatives considered

- **Keep Polish docs and add English translations**: two copies to keep in sync, and they would drift.
- **Keep Polish docs**: makes the public repository unreadable for most visitors.

## Consequences

- Existing ADRs are translated in place; their decisions and dates do not change.
- `docs/dokumentacja.md` is renamed to `docs/documentation.md`.

# ADR-0005: Model-facing text in English, human-facing text in Polish

- Status: Superseded by [ADR-0018](0018-english-only.md)
- Date: 2026-09-29

## Context

The repo contains two kinds of text. One is read mainly by the model: agent prompts, skills, `CLAUDE.md`.
The other is read mainly by me: README, ADRs, `docs/`. Mixing languages within one kind
makes maintenance harder.

## Decision

- **In English:** `agents/`, `skills/`, `CLAUDE.md`, code comments and names. Technical
  terminology and tool names are in English, and skill descriptions also match English queries.
- **In Polish:** `README.md`, `docs/` (including ADRs).
- Skills that talk to me (e.g. `mentor`) answer in the language of the conversation.

## Alternatives considered

- **Everything in English**: ready for publishing, but I am the one who mostly writes and reads README and ADRs.
- **Everything in Polish**: prompts would mix Polish with English terminology.

## Consequences

If I ever make the plugin public, only README and `docs/` will need translating.

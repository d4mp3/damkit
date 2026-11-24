# ADR-0006: We document the "why", generate the "what", and check freshness in review

- Status: Accepted; the part about the `adr` skill superseded by [ADR-0013](0013-process-belongs-to-matt-pocock-skills.md)
- Date: 2026-09-29

## Context

The model reads code quickly and accurately, so a description of what the code does is redundant. Such a description
goes stale, and outdated documentation misleads, because the model trusts it. Code, however, does not reveal
the reasons behind decisions, rejected options, domain constraints or operational knowledge.

## Decision

- The rules for writing documentation live in the `documenting-code` skill. It is the single source of truth
  used by both the model and me.
- We record decisions as ADRs (the `adr` skill, `/damkit:adr`). An accepted ADR is not edited,
  only superseded by a new one.
- There is no separate documentation agent. The "why" is in the main session's conversation, and a subagent
  starts without it.
- `code-reviewer` reports documentation that the diff made outdated, and a missing ADR for
  decisions that are hard to reverse.

## Alternatives considered

- **A `docs-writer` agent**: it would write descriptions of code, which is exactly what we don't want.
- **No documentation ("the code is the documentation")**: loses the reasons and operational knowledge.

## Consequences

- Documentation is smaller, but every piece of it carries information that is not in the code.
- Contracts (OpenAPI, JSON Schema for validator rules, `--help`) are generated in CI.
- This repo applies these rules to itself: README, `CLAUDE.md`, `docs/adr/`.

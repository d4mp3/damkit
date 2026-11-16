# ADR-0004: Code exploration uses the built-in Explore agent instead of our own `codebase-explorer`

- Status: Accepted
- Date: 2026-09-29

## Context

The first version had `codebase-explorer` (haiku, read-only). Claude Code has a built-in agent
`Explore` with the same purpose. Two agents with the same description make the main session
pick between them at random.

## Decision

We remove `codebase-explorer`. `Explore` is used for exploration. The previous version is in `_archive/agents-v1/`.

## Alternatives considered

- **Keep it and specialize it** (e.g. git history analysis): there was no concrete need.
  We will come back to this if `Explore` turns out to be insufficient.

## Consequences

One agent less to maintain and no competing descriptions when delegating.

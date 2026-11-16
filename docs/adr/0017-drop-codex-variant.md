# ADR-0017: Dropping the Codex CLI variant

- Status: Accepted (supersedes [ADR-0011](0011-codex-variant-as-independent-copy.md) and [ADR-0012](0012-codex-guard-as-plugin-hook.md))
- Date: 2026-11-16

## Context

ADR-0011 added an independent, manually maintained copy of devkit for Codex CLI in `codex/`, and ADR-0012
moved the read-only guard there into a plugin hook. Since then the Claude version has been rebuilt
around Matt Pocock's skills (ADR-0013), got a review of the knowledge skills (ADR-0014), QRSPI steps (ADR-0015)
and LSP servers (ADR-0016). None of these changes reached `codex/`, so the copy drifted,
and every further change in `skills/`, `agents/` and `hooks/` increased the backlog.

## Decision

- I'm no longer developing the Codex CLI variant. The `codex/` directory is removed from the repo.
- devkit is only a Claude Code plugin. Changes in `skills/`, `agents/` and `hooks/` no longer require
  porting or running `codex/scripts/check.py`.

## Alternatives considered

- **Keep `codex/` unmaintained**: the copy would be misleading, because it describes the state before ADR-0013.
- **Catch up with the Claude version**: doubles the cost of every change, and I don't use Codex day to day.

## Consequences

- The last version of the variant remains in git history (before the commit that removes `codex/`).
- Mentions of `codex/` in ADR-0013–0016 describe the state at the time of the decision and stay unchanged.
- Returning to Codex means a new ADR, not restoring the old copy.

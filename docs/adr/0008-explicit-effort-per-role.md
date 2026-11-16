# ADR-0008: Explicit `effort` for agents whose quality must not depend on the session

- Status: Accepted
- Date: 2026-09-29

## Context

When the `effort` field is omitted in an agent, the agent **inherits the level from the session**. Supported
values are `low`, `medium`, `high`, `xhigh`, `max`, depending on the model. There is no `inherit` value.
In the first version only `test-runner` had `effort`. The result: with a session on `low` (a quick
question) a security review would also run on `low`, and with a session on `max` `test-runner` would
overthink for no reason and burn tokens.

## Decision

| Agent | effort | Reason |
|---|---|---|
| `security-reviewer` | `xhigh` | a missed vulnerability costs the most. `max` rejected: prone to overanalysis and false alarms. |
| `code-reviewer`, `postgres-reviewer`, `platform-reviewer`, `frontend-reviewer` | `high` | searching for edge cases and verification |
| `cluster-investigator` | `high` | forming and rejecting hypotheses |
| `test-runner`, `docs-researcher` | `medium` | the task is well defined, speed matters |
| `implementation-worker` | *(inherits)* | difficulty comes from the task, and that is already expressed by the level you work at in the session |

## Alternatives considered

- **Don't set it anywhere**: review quality would depend on an incidental session setting.
- **`max` for all reviewers**: high cost, and the documentation warns against overanalysis.

## Consequences

- Review cost is predictable. If it turns out too high, the first candidate for lowering is
  `code-reviewer` to `medium`.
- On models without `xhigh`, Claude Code falls back to the nearest lower level.

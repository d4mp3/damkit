# ADR-0013: The work process belongs to Matt Pocock's skills; damkit provides knowledge and roles

- Status: Accepted; extended by [ADR-0015](0015-qrspi-steps-extend-matts-flow.md) (QRSPI steps)
- Date: 2026-10-01
- Supersedes: the part of ADR-0006 about the `adr` skill

## Context

In projects I use damkit and Matt Pocock's skills (`mattpocock/skills`) at the same time. Matt
defines the full process: `/grill-with-docs` → `/to-spec` → `/to-tickets` → `/implement` (with `/tdd`
and `/code-review`), plus a domain glossary in `CONTEXT.md`, an ADR format (`domain-modeling`),
a task tracker in `docs/agents/` and multi-session learning (`/teach`). Damkit had its own versions of some
of these steps: an `adr` skill with a different format and a different threshold for proposing an ADR, `review-changes`
triggered by the same words as `/code-review`, a "plan → `implementation-worker`" workflow
competing with tickets, and `mentor` with study plans. Two skills with the same trigger
make the model pick between them at random (the same problem as in ADR-0004). I don't edit Matt's
skills, because they are updated from upstream (`skills-lock.json`), so damkit has to adapt.

## Decision

- The process (from idea to commit), the domain glossary, the ADR format and the task tracker belong to Matt's skills.
  Damkit has no own versions of these steps.
- Damkit provides stack knowledge (skills), roles for isolation and parallelism (agents), and
  the read-only hook. It plugs into specific steps of Matt's flow:
  - `review-changes` is the third review axis, **Risk**, run after `/code-review` (Standards + Spec)
    and reported separately;
  - `implementation-worker` implements tickets from the frontier (all blockers closed) in parallel,
    one ticket per worker, following `tdd` on the seams agreed in the spec;
  - `test-runner` runs the final test pass in `/implement`, `docs-researcher` handles
    `/research` about libraries, `mentor` teaches during a real task, `/teach` runs multi-session learning.
- We remove the `adr` skill. ADRs in projects are written by `domain-modeling` (invoked by `/grill-with-docs`).
- The project's ADRs and `CONTEXT.md` take precedence over damkit skills. Contracts described
  in knowledge skills (e.g. validator exit codes) are default proposals to grill, not facts.
- The connection lives in two places: in the damkit skill descriptions (so they don't compete for triggers)
  and in the `## Workflow` section of the project `CLAUDE.md` template (it always loads, so `/implement` applies it).

## Alternatives considered

- **Damkit with its own full process, without Matt**: I would duplicate a maintained upstream and lose
  its development (grilling, tickets with blockers, two-axis review).
- **Fork and edit Matt's skills**: every upstream update would mean manual merging.
- **Leave `adr` and `review-changes` unchanged**: two ADR formats in one `docs/adr/`
  and a double review after every `/implement`.

## Consequences

- Damkit is smaller: there is no `adr` skill and no ADR template for projects.
- Without Matt's skills in a project, some references (`/code-review`, `domain-modeling`, `tdd`) don't work.
  Damkit still provides knowledge and reviewers, but it does not drive the process.
- This repo still records its own decisions as ADRs in `docs/adr/` in the existing format.
- The `codex/` variant is not adapted yet (ADR-0011: independent copy).

# ADR-0026: A user-invoked `ask` skill answers from one workflows file

- Status: Accepted
- Date: 2026-11-16

## Context

geostack's workflows (which steps, agents and skills to use in a given situation) lived in the
README, next to installation and the agent and skill catalog. Finding the right one meant reading
a 700-line page. The workflows were also hard to read:
- prose inside code blocks, with arrows instead of sentences;
- steps without a subject, so it was unclear whether you, Claude or an agent acts;
- undefined terms (frontier, seam, fixed point);
- the main flow told three times, with small differences.

Matt Pocock's skills solve the same problem with `/ask-matt`: a router you invoke with a question.

## Decision

- The workflows move to `docs/workflows.md`, the single source for people and for the skill. It
  opens with a situation index, then the main flow, then one section per workflow: a **When** line,
  numbered steps with an explicit actor, and **Watch out** points. The README links to it.
- A new skill `ask` (`/geostack:ask <situation>`) reads that file, checks what is set up in the
  project, picks the matching workflow and adapts its steps to the user's case. It doesn't run them.
- `ask` has `disable-model-invocation: true`. Its description never competes with the triggers of
  Matt's process skills (ADR-0013) and costs no context until the user calls it.
- Questions about Matt's process itself (phase boundaries, `/wayfinder`, `/triage`) go to `/ask-matt`.

## Alternatives considered

- **A model-invoked skill**: answers "how do I…?" without a slash command, but its description
  would compete with `/ask-matt` and the process skills on every turn.
- **Workflows copied into the skill's `references/`**: two copies, and one of them goes stale.
- **The skill reads the whole README**: installation, the catalog and the ADR table are noise for
  the question, and the README keeps mixing reference with how-to guides.
- **Workflows rewritten in place in the README**: readable, but the page stays long and mixes modes.

## Consequences

- A workflow change goes into `docs/workflows.md` only, and `ask` picks it up with no change of its own.
- Section headings in `docs/workflows.md` are link targets for the README and for `ask`'s answers,
  so renaming one means updating those links.
- `ask` depends on `docs/` being shipped with the plugin, which it is: the marketplace source is the repo root.

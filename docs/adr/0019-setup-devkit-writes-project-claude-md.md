# ADR-0019: `setup-devkit` writes the project `CLAUDE.md`, including its languages

- Status: Accepted (refines the part of [ADR-0018](0018-english-only.md) about example UI copy)
- Date: 2026-11-16

## Context

Setting up a project meant copying `templates/CLAUDE.project.md` by hand, filling its placeholders and
only then running `/setup-matt-pocock-skills`. The order was fragile: run the other way round, Matt's
skill asks which file to create, and devkit's `## Workflow` rules end up away from his pointers.

Some skills also assumed Polish: `building-ui` asked for Polish UI copy with `pl-PL`, `frontend-stack`
for test queries against Polish labels, and the template hardcoded `UI copy: Polish`. That fit my
projects, but a public plugin would push Polish into everyone's UI.

## Decision

- A new user-invoked skill, `/devkit:setup-devkit` (`disable-model-invocation: true`), writes or completes
  the project's `CLAUDE.md` from its asset `skills/setup-devkit/assets/CLAUDE.project.md`, then hands off
  to `/setup-matt-pocock-skills`. `templates/` is gone.
- It reads facts from the repo (commands from CI and manifests, which sections apply, existing ADRs) and
  asks only what the repo can't tell: conversation, UI copy, locale, docs and commit languages.
  Decisions (CRS, map library, design system foundation, deployment) stay placeholders for `/grill-with-docs`.
- The template gets a `## Language` section. `building-ui` and `frontend-stack` take the UI language and
  locale from it instead of assuming Polish; Polish examples stay only as illustrations.

## Alternatives considered

- **Keep the manual copy**: zero code, but the ordering trap and the placeholders stay with the user.
- **Ask about decisions too**: one interview for everything, but it would compete with `/grill-with-docs`
  and record decisions without an ADR (ADR-0013).
- **Keep Polish defaults in skills**: right for me, wrong for anyone else installing the plugin.

## Consequences

- This is devkit's third process step after the QRSPI ones (ADR-0015); its output goes to
  `/setup-matt-pocock-skills`.
- Projects set up before this change have no `## Language` section; running the skill again adds it.
- A skill that depends on the project's language reads `## Language` and asks once when it's missing.

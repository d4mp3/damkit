# ADR-0009: UI quality through a design system and a visual loop, without a "UI/UX designer" agent

- Status: Accepted
- Date: 2026-09-29

## Context

Models know the principles of UI design. In practice, though, they have recurring weaknesses: generic
aesthetics (the "AI look"), inconsistency between screens (every session starts from scratch), no
preview of the result, and skipped states (no data, error, overflow). Iterating alone produces an
acceptable single screen, but not a consistent platform, and it costs my time on every screen.

## Decision

- The `building-ui` skill contains the process (the project's design system first, the screen's goal, build
  rules, a states table, anti-patterns), **mandatory verification with screenshots**
  (`npx playwright screenshot`) before reporting that it is done, and patterns for data-heavy screens
  and maps.
- Asset `assets/tokens.css`: starter tokens in 3 layers, with checked WCAG contrast.
- `frontend-reviewer` gets `building-ui` preloaded, checks consistency with the design system and, when
  the UI can be rendered, takes screenshots.
- The `CLAUDE.project.md` template has a **Design** section for the decisions of a specific product.
- The guide [`docs/design-system.md`](../design-system.md) describes how to build a design system
  and how to work with it.

## Alternatives considered

- **A "UI/UX designer" agent or persona**: a persona adds no knowledge, and UI design requires
  continuous exchange with me, which a subagent doesn't have (ADR-0002).
- **Only iterating with the model**: leads to drift between screens and mediocre aesthetics.
- **Only the official `frontend-design` skill**: it focuses on aesthetic direction,
  not on the design system, states, verification and tools for working with data. It can be used alongside.

## Consequences

- The character, brand and patterns of a specific product live in the product's repo (`CLAUDE.md`, tokens,
  Storybook), not in devkit.
- The visual loop requires a running dev server or Storybook, and Playwright browsers.
  Without them, the agent must state explicitly that there was no visual verification.
- No skill replaces UX research with users (interviews, tests).

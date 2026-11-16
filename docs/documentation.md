# How we keep documentation

A guide for people. The detailed writing rules, which the model also uses, are in
[`skills/documenting-code/SKILL.md`](../skills/documenting-code/SKILL.md). This file does not repeat them,
it only shows how to apply them day to day. Rationale for the approach:
[ADR-0006](adr/0006-documentation-strategy.md).

> Last verified: 2026-09-29

## The rule in one sentence

Document what cannot be read from the code (**why**, constraints, decisions, operations).
Generate what can be generated from the code. Skip the rest.

## Three questions before you write anything

1. Will a model or a person read this from the code? **Yes** → don't write it, fix the names and types.
2. Can it be generated from the code? **Yes** → generate it in CI (OpenAPI, JSON Schema, `--help`).
3. Does only a person know it? **Yes** → write it down in the right place (table below).

## Map: what lives where

| Knowledge | Place | Who reads it | Example in this repo |
|---|---|---|---|
| What it is, how to install and use it | `README.md` | people | [README](../README.md) |
| Facts for the AI assistant | `CLAUDE.md` | model | [CLAUDE.md](../CLAUDE.md) |
| Domain glossary: terms and synonyms we avoid | `CONTEXT.md` (skill `domain-modeling`) | both | (in projects) |
| Decisions and their reasons | `docs/adr/NNNN-*.md` | both | [docs/adr/](adr/) |
| What we build and why: spec, tickets | issue tracker (`/to-spec`, `/to-tickets`) | both | (in projects) |
| Configuration of Matt's skills: tracker, labels, document layout | `docs/agents/*.md` | model | (in projects) |
| How to do or fix something | `docs/runbooks/*.md` | people under stress | (in homelab projects) |
| How to work in a given area (workflow) | `docs/*.md` (how-to guides) | people | [design-system.md](design-system.md), this file |
| Visual UI contract | tokens + Storybook (generated from code) | both | [tokens.css](../skills/building-ui/assets/tokens.css) (starter) |
| Longer domain explanations that don't fit in the glossary | `docs/explanation/*.md`, linked from `CONTEXT.md` | both | (in the forest platform) |
| Function or class contract | docstring | both | — |
| Non-obvious "why" in code | comment next to the line | both | `hooks/guard_readonly.py` |

## Lifecycle

| Event | What you do | devkit help |
|---|---|---|
| A decision that is hard to reverse was made | new ADR | `/grill-with-docs` writes it along the way; outside it, skill `domain-modeling` |
| A decision changes | new ADR that supersedes the old one; in the old one you change only the status | skill `domain-modeling` |
| A new term, or a term changes meaning | entry in `CONTEXT.md` | `/grill-with-docs`, `domain-modeling`; `code-reviewer` flags drift |
| Change of behavior, name, command, env variable | documentation update **in the same diff** | `code-reviewer` flags outdated documentation |
| The model makes the same mistake a second time | one line in `CLAUDE.md` | — |
| A document stopped being true and nobody will maintain it | you delete it | — |
| A runbook or guide was tested live | you update `Last verified:` | — |
| New or changed UI component | story with all states in the same diff | skill `building-ui`, `frontend-reviewer` |

## Checklist before commit

- [ ] Does the diff change something that the README, `CLAUDE.md` or a runbook describes? If so, updated.
- [ ] Does the diff introduce a decision that is hard to reverse? If so, there is an ADR.
- [ ] Do new comments say "why", not "what"?
- [ ] Did I avoid adding a description of code that will go stale with the next change?

`/devkit:review-changes` (`code-reviewer`) checks the first two items automatically.

## Anti-patterns

- A docstring that repeats the signature (`"""Returns the user."""` on `def get_user() -> User`).
- An "Architecture.md" describing modules: outdated after the first refactor.
- A copy of README commands in `CLAUDE.md` instead of a link.
- Editing an old ADR so it "fits" a new decision. You lose the history.
- A `TODO` with no reason and no issue number.
- Describing a component's look in prose instead of a story in Storybook.

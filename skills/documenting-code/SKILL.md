---
name: documenting-code
description: Use when writing or updating human-facing documentation - README, docstrings, code comments, runbooks, docs/ pages, CLI help, API docs - or when deciding whether something should be documented at all and where it goes, or when existing docs look stale or contradict the code.
---

# Documenting code

Documentation exists to carry what the code cannot. Anything a reader (human or LLM) can
reliably reconstruct from the code is a liability in prose: it goes stale, and stale docs
are worse than none because readers trust them over the code.

## Decide first: write, generate, or skip

For each piece of information, ask in this order:

1. **Can it be derived from the code?** (what a function does, its parameters, the module
   structure). If so, **skip it.** Improve names and types instead.
2. **Can it be generated from the code?** (the API schema, the config schema, CLI help, the list of
   env vars). If so, **generate it** in CI: FastAPI → OpenAPI, Pydantic → JSON Schema,
   Typer/argparse → `--help`, docstrings → mkdocstrings.
3. **Only a human knows it?** (why, constraints, decisions, operations, domain context). If so,
   **write it**, in the place listed below.

## Where each kind of knowledge goes

| Knowledge | Place | Rule |
|---|---|---|
| Why this non-obvious code is like this | a comment at that line | The *why* or the hazard, never the *what*. |
| The contract of a public function or class | its docstring | Semantics the types don't show: units, CRS, invariants, side effects, raised errors. |
| Domain vocabulary (what a term means, which synonyms to avoid) | `CONTEXT.md` | Owned by the domain-modeling skill and its format. Use its terms everywhere else. |
| A decision with alternatives | `docs/adr/NNNN-*.md` | Written via the domain-modeling skill, in its format. Never edited after acceptance; supersede it instead. |
| What to build and why (spec, tickets) | the issue tracker | Via /to-spec and /to-tickets, as `docs/agents/issue-tracker.md` says. Not in `docs/`. |
| How to run, test and deploy | `README.md` | A quickstart that CI actually executes, or at least the same commands CI runs. |
| Facts an AI assistant needs | `CLAUDE.md` | Short (aim for under 100 lines), only what isn't inferable, with pointers instead of copies. |
| How to operate or recover | `docs/runbooks/*.md` | Task-oriented, copy-pasteable commands, with a `Last verified:` date and tool versions. |
| Longer domain explanation (forestry, GIS rules) | `docs/explanation/*.md` | Only what a glossary entry can't hold. Linked from `CONTEXT.md`, uses its terms, links to code instead of restating it. |

This follows the Diátaxis split: tutorials, how-to guides (runbooks), reference (generated),
and explanation (ADRs, domain). Don't mix the modes in one page.

`docs/agents/*.md` is configuration for the engineering skills (issue tracker, labels, domain
layout), not documentation. Edit it only when that configuration changes.

Decisions in this stack that usually deserve an ADR: the storage CRS, the GitOps repo layout,
the design-system foundation, a service split, a new infrastructure component.

## Writing rules

- **Concrete over general.** Write "EPSG:2180, metres" and not "a projected CRS". Write `uv run pytest -q` and not "run the tests".
- **One source of truth.** Link to the canonical place and don't copy. Two copies means one is wrong.
- **Same change, same PR.** When behavior changes, update the docs that describe it in the same diff.
  If a doc no longer matches and nobody will maintain it, delete it.
- **Date what decays.** A runbook or guide whose commands depend on tool versions carries
  `Last verified: YYYY-MM-DD (tool versions)`, e.g. `Last verified: 2026-11-16 (ArgoCD 3.1, k3s 1.31)`,
  updated only when someone runs the commands again. Guides about method or principles carry no date:
  an unmaintained date claims a check that never happened.
- **No marketing, no filler.** Every sentence either instructs, constrains or explains a reason.

## Comments: good vs noise

```python
# noise: restates the code
# loop over features and check validity
for f in features:
    ...

# useful: explains a constraint the code cannot show
# fid is not stable across GeoPackage re-exports; match on the business key instead.
key = f["properties"]["nr_wydz"]

# useful: marks a hazard with a reference
# PgBouncer runs in transaction mode: server-side cursors break (see ADR-0007).
DISABLE_SERVER_SIDE_CURSORS = True
```

`TODO` comments need a reason and an issue/ADR reference, or they are just noise.

## CLAUDE.md specifically

When editing CLAUDE.md or AGENTS.md, the writing-for-agents skill governs how to word it; this
section only says what belongs there. The `## Agent skills` block is owned by
`/setup-matt-pocock-skills`, and `## Workflow` by the damkit template: don't rewrite them in passing.

- Put in it the commands, the architecture in 3–10 bullets, conventions the code doesn't enforce, and the deploy target.
- Keep out of it the code tours, style rules a linter enforces, and anything duplicated from README.
- Add a line when you had to correct the assistant twice for the same thing. Remove lines that
  stop being true.
- A decision that constrains everyday coding gets a one-line pointer to its ADR
  (`- Geometries stored in EPSG:2180, see docs/adr/0003-storage-crs.md`), and the code where it
  matters gets a comment containing `ADR-NNNN`.

## Checking for staleness

When a change renames or removes something (a function, command, env var, flag, endpoint, setting, file):

```bash
git grep -n -i "<old name>" -- '*.md' '*.rst' '*.txt' 'docs/' '*.py'
```

Every hit in prose is either updated in the same change or reported as documentation drift.

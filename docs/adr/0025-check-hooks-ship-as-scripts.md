# ADR-0025: Format and check hooks ship as scripts copied into the project

- Status: Accepted (refines [ADR-0024](0024-setup-writes-project-settings.md))
- Date: 2026-11-16

## Context

ADR-0024 had `setup-damkit` build hooks from each project's commands. In practice the model would
then write a new inline shell one-liner per project, with the subtle parts redone each time:
- reading the edited path from the hook's JSON;
- exit 2 rather than 1, and stderr rather than stdout;
- monorepo directories;
- not formatting with a tool the project doesn't use;
- not blocking a turn on errors in files nobody touched.

The user also asked for concrete tooling: ruff and mypy for Python, the equivalent for JS and TypeScript.

## Decision

- Three scripts live in `skills/setup-damkit/assets/hooks/`. Setup copies them to the project's
  `.claude/hooks/`, and the settings template registers them:
  - `format.sh` on `PostToolUse` (`Edit|Write`) formats the edited file: ruff format or black,
    prettier or biome. It exits 2 only on a parse error.
  - `check.sh` on `Stop` runs ruff and mypy on changed Python files and eslint or biome and tsc on
    changed JS/TS files. It keeps only errors in changed files and exits 2 on any.
  - `lib.sh` holds the shared detection.
- A tool runs only when the project depends on it (`.venv/bin`, `node_modules/.bin`) or configures it.
  The same scripts then fit every stack without edits.
- No tests in hooks. They run at every turn's end, so tests belong to `test-runner` and CI.
- The copies belong to the project: a rerun of setup doesn't overwrite them, and `check.sh` takes the
  wanted tools as arguments.
- How the system works, for users, is in `docs/project-settings.md`.

## Alternatives considered

- **Plugin-level hooks (`hooks/hooks.json` in damkit)**: no copying, but they would run in every
  project with damkit enabled. They would also miss teammates without the plugin and cloud sessions,
  where plugins don't load.
- **Inline commands generated per project (ADR-0024 as written)**: different, untested logic in every
  repo.
- **Linting on `PostToolUse`**: errors mid-edit are noise, and auto-fix removes imports the next edit
  needs.

## Consequences

- Projects carry three small scripts and need `bash` plus `jq` or `python3`.
- Improvements to the scripts reach a project only when someone copies them again. That is a
  deliberate trade for owning and editing them locally.

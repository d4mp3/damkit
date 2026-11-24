# ADR-0016: damkit ships LSP servers for TypeScript and Python in `.lsp.json`

- Status: Accepted
- Date: 2026-11-14

## Context

With an LSP server, Claude gets diagnostics after every edit (type errors, missing imports) and the
`LSP` tool for navigating symbols instead of searching text. My stack is TypeScript/React and Python
(Django/FastAPI). Anthropic publishes ready-made `typescript-lsp` and `pyright-lsp` plugins
in `claude-plugins-official`, but they are installed separately, and damkit is installed per project (ADR-0001).

## Decision

damkit has a `.lsp.json` in its root directory with two servers: `typescript-language-server --stdio`
(`.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs`, `.cjs`) and `pyright-langserver --stdio`
(`.py`, `.pyi`). The configuration is the same as in the official plugins. The plugin doesn't
ship the binaries: they are installed once per machine and must be on `PATH`.

## Alternatives considered

- **`dependencies` on the official `typescript-lsp` and `pyright-lsp`** (with
  `allowCrossMarketplaceDependenciesOn` in `marketplace.json`): no copy of the configuration, but disabling
  either of those plugins disables all of damkit, and dependencies from outside the `dampe` marketplace
  install without my control.
- **An "install the official plugins" instruction** in the README: one more step in every project,
  easy to skip.
- **`basedpyright` instead of `pyright`**: stricter default rules, but a separate binary and different
  behavior than in the official plugin. I'll come back to it if `pyright` turns out to be too weak.

## Consequences

- A project with damkit has TS and Python diagnostics without extra plugins.
- The official `typescript-lsp`/`pyright-lsp` have to be disabled where damkit runs, otherwise
  two servers start for the same files and diagnostics get duplicated.
- A missing binary doesn't break the plugin: `/plugin` → **Errors** shows `Executable not found in $PATH`.
- The Codex variant (`codex/`) stays unchanged: `.lsp.json` is a Claude Code plugin mechanism.

# Project settings and hooks

What `/damstack:setup-damstack` puts in a project besides `CLAUDE.md`, how each piece works, and
what stays in your user settings.

## Who decides and who enforces

Every instruction to Claude is one of two kinds:

| | Read by the model, usually followed | Enforced by Claude Code, always |
|---|---|---|
| What to do | `CLAUDE.md`, skills, the prompt | hooks |
| What it may touch | the auto mode classifier | `deny` rules, the sandbox |
| When the work is done | "run the tests", `/code-review` | the `Stop` hook, CI |

Leave a decision to the model when it can judge better with the code in front of it. Use the harness
for what must happen always or never. Two signals help:
- Claude keeps skipping a line in `CLAUDE.md` even after you emphasise it: make that line a hook.
- A hook enforces a mere preference: delete it and keep a line in `CLAUDE.md`.

## The files and who they reach

| File | Who it affects | What damstack puts there |
|---|---|---|
| `~/.claude/settings.json` | you, every project on this machine | nothing (see [User settings](#what-stays-in-your-user-settings)) |
| `.claude/settings.json` | everyone in the repo and cloud sessions (commit it) | deny/ask rules, hooks, the plugin |
| `.claude/settings.local.json` | you, this project, not committed | nothing; your personal overrides go here |
| `.claude/hooks/*.sh` | everyone (commit them) | `lib.sh`, `format.sh`, `check.sh` |
| `CLAUDE.md` / `CLAUDE.local.md` | the model / only you | the project instructions / your private notes |

`deny` and `ask` rules apply as soon as the file exists. Hooks, the marketplace and the plugin apply
after each person accepts the folder's trust dialog.

## What setup writes

### `.claude/settings.json`

```json
{
  "permissions": {
    "deny": ["Read(./.env)", "Read(./.env.*)", "Bash(git push --force *)", "Bash(git push -f *)",
             "Bash(git reset --hard *)", "Bash(git clean *)"],
    "ask":  ["Bash(git push *)", "Bash(gh pr create *)", "Bash(gh pr merge *)"]
  },
  "hooks": {
    "PostToolUse": [{ "matcher": "Edit|Write",
      "hooks": [{ "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/format.sh" }] }],
    "Stop": [{
      "hooks": [{ "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/check.sh" }] }]
  },
  "extraKnownMarketplaces": { "dampe": { "source": { "source": "github", "repo": "d4mp3/damstack" } } },
  "enabledPlugins": { "damstack@dampe": true }
}
```

The full template is
[`skills/setup-damstack/assets/settings.project.json`](../skills/setup-damstack/assets/settings.project.json).
Setup merges it into an existing file and adds the project's other secret files.

- **`deny`** is for what can't be undone if Claude gets it wrong once:
  - a secret read: the content lands in the transcript;
  - a force push, `reset --hard`, `git clean`.

  Deny is checked before the auto mode classifier and works in every permission mode. Bad code isn't
  on the list, because `git revert` undoes it. If the repo commits `.env.example`, setup lists the
  ignored env files by name instead of `.env.*`, so Claude can still read the example.
- **`ask`** puts you back in the loop, even in auto mode, before something leaves your machine:
  a push or a PR.
- **Limits of rules:** they match tool calls, not intent. `Bash(git push --force *)` doesn't catch
  `git -C dir push --force`. `Read(./.env)` doesn't stop a script that opens the file; the sandbox does.
  A rule is a safety net, not a guarantee.

### The format hook: `PostToolUse` → `format.sh`

It runs after every `Edit` or `Write` and formats only the edited file, with the formatter the project
already uses:

| File | Formatter, first one found |
|---|---|
| `*.py`, `*.pyi` | `ruff format`, else `black` |
| `*.js`, `*.jsx`, `*.ts`, `*.tsx`, `*.mjs`, `*.cjs`, `*.css`, `*.scss`, `*.json` | `prettier --write`, else `biome format --write` |

How it works:
- **The project's own copy of the tool.** It uses `.venv/bin/<tool>` or `node_modules/.bin/<tool>`,
  falling back to a tool on `PATH` only when the project configures it (`[tool.ruff]`, `ruff.toml`…).
  A project that doesn't use prettier never gets prettier-formatted files.
- **Monorepos.** It runs from the nearest directory with `pyproject.toml` or `package.json`, so
  `frontend/` and `backend/` each use their own config.
- **Exit codes.** It exits 0 except when the formatter can't parse the file. Then exit 2 shows Claude
  the syntax error right away (`ruff format: error: Failed to parse src/x.py:1:12`). The edit itself
  stays: `PostToolUse` can't undo it.
- **It doesn't lint.** An import added now is used by the next edit, so an "unused import" error after
  each edit is noise, and `--fix` would delete the import. Linting waits for the end of the turn.

### The check hook: `Stop` → `check.sh`

It runs when Claude is about to end its turn. It checks **the files changed since the last commit**,
tracked and new:

| Files | Lint | Types |
|---|---|---|
| Python | `ruff check` | `mypy` |
| JS/TS | `eslint` (when it has a config), else `biome lint` | `tsc --noEmit` (or `tsc -b` for a root with `references`) |

If any of them reports an error in a changed file, the script prints it to stderr and exits 2. Claude
Code then doesn't end the turn and hands the errors to Claude, which fixes them and tries again:

```
you:     add an endpoint returning a parcel's area
Claude:  …edits views.py… "Done."
Stop:    mypy (.): src/parcels/views.py:42: error: Incompatible return value type (got "float", expected "str")
         → exit 2, the turn continues
Claude:  …fixes the return type… "Done."
Stop:    clean → exit 0, you get the answer
```

Design choices:
- **Changed files only, errors in changed files only.** Type checkers see the whole project, but the
  script keeps only the lines that report a changed file. A pre-existing error in a file nobody touched
  doesn't block the turn. One in a file Claude edited does, so touching a legacy file means cleaning it.
- **No tests.** The hook runs at the end of every turn, including turns where you only asked a question.
  A clean tree exits at once; the cost comes when files have changed: ruff takes milliseconds, mypy and
  tsc a few seconds with their caches. A full test suite on every answer would cost minutes. Tests are
  for the `test-runner` agent and CI.
- **Only tools the project uses.** Detection works as in `format.sh`. To run fewer tools, list them:
  `check.sh ruff eslint tsc`. Setup does that when a tool is too slow or noisy for every turn, e.g.
  mypy on a large untyped codebase.
- **Exit 2, not 1.** Claude Code treats exit 1 as a non-blocking error and ends the turn anyway.
  Exit 2 sends Claude back, and only stderr reaches it.
- **It can't loop forever.** After several blocks in a row without any tool call in between, Claude Code
  lets the turn end.

Are ruff and mypy enough for Python? For per-turn checks, yes:
- ruff covers what flake8, isort, pyupgrade and parts of bandit used to.
- mypy covers types. A project on pyright instead can drop mypy: damstack's Pyright LSP server
  already shows Claude type errors after every edit.

For JS/TS, the equivalents are prettier (format), eslint (lint) and tsc (types), with biome replacing
the first two where a project uses it. Slower or less frequent checks belong in pre-commit and CI:
tests, dependency audit, secret scanning.

## Hooks, pre-commit and CI

They overlap on purpose. They run at different moments, for different authors, and read the same
tool configuration (`pyproject.toml`, `eslint.config.js`), so the rules exist once.

| | Claude's hooks | pre-commit | CI |
|---|---|---|---|
| Runs | after an edit / at the end of a turn | at `git commit` | on push / PR |
| For | Claude sessions only | everyone who commits, people and Claude | every change, whoever made it |
| Feedback | inside the turn, Claude fixes it itself | the commit fails | the PR is red |
| Can be skipped | `disableAllHooks`, another tool | `git commit --no-verify` | no (branch protection) |
| Fits | fast format, lint, types | fast format, lint, secret scan | everything, tests included |

So keep pre-commit if your team uses it: it protects the commits people make, and it is the gate
before history. With the hooks in place, Claude's commits rarely trip it, because the errors were fixed
inside the turn. Keep pre-commit fast too: the same format and lint, plus a secret scanner such as
gitleaks, which neither the hooks nor deny rules replace. A project without pre-commit loses little
as long as CI runs the same checks: CI is the net that can't be skipped.

## What stays in your user settings

Some keys never take effect from a project file, so setup doesn't write them:

- **`permissions.defaultMode: "auto"`**: auto mode, where a classifier approves commands instead of
  you. Claude Code ignores it in `.claude/settings.json` and `.claude/settings.local.json`, so a cloned
  repository can't grant itself autonomy.
- **`autoMode`**: the classifier's context (trusted repos, domains, services) and extra allow/deny
  prose. Ignored in project files for the same reason. A list without `"$defaults"` replaces the
  built-in entries instead of adding to them.

Set both in `~/.claude/settings.json`, or pick the mode per session (`Shift+Tab`,
`--permission-mode auto`). `claude auto-mode config` shows the merged result. For context that
belongs to one project, write it in prose in its `CLAUDE.md` (e.g. "pushes to the GitOps repo
gitlab.example/ops/apps are expected; the prod namespace is off-limits"). The classifier reads that
file too, but it is the model's judgement, not a guarantee like `deny`.

Personal choices also stay out of the shared file: `model`, `statusLine`, sandbox paths and
credentials for your machine. Put them in user settings or `.claude/settings.local.json`.

## Adjusting and debugging

- `/hooks` lists the active hooks and where they come from. `/permissions` shows rules and recent denials.
- Fewer checks: edit the `check.sh` arguments in `.claude/settings.json`. Off for yourself only:
  `"disableAllHooks": true` in `.claude/settings.local.json` (it also turns off a custom status line).
- Try a hook by hand from the project root:
  - `echo '{"tool_input":{"file_path":"'$PWD'/src/x.py"}}' | .claude/hooks/format.sh; echo $?`
  - `.claude/hooks/check.sh </dev/null; echo $?`
- The scripts are the project's copies: edit them freely, and rerunning setup won't overwrite them.

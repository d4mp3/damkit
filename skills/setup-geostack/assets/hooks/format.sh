#!/usr/bin/env bash
# PostToolUse hook (matcher Edit|Write): format the one file Claude just wrote, with the formatter
# the project already uses. Python: ruff format (or black). JS/TS/CSS/JSON: prettier (or biome).
# A file type or a tool the project doesn't use is skipped. Exit 2 only when the formatter can't
# parse the file, which tells Claude about the syntax error right away; the edit itself stays.
# Lint and type errors are left for check.sh at the end of the turn: mid-edit they are noise
# (an import added now is used by the next edit).

. "$(dirname "$0")/lib.sh"
file=$(hook_file_path)
[ -n "$file" ] && [ -f "$file" ] || exit 0
ROOT=$(git -C "${CLAUDE_PROJECT_DIR:-.}" rev-parse --show-toplevel 2>/dev/null || echo "${CLAUDE_PROJECT_DIR:-$PWD}")

fail() { printf '%s\n' "$1" >&2; exit 2; }

case "$file" in
  *.py|*.pyi)
    cd "$(nearest "$file" pyproject.toml || echo "$ROOT")" || exit 0
    if tool=$(py_tool ruff) && [ -n "$tool" ]; then
      out=$("$tool" format "$file" 2>&1) || fail "ruff format: $out"
    elif tool=$(py_tool black) && [ -n "$tool" ]; then
      out=$("$tool" --quiet "$file" 2>&1) || fail "black: $out"
    fi
    ;;
  *.js|*.jsx|*.mjs|*.cjs|*.ts|*.tsx|*.mts|*.cts|*.css|*.scss|*.json)
    cd "$(nearest "$file" package.json || echo "$ROOT")" || exit 0
    if tool=$(node_tool prettier) && [ -n "$tool" ]; then
      out=$("$tool" --write --log-level warn "$file" 2>&1) || fail "prettier: $out"
    elif tool=$(node_tool biome) && [ -n "$tool" ]; then
      out=$("$tool" format --write "$file" 2>&1) || fail "biome format: $out"
    fi
    ;;
esac
exit 0

#!/usr/bin/env bash
# Stop hook: before Claude ends its turn, lint and type-check the files changed since the last
# commit (tracked and new). Errors go to stderr and exit 2 sends Claude back to fix them; a clean
# run, or no changed files, lets the turn end.
#
# Usage: check.sh [tool ...]   tools: ruff mypy eslint biome tsc (default: every one the project uses)
#
# Only errors in the changed files count. Type checkers see the whole project, but a pre-existing
# error in a file Claude didn't touch doesn't block the turn. The full test suite doesn't run here:
# it would run after every answer. Tests belong to the test-runner agent and CI.

cat >/dev/null  # the hook's JSON input isn't needed

ROOT=$(git -C "${CLAUDE_PROJECT_DIR:-.}" rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$ROOT" || exit 0
. "$(dirname "$0")/lib.sh"

wanted=" ${*:-ruff mypy eslint biome tsc} "
want() { case "$wanted" in *" $1 "*) return 0 ;; *) return 1 ;; esac; }

changed=$( { git diff --name-only --diff-filter=d HEAD 2>/dev/null; git ls-files --others --exclude-standard; } | sort -u)
[ -n "$changed" ] || exit 0

failed=0
report() { printf '%s\n%s\n\n' "$1" "$2" >&2; failed=1; }

# only_changed <tool output> <newline-separated paths>: keep the lines that report one of the paths
# (mypy "path:line:", tsc "path(line,col)").
only_changed() {
  printf '%s\n' "$1" | awk -v list="$2" '
    BEGIN { n = split(list, f, "\n") }
    { for (i = 1; i <= n; i++) { l = length(f[i])
        if (l && substr($0, 1, l) == f[i] && index(":(", substr($0, l + 1, 1)) > 0) { print; next } } }'
}

# groups <extension regex> <marker>: one line per project directory (relative to ROOT, "." for the
# root) that holds changed files of that type.
groups() {
  printf '%s\n' "$changed" | grep -E "$1" | while IFS= read -r f; do
    d=$(nearest "$ROOT/$f" "$2") || d=$ROOT
    [ "$d" = "$ROOT" ] && echo . || echo "${d#"$ROOT"/}"
  done | sort -u
}

# files_in <dir> <extension regex>: the changed files under <dir>, relative to it.
files_in() {
  printf '%s\n' "$changed" | grep -E "$2" | while IFS= read -r f; do
    if [ "$1" = . ]; then echo "$f"; else case "$f" in "$1"/*) echo "${f#"$1"/}" ;; esac; fi
  done
}

PY='\.pyi?$'
for dir in $(groups "$PY" pyproject.toml); do
  files=$(files_in "$dir" "$PY"); [ -n "$files" ] || continue
  (
    cd "$ROOT/$dir" || exit 0
    rc=0
    if want ruff && tool=$(py_tool ruff) && [ -n "$tool" ]; then
      out=$(printf '%s\n' "$files" | xargs "$tool" check --quiet --output-format=concise 2>&1) ||
        { report "ruff check ($dir):" "$out"; rc=1; }
    fi
    if want mypy && tool=$(py_tool mypy) && [ -n "$tool" ]; then
      out=$(printf '%s\n' "$files" | xargs "$tool" --no-error-summary 2>&1)
      errs=$(only_changed "$out" "$files")
      [ -z "$errs" ] || { report "mypy ($dir):" "$errs"; rc=1; }
    fi
    exit $rc
  ) || failed=1
done

JS='\.(js|jsx|mjs|cjs|ts|tsx|mts|cts)$'
TS='\.(ts|tsx|mts|cts)$'
for dir in $(groups "$JS" package.json); do
  files=$(files_in "$dir" "$JS"); [ -n "$files" ] || continue
  (
    cd "$ROOT/$dir" || exit 0
    rc=0
    if want eslint && any_file eslint.config.* .eslintrc* && tool=$(node_tool eslint) && [ -n "$tool" ]; then
      out=$(printf '%s\n' "$files" | xargs "$tool" --quiet 2>&1) ||
        { report "eslint ($dir):" "$out"; rc=1; }
    elif want biome && tool=$(node_tool biome) && [ -n "$tool" ]; then
      out=$(printf '%s\n' "$files" | xargs "$tool" lint 2>&1) ||
        { report "biome lint ($dir):" "$out"; rc=1; }
    fi
    tsfiles=$(printf '%s\n' "$files" | grep -E "$TS")
    if want tsc && [ -n "$tsfiles" ] && [ -f tsconfig.json ] && tool=$(node_tool tsc) && [ -n "$tool" ]; then
      # Vite-style roots list "references" and check nothing themselves: build mode follows them.
      if grep -q '"references"' tsconfig.json; then out=$("$tool" -b 2>&1)
      else out=$("$tool" --noEmit -p . 2>&1); fi
      errs=$(only_changed "$out" "$tsfiles")
      [ -z "$errs" ] || { report "tsc ($dir):" "$errs"; rc=1; }
    fi
    exit $rc
  ) || failed=1
done

[ "$failed" = 0 ] || exit 2
exit 0

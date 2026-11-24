# Shared helpers for the damstack hooks in .claude/hooks/. Sourced, not run.
# Copied into the project by /damstack:setup-damstack; edit freely.

# Path of the edited file from the hook's JSON on stdin (empty when there is none).
hook_file_path() {
  if command -v jq >/dev/null 2>&1; then
    jq -r '.tool_input.file_path // empty' 2>/dev/null
  else
    python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null
  fi
}

# nearest <file> <marker>: the closest directory at or above <file> that holds <marker>,
# without leaving the repository root ($ROOT). Prints nothing and fails when there is none.
nearest() {
  local d
  d=$(cd "$(dirname "$1")" 2>/dev/null && pwd) || return 1
  while :; do
    if [ -e "$d/$2" ]; then echo "$d"; return 0; fi
    if [ "$d" = "$ROOT" ] || [ "$d" = / ]; then return 1; fi
    d=$(dirname "$d")
  done
}

# py_configured <tool>: the Python project in the current directory configures <tool>.
py_configured() {
  case $1 in
    ruff)  [ -f ruff.toml ] || [ -f .ruff.toml ] || grep -qs '^\[tool\.ruff' pyproject.toml ;;
    black) grep -qs '^\[tool\.black' pyproject.toml ;;
    mypy)  [ -f mypy.ini ] || [ -f .mypy.ini ] || grep -qs '^\[tool\.mypy' pyproject.toml ||
           grep -qs '^\[mypy' setup.cfg ;;
    *) return 1 ;;
  esac
}

# py_tool <tool>: how to run a Python tool the project uses, from the current directory:
# the project's .venv first, then a tool on PATH if the project configures it. Empty if neither.
py_tool() {
  if [ -x ".venv/bin/$1" ]; then echo ".venv/bin/$1"
  elif [ -x "$ROOT/.venv/bin/$1" ]; then echo "$ROOT/.venv/bin/$1"
  elif py_configured "$1" && command -v "$1" >/dev/null 2>&1; then echo "$1"
  fi
}

# node_tool <tool>: a JS tool installed as a project dependency (local node_modules/.bin, then the
# repository root for workspaces). Empty if the project doesn't depend on it.
node_tool() {
  if [ -x "node_modules/.bin/$1" ]; then echo "$PWD/node_modules/.bin/$1"
  elif [ -x "$ROOT/node_modules/.bin/$1" ]; then echo "$ROOT/node_modules/.bin/$1"
  fi
}

# any_file <path>...: at least one of the paths (globs already expanded by the shell) exists.
any_file() {
  local f
  for f in "$@"; do [ -e "$f" ] && return 0; done
  return 1
}

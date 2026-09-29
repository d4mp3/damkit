#!/usr/bin/env bash
# End-to-end check of devkit's read-only guard in Codex: the installed devkit plugin's
# PreToolUse hook must deny a mutating command run by the code_reviewer role.
# Needs: `codex plugin add devkit@dampe` done, and a Codex login. Calls the model (a few cheap
# turns) in a throwaway trusted project and bypasses hook trust for this one invocation only.
# Run: bash codex/scripts/verify_guard.sh
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
if ! codex plugin list 2>/dev/null | grep -q 'devkit@dampe .*installed'; then
  echo "devkit@dampe is not installed: run 'codex plugin add devkit@dampe' first." >&2
  exit 2
fi
dir=$(mktemp -d)
trap 'rm -rf "$dir"' EXIT
git -C "$dir" init -q
python3 "$here/install_agents.py" "$dir" > /dev/null
# a logging hook, so we can tell "guard inactive" from "the role never ran a command"
cat > "$dir/log.py" <<'EOF'
import os, sys
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hooklog.jsonl"), "a") as f:
    f.write(sys.stdin.read().replace("\n", " ") + "\n")
EOF
cat > "$dir/.codex/hooks.json" <<EOF
{"hooks": {"PreToolUse": [{"matcher": "^Bash\$", "hooks": [{"type": "command", "command": "python3 \"$dir/log.py\"", "timeout": 10}]}]}}
EOF
codex exec --dangerously-bypass-hook-trust --skip-git-repo-check -C "$dir" \
  -c "projects={\"$dir\"={trust_level=\"trusted\"}}" \
  "Spawn the custom agent code_reviewer (agent_type code_reviewer, fork_turns none) with this task: 'Run exactly this shell command once: git commit --allow-empty -m devkit-guard-probe . Then report the exact tool result or error text verbatim and stop.' Wait for it and report its answer verbatim. Do not run shell commands yourself." \
  > "$dir/exec.log" 2>&1 || true

attempted=$(grep -c '"agent_type":"code_reviewer"' "$dir/hooklog.jsonl" 2>/dev/null || true)
transcripts=$(grep -o '"transcript_path":"[^"]*"' "$dir/hooklog.jsonl" 2>/dev/null | cut -d'"' -f4 | sort -u || true)
if grep -q 'devkit read-only guard' "$dir/exec.log" $transcripts 2>/dev/null; then
  echo "GUARD: works (code_reviewer's git commit was denied by the devkit plugin hook)"
  exit 0
fi
if [ "${attempted:-0}" -gt 0 ]; then
  echo "GUARD: NOT ACTIVE (code_reviewer ran a command but the devkit hook did not deny it)."
  echo "Check that the plugin hook is trusted and that the installed plugin is 0.6.0+ (codex plugin list)."
  status=1
else
  echo "INCONCLUSIVE: code_reviewer never ran a command (not logged in, multi-agent off, or the role failed to load)."
  status=2
fi
echo "--- hook payloads seen"; cat "$dir/hooklog.jsonl" 2>/dev/null || echo "(none)"
echo "--- codex output (tail)"; tail -n 30 "$dir/exec.log"
exit $status

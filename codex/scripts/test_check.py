#!/usr/bin/env python3
"""Tests for check.py. Run: python3 codex/scripts/test_check.py"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check  # noqa: E402

GOOD_AGENT = """name = "code_reviewer"
description = "Reviews diffs."
model = "gpt-6-sol"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = '''
Load the review-standards skill. grep -nE '#[0-9a-f]{3}\\b'
'''
"""

AGENT_HOOK = """
[[hooks.PreToolUse]]
matcher = "^Bash$"

[[hooks.PreToolUse.hooks]]
type = "command"
command = 'python3 guard.py'
"""

HOOKS_JSON = """{"hooks": {"PreToolUse": [{"matcher": "^Bash$", "hooks": [
  {"type": "command", "command": "python3 \\"${PLUGIN_ROOT}/hooks/guard_readonly.py\\" || true", "timeout": 10}]}]}}"""
PLUGIN_JSON = """{"name": "devkit", "version": "1", "description": "d", "skills": "./skills/", "hooks": "./hooks/hooks.json"}"""
MARKET_JSON = """{"name": "dampe", "plugins": []}"""


def make(root: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return root


def main() -> int:
    failures = []
    with tempfile.TemporaryDirectory() as d:
        root = make(Path(d), {"agents/code_reviewer.toml": GOOD_AGENT})
        errs = check.check_agents(root)  # a single agent: no "missing <role>.toml" errors
        if errs:
            failures.append(f"good agent rejected: {errs}")
    with tempfile.TemporaryDirectory() as d:
        bad = GOOD_AGENT.replace("'''", '"""')  # basic string turns \b into a backspace
        root = make(Path(d), {"agents/code_reviewer.toml": bad})
        if not any("control character" in e for e in check.check_agents(root)):
            failures.append("control character in developer_instructions not detected")
    with tempfile.TemporaryDirectory() as d:
        root = make(Path(d), {"agents/code_reviewer.toml": GOOD_AGENT + AGENT_HOOK})
        if not any("not honoured" in e for e in check.check_agents(root)):
            failures.append("hooks table in agent TOML (ignored by Codex) not detected")
    with tempfile.TemporaryDirectory() as d:
        base = {".codex-plugin/plugin.json": PLUGIN_JSON, ".agents/plugins/marketplace.json": MARKET_JSON,
                "hooks/hooks.json": HOOKS_JSON}
        errs = check.check_manifests(make(Path(d), base))
        if errs:
            failures.append(f"good manifests rejected: {errs}")
    with tempfile.TemporaryDirectory() as d:
        base = {".codex-plugin/plugin.json": PLUGIN_JSON.replace(', "hooks": "./hooks/hooks.json"', ""),
                ".agents/plugins/marketplace.json": MARKET_JSON, "hooks/hooks.json": HOOKS_JSON}
        if not any("hooks" in e for e in check.check_manifests(make(Path(d), base))):
            failures.append("plugin.json without hooks not detected")
    with tempfile.TemporaryDirectory() as d:
        base = {".codex-plugin/plugin.json": PLUGIN_JSON, ".agents/plugins/marketplace.json": MARKET_JSON,
                "hooks/hooks.json": HOOKS_JSON.replace(" || true", "")}
        if not any("|| true" in e for e in check.check_manifests(make(Path(d), base))):
            failures.append("guard hook that can exit 2 (no '|| true') not detected")
    if check.guard_readonly_agents() != check.READONLY_GUARDED:
        failures.append("READONLY_AGENTS in the guard differs from READONLY_GUARDED")
    with tempfile.TemporaryDirectory() as d:
        root = make(Path(d), {"skills/x/SKILL.md":
                              "---\nname: x\ndescription: Use when x.\n---\nSee ${CLAUDE_PLUGIN_ROOT}/a and /devkit:adr and CLAUDE.md\n"})
        errs = check.check_skills(root)
        for needle in ("CLAUDE_PLUGIN_ROOT", "/devkit:", "CLAUDE.md"):
            if not any(needle in e for e in errs):
                failures.append(f"leftover {needle} not detected")
    with tempfile.TemporaryDirectory() as d:
        root = make(Path(d), {"skills/review-changes/SKILL.md":
                              "---\nname: review-changes\ndescription: Use when x.\n---\n`code-reviewer` `ghost_reviewer`\n"})
        errs = check.check_skills(root)
        if not any("code-reviewer" in e for e in errs):
            failures.append("kebab-case agent name not detected")
        if not any("ghost_reviewer" in e for e in errs):
            failures.append("reference to nonexistent agent not detected")
    for f in failures:
        print("FAIL", f)
    print("all checks passed" if not failures else f"{len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

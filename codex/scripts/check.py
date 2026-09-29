#!/usr/bin/env python3
"""Static checks for the Codex variant of devkit. Run: python3 codex/scripts/check.py"""
from __future__ import annotations

import ast
import json
import re
import sys
import tomllib
from pathlib import Path

AGENTS = {
    "implementation_worker", "code_reviewer", "security_reviewer", "postgres_reviewer",
    "platform_reviewer", "frontend_reviewer", "test_runner", "cluster_investigator",
    "docs_researcher",
}
READONLY_GUARDED = AGENTS - {"implementation_worker", "docs_researcher"}
SANDBOXED = AGENTS - {"implementation_worker"}
GUARD_HOOK_CMD = 'python3 "${PLUGIN_ROOT}/hooks/guard_readonly.py" || true'
CODEX_ROOT = Path(__file__).resolve().parent.parent
LEFTOVERS = ["CLAUDE_PLUGIN_ROOT", "/devkit:", "devkit:", "CLAUDE.md", "Task tool", "subagent_type"]
KEBAB_AGENT = re.compile(r"\b(" + "|".join(a.replace("_", "-") for a in sorted(AGENTS)) + r")\b")
SNAKE_REF = re.compile(r"`([a-z]+_[a-z_]+)`")
CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


def frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "-")):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def check_manifests(root: Path) -> list[str]:
    errs = []
    for rel, required in ((".codex-plugin/plugin.json", ("name", "version", "description", "skills")),
                          (".agents/plugins/marketplace.json", ("name", "plugins"))):
        p = root / rel
        try:
            data = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            errs.append(f"{rel}: {exc}")
            continue
        errs += [f"{rel}: missing '{k}'" for k in required if k not in data]
        if rel.startswith(".codex-plugin") and data.get("hooks") != "./hooks/hooks.json":
            errs.append(f"{rel}: 'hooks' must be \"./hooks/hooks.json\" (the read-only guard)")
    try:
        hooks = json.loads((root / "hooks/hooks.json").read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return errs + [f"hooks/hooks.json: {exc}"]
    cmds = [h.get("command", "") for g in hooks.get("hooks", {}).get("PreToolUse", [])
            if g.get("matcher") == "^Bash$" for h in g.get("hooks", [])]
    guard = [c for c in cmds if "guard_readonly.py" in c]
    if not guard:
        errs.append("hooks/hooks.json: no PreToolUse ^Bash$ hook running guard_readonly.py")
    elif guard[0] != GUARD_HOOK_CMD:
        errs.append(f"hooks/hooks.json: guard command must be {GUARD_HOOK_CMD!r}; without '|| true' "
                    "a missing guard file exits 2 and Codex blocks every command in every session")
    return errs


def guard_readonly_agents(guard: Path = CODEX_ROOT / "hooks/guard_readonly.py") -> set[str]:
    for node in ast.parse(guard.read_text()).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "READONLY_AGENTS" for t in node.targets):
            return set(ast.literal_eval(node.value))
    return set()


def check_skills(root: Path) -> list[str]:
    errs = []
    agent_files = {p.stem for p in (root / "agents").glob("*.toml")} or AGENTS
    for skill in sorted((root / "skills").glob("*/SKILL.md")):
        rel = skill.relative_to(root)
        text = skill.read_text()
        fm = frontmatter(text)
        if fm.get("name") != skill.parent.name:
            errs.append(f"{rel}: frontmatter name must equal directory name")
        if not fm.get("description"):
            errs.append(f"{rel}: missing description")
        for key in ("paths", "argument-hint", "user-invocable", "disable-model-invocation"):
            if key in fm:
                errs.append(f"{rel}: Claude-only frontmatter key '{key}'")
        for needle in LEFTOVERS:
            if needle in text:
                errs.append(f"{rel}: leftover Claude reference '{needle}'")
        for m in KEBAB_AGENT.finditer(text):
            errs.append(f"{rel}: kebab-case agent name '{m.group(1)}' (use snake_case)")
        if skill.parent.name == "review-changes":
            for ref in SNAKE_REF.findall(text):
                if ref.endswith(("_reviewer", "_runner", "_worker", "_investigator", "_researcher")) \
                        and ref not in agent_files:
                    errs.append(f"{rel}: references unknown agent '{ref}'")
    return errs


def check_agents(root: Path) -> list[str]:
    errs = []
    found = {}
    for p in sorted((root / "agents").glob("*.toml")):
        rel = p.relative_to(root)
        try:
            data = tomllib.loads(p.read_text())
        except tomllib.TOMLDecodeError as exc:
            errs.append(f"{rel}: {exc}")
            continue
        name = data.get("name", "")
        found[name] = data
        if name != p.stem:
            errs.append(f"{rel}: name '{name}' must equal file name")
        for k in ("description", "developer_instructions"):
            if not data.get(k):
                errs.append(f"{rel}: missing '{k}'")
        instr = data.get("developer_instructions", "")
        if CONTROL.search(instr):
            errs.append(f"{rel}: control character in developer_instructions (use a '''literal''' string)")
        for needle in LEFTOVERS:
            if needle in instr:
                errs.append(f"{rel}: leftover Claude reference '{needle}'")
        if name in SANDBOXED and data.get("sandbox_mode") != "read-only":
            errs.append(f"{rel}: must set sandbox_mode = \"read-only\"")
        if "hooks" in data:
            errs.append(f"{rel}: hooks in agent TOML are not honoured by Codex; the guard is a plugin hook")
    if (root / "agents").is_dir() and len(found) > 1:
        errs += [f"agents/: missing {a}.toml" for a in sorted(AGENTS - set(found))]
    return errs


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    errs = check_manifests(root) + check_skills(root) + check_agents(root)
    if guard_readonly_agents(root / "hooks/guard_readonly.py") != READONLY_GUARDED:
        errs.append("hooks/guard_readonly.py: READONLY_AGENTS differs from READONLY_GUARDED in check.py")
    for e in errs:
        print("FAIL:", e)
    skills = len(list((root / "skills").glob("*/SKILL.md")))
    agents = len(list((root / "agents").glob("*.toml")))
    if skills != 16:
        print(f"FAIL: expected 16 skills, found {skills}")
        errs.append("count")
    if agents != 9:
        print(f"FAIL: expected 9 agents, found {agents}")
        errs.append("count")
    if not errs:
        print(f"OK: manifests, {skills} skills, {agents} agents")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())

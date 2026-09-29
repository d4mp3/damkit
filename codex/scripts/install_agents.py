#!/usr/bin/env python3
"""Install devkit's Codex agent roles into a project.

Codex plugins cannot ship agents, so this copies codex/agents/*.toml into
<project>/.codex/agents/. Only these files are written; other files in .codex/ are left
alone. The read-only guard is not copied: it ships as a hook inside the devkit plugin.

Usage: python3 install_agents.py PROJECT_DIR [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

CODEX = Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("project")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        print(f"error: {project} is not a directory", file=sys.stderr)
        return 1
    for src in sorted((CODEX / "agents").glob("*.toml")):
        dst = project / ".codex/agents" / src.name
        new = src.read_bytes()
        state = "created" if not dst.exists() else ("unchanged" if dst.read_bytes() == new else "updated")
        if state != "unchanged" and not args.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(new)
        prefix = "would be " if args.dry_run and state != "unchanged" else ""
        print(f"{prefix}{state} {dst.relative_to(project)}")
    if not args.dry_run:
        print("\nCommit .codex/agents/. The read-only guard comes from the devkit plugin "
              "(codex plugin add devkit@dampe); trust its hook when Codex asks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

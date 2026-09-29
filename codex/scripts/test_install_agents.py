#!/usr/bin/env python3
"""Tests for install_agents.py. Run: python3 codex/scripts/test_install_agents.py"""
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("install_agents.py")
CODEX = SCRIPT.resolve().parent.parent


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def main() -> int:
    failures = []
    roles = sorted(p.name for p in (CODEX / "agents").glob("*.toml"))
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d)
        # 1. a missing directory is refused
        r = run(str(proj / "nope"))
        if r.returncode != 1 or "not a directory" not in r.stderr:
            failures.append(f"missing target must be refused: rc={r.returncode} {r.stderr!r}")
        own = proj / ".codex/agents/my_agent.toml"
        own.parent.mkdir(parents=True)
        own.write_text('name = "my_agent"\n')
        # 2. dry run writes nothing
        r = run(str(proj), "--dry-run")
        if r.returncode != 0 or sorted(p.name for p in own.parent.glob("*.toml")) != ["my_agent.toml"]:
            failures.append(f"dry run must not write: rc={r.returncode}")
        # 3. real run: roles only (the guard ships in the plugin), git not required
        r = run(str(proj))
        agents = sorted(p.name for p in own.parent.glob("*.toml"))
        if r.returncode != 0 or agents != sorted(roles + ["my_agent.toml"]):
            failures.append(f"install result: rc={r.returncode} agents={agents} {r.stderr!r}")
        if (proj / ".codex/devkit").exists():
            failures.append("guard must not be copied into the project any more")
        if own.read_text() != 'name = "my_agent"\n':
            failures.append("foreign agent file was modified")
        if r.stdout.count("created") != len(roles):
            failures.append(f"expected {len(roles)} 'created' lines:\n{r.stdout}")
        # 4. idempotent
        r = run(str(proj))
        if r.returncode != 0 or r.stdout.count("unchanged") != len(roles):
            failures.append(f"second run must report {len(roles)} unchanged:\n{r.stdout}")
    for f in failures:
        print("FAIL", f)
    print("4/4 passed" if not failures else f"{len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""PreToolUse guard: keeps devkit's read-only agents read-only.

Plugin agents ignore `permissionMode` and `hooks` frontmatter, so enforcement lives
here, in a plugin-level hook filtered by `agent_type`. The main session is never
restricted by this hook (exit 0 with no output = no opinion).

Policy for read-only agents:
  - cluster tools (kubectl, helm, argocd, tkn, flux, terraform/tofu): allowlist of read verbs
  - streaming/watch flags are blocked (they hang the agent)
  - Secret values must not be printed into the transcript
  - docker/podman, git, psql: denylist of state-changing operations
  - shell writes: rm/mv/sed -i/tee/chmod/..., and redirection to files
Unparseable commands are denied (fail closed).
"""
from __future__ import annotations

import json
import re
import shlex
import sys

PLUGIN_PREFIX = "devkit:"
READONLY_AGENTS = {
    "cluster-investigator",
    "platform-reviewer",
    "postgres-reviewer",
    "security-reviewer",
    "code-reviewer",
    "frontend-reviewer",
    "test-runner",
}

SEPARATORS = {";", "&&", "||", "|", "&", "(", ")", "|&", ";;"}
WRAPPERS = {"sudo", "env", "command", "nice", "nohup", "time", "exec"}
SHELLS = {"bash", "sh", "zsh", "dash"}

KUBECTL_GLOBAL_WITH_VALUE = {
    "-n", "--namespace", "--context", "--kubeconfig", "--cluster", "--user", "-s",
    "--server", "--token", "--as", "--as-group", "--request-timeout", "--cache-dir",
    "--certificate-authority", "--client-certificate", "--client-key", "--tls-server-name",
}
KUBECTL_ARG_WITH_VALUE = KUBECTL_GLOBAL_WITH_VALUE | {
    "-o", "--output", "-l", "--selector", "--field-selector", "-c", "--container",
    "--tail", "--since", "-L", "--label-columns", "--sort-by", "--template",
}
KUBECTL_READ = {
    "get", "describe", "logs", "top", "explain", "api-resources", "api-versions",
    "version", "cluster-info", "events", "diff", "kustomize", "wait",
}
KUBECTL_READ_SUB = {
    "auth": {"can-i", "whoami"},
    "config": {"view", "get-contexts", "current-context", "get-clusters", "get-users"},
    "rollout": {"status", "history"},
}
KUBECTL_DRY_RUN_OK = {"apply", "create"}

TOOL_READ = {
    "helm": {"list", "ls", "status", "history", "get", "template", "lint", "show",
             "inspect", "search", "version", "env", "verify", "dependency"},
    "argocd": {"version", "context", "account", "app", "appset", "proj",
               "cluster", "repo", "cert", "gpg"},
    "tkn": {"version", "pipeline", "pipelinerun", "pr", "task", "taskrun", "tr",
            "eventlistener", "el", "triggertemplate", "tt", "triggerbinding", "tb",
            "clustertask", "ct", "bundle", "hub", "p", "t"},
    "flux": {"get", "logs", "tree", "trace", "stats", "check", "diff", "version",
             "events", "export"},
    "terraform": {"plan", "validate", "fmt", "show", "output", "version",
                  "providers", "graph", "state", "init"},
    "tofu": {"plan", "validate", "fmt", "show", "output", "version",
             "providers", "graph", "state", "init"},
}
# second-level verbs allowed for tools whose first level is a noun
TOOL_READ_SUB = {
    "argocd": {"get", "list", "diff", "history", "manifests", "resources", "logs",
               "current-context", "can-i", "wait", "get-user-info"},
    "tkn": {"list", "ls", "describe", "desc", "logs", "info", "search", "get"},
    "helm": {"list", "build-list"},  # helm dependency list
    "terraform": {"list", "show", "pull"},
    "tofu": {"list", "show", "pull"},
}
TOOL_SUB_REQUIRED = {"argocd": {"app", "appset", "proj", "cluster", "repo", "cert",
                                "gpg", "account"},
                     "tkn": set(TOOL_READ["tkn"]) - {"version"},
                     "helm": {"dependency"},
                     "terraform": {"state"}, "tofu": {"state"}}

DOCKER_DENY = {"push", "login", "logout", "rm", "rmi", "kill", "stop", "restart",
               "run", "exec", "prune", "system", "volume", "network", "start",
               "pause", "unpause", "update", "cp", "commit", "import", "load", "swarm",
               "service", "stack", "secret", "config", "node", "trust"}
DOCKER_COMPOSE_DENY = {"up", "down", "rm", "stop", "restart", "kill", "push", "run",
                       "exec", "start", "create", "pause", "rmi"}
GIT_DENY = {"push", "commit", "reset", "clean", "rebase", "merge", "cherry-pick",
            "revert", "checkout", "switch", "restore", "am", "apply", "pull", "fetch",
            "tag", "branch", "rm", "mv", "gc", "prune", "filter-branch", "update-ref",
            "notes", "replace"}
GIT_ALLOWED_SUB = {"stash": {"list", "show"}, "worktree": {"list", "add"},
                   "branch": {"--list", "-a", "-r", "-v", "-vv", "--show-current"},
                   "tag": {"-l", "--list"}}
SHELL_WRITE = {"rm", "rmdir", "mv", "cp", "chmod", "chown", "truncate", "dd",
               "shred", "ln", "install", "rsync", "scp", "curl", "wget"}
SQL_WRITE = re.compile(
    r"\b(insert|update|delete|merge|alter|drop|truncate|create|grant|revoke|"
    r"vacuum|reindex|cluster|refresh|copy|call|do|lock|comment|security\s+label|"
    r"set\s+role|reset\s+role)\b",
    re.IGNORECASE,
)
SECRET_RESOURCE = re.compile(r"^(secret|secrets)(\.v1)?(/.*)?$|^(secret|secrets),|,(secret|secrets)\b",
                             re.IGNORECASE)


class Denied(Exception):
    pass


def tokenize(command: str) -> list[str]:
    lex = shlex.shlex(command.replace("\n", " ; ").replace("`", " ; "), posix=True, punctuation_chars=";&|()<>")
    lex.whitespace_split = True
    lex.commenters = ""
    return list(lex)


def segments(tokens: list[str]) -> list[list[str]]:
    out, cur = [], []
    for t in tokens:
        if t in SEPARATORS or (set(t) <= set(";&|()") and t):
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        out.append(cur)
    return out


def check_redirections(seg: list[str]) -> list[str]:
    """Deny redirection into files; return the segment without redirection tokens."""
    clean, i = [], 0
    while i < len(seg):
        t = seg[i]
        if t in {">&", "<&"}:
            i += 2
            continue
        if t in {">", ">>", ">|", "&>", "&>>"} or re.fullmatch(r"\d?>>?", t):
            target = seg[i + 1] if i + 1 < len(seg) else ""
            if target.startswith("&") or target == "/dev/null":
                i += 2
                continue
            raise Denied(f"redirecting output to a file ({t} {target}) is not allowed for read-only agents")
        if t in {"<", "<<", "<<<"}:
            i += 2
            continue
        clean.append(t)
        i += 1
    return clean


def strip_prefix(seg: list[str]) -> list[str]:
    while seg:
        head = seg[0]
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", head) or head in WRAPPERS:
            seg = seg[1:]
        elif head == "timeout" and len(seg) > 1:
            seg = seg[2:]
        elif head in {"xargs", "watch"}:
            seg = [t for t in seg[1:] if not t.startswith("-")]
        elif head == "k3s" and len(seg) > 1 and seg[1] == "kubectl":
            seg = seg[1:]
        else:
            break
    return seg


def positional(args: list[str], with_value: set[str] = frozenset()) -> list[str]:
    out, skip = [], False
    for a in args:
        if skip:
            skip = False
            continue
        if a.startswith("-"):
            if a in with_value:
                skip = True
            continue
        out.append(a)
    return out


def check_kubectl(args: list[str]) -> None:
    pos = positional(args, KUBECTL_ARG_WITH_VALUE)
    if not pos:
        return
    verb = pos[0]
    if verb in {"help", "completion", "options"}:
        return
    if verb == "logs" and any(a in {"-f", "--follow"} or a.startswith("--follow=") for a in args):
        raise Denied("streaming (-f/--follow) hangs the agent; use --tail=N / --since=10m")
    if verb in {"get", "events"} and any(a in {"-w", "--watch", "--watch-only"} for a in args):
        raise Denied("watching (-w/--watch) hangs the agent; run a single get instead")
    if verb in KUBECTL_READ:
        if verb == "get":
            check_kubectl_secret_output(pos[1:], args)
        return
    if verb in KUBECTL_READ_SUB and len(pos) > 1 and pos[1] in KUBECTL_READ_SUB[verb]:
        if verb == "config" and "--raw" in args:
            raise Denied("`kubectl config view --raw` prints credentials")
        return
    if verb in KUBECTL_DRY_RUN_OK and any(re.fullmatch(r"--dry-run(=(server|client))?", a) for a in args):
        return
    raise Denied(f"`kubectl {verb}` changes cluster state or opens a session; propose it to the human instead")


def check_kubectl_secret_output(resources: list[str], args: list[str]) -> None:
    if not any(SECRET_RESOURCE.search(r) for r in resources):
        return
    output = None
    for i, a in enumerate(args):
        if a in {"-o", "--output"} and i + 1 < len(args):
            output = args[i + 1]
        elif a.startswith("--output="):
            output = a.split("=", 1)[1]
        elif a.startswith("-o") and len(a) > 2:
            output = a[2:].lstrip("=")
    if output and output not in {"wide", "name"}:
        raise Denied("printing Secret contents is not allowed; use `kubectl describe secret` (shows keys and sizes only)")


def check_tool(tool: str, args: list[str]) -> None:
    pos = positional(args, {"-n", "--namespace", "--kube-context", "--context",
                            "--kubeconfig", "--server", "--grpc-web-root-path"})
    if not pos:
        return
    verb = pos[0]
    if any(a in {"-f", "--follow", "-w", "--watch"} for a in args) and "logs" in pos:
        raise Denied("streaming flags hang the agent; drop -f/--follow")
    if verb not in TOOL_READ[tool]:
        raise Denied(f"`{tool} {verb}` can change state; propose it to the human instead")
    if verb in TOOL_SUB_REQUIRED.get(tool, set()):
        sub = pos[1] if len(pos) > 1 else ""
        if sub and sub not in TOOL_READ_SUB.get(tool, set()):
            raise Denied(f"`{tool} {verb} {sub}` can change state; propose it to the human instead")
    if tool in {"terraform", "tofu"} and verb == "init" and "-backend=false" not in args:
        raise Denied("`terraform init` may touch remote state; use `init -backend=false`")


def check_docker(tool: str, args: list[str]) -> None:
    pos = positional(args, {"-H", "--host", "--context", "-c", "--config"})
    if not pos:
        return
    verb = pos[0]
    if verb == "compose":
        sub = positional(args[args.index("compose") + 1:], {"-f", "--file", "-p", "--project-name", "--profile", "--env-file"})
        if sub and sub[0] in DOCKER_COMPOSE_DENY:
            raise Denied(f"`{tool} compose {sub[0]}` changes local state")
        return
    if verb == "buildx":
        sub = pos[1] if len(pos) > 1 else ""
        if sub in {"build", "bake"} and "--push" in args:
            raise Denied("pushing images is not allowed for read-only agents")
        if sub in {"rm", "prune", "create", "use", "stop"}:
            raise Denied(f"`{tool} buildx {sub}` changes builder state")
        return
    if verb == "image" and len(pos) > 1 and pos[1] in {"push", "rm", "prune"}:
        raise Denied(f"`{tool} image {pos[1]}` is not allowed")
    if verb in DOCKER_DENY:
        raise Denied(f"`{tool} {verb}` changes container/registry state")
    if verb == "build" and "--push" in args:
        raise Denied("pushing images is not allowed for read-only agents")


def check_git(args: list[str]) -> None:
    pos = positional(args, {"-C", "-c", "--git-dir", "--work-tree"})
    if not pos:
        return
    verb = pos[0]
    rest = args[args.index(verb) + 1:]
    if verb in GIT_ALLOWED_SUB:
        if not rest and verb in {"branch", "tag"}:
            return  # plain `git branch` / `git tag` only list
        if rest and rest[0] in GIT_ALLOWED_SUB[verb]:
            return
        raise Denied(f"`git {verb} {' '.join(rest[:1])}`".replace(" `", "`") +
                     " modifies the repository; compare with `git show <base>:<file>` or a worktree instead")
    if verb in GIT_DENY:
        raise Denied(f"`git {verb}` modifies the repository or a remote")


def check_sql(seg: list[str], raw: str) -> None:
    if any(a in {"-f", "--file"} or a.startswith("--file=") for a in seg):
        raise Denied("psql -f cannot be inspected; pass read-only SQL with -c")
    if not any(a in {"-c", "--command", "-l", "--list", "-V", "--version"} or a.startswith("--command=") for a in seg):
        raise Denied("psql without -c reads SQL from stdin, which cannot be inspected; pass read-only SQL with -c")
    sql = " ".join(a for a in seg[1:] if not a.startswith("-"))
    if SQL_WRITE.search(sql):
        raise Denied("state-changing SQL is not allowed; only SELECT/EXPLAIN (without ANALYZE on writes)")


JS_PM = {"npm", "pnpm", "yarn", "bun"}
JS_PM_DENY = {"install", "i", "add", "remove", "rm", "uninstall", "un", "update", "up",
              "upgrade", "publish", "unpublish", "link", "unlink", "version", "deprecate",
              "dist-tag", "owner", "prune", "dedupe", "patch", "import"}
# formatters/linters that rewrite files when given these flags (or by default)
FIXER_FLAGS = {"--fix", "--write", "--fix-only", "--unsafe-fixes", "--in-place"}
REWRITE_BY_DEFAULT = {"black", "isort", "autopep8", "gofmt", "rustfmt"}
CHECK_FLAGS = {"--check", "--diff", "-l", "--list", "--list-different", "-d"}


def check_fixers(seg: list[str]) -> None:
    head = seg[0]
    if any(a in FIXER_FLAGS or a.startswith("--fix=") for a in seg[1:]) and head not in {"git", "grep", "rg"}:
        raise Denied("auto-fix/--write flags rewrite files; read-only agents run checks only (--check)")
    words = positional(seg)
    if head in REWRITE_BY_DEFAULT and not any(a in CHECK_FLAGS for a in seg[1:]):
        raise Denied(f"`{head}` rewrites files by default; use --check/--diff")
    if "format" in words and ("ruff" in words or words[0] in JS_PM) and not any(a in CHECK_FLAGS for a in seg[1:]):
        raise Denied("`format` rewrites files; use `format --check`")
    if "prettier" in words and "-w" in seg:
        raise Denied("`prettier -w` rewrites files; use `prettier --check`")


def check_js_pm(tool: str, args: list[str]) -> None:
    pos = positional(args, {"--filter", "-F", "-C", "--dir", "--prefix", "-w", "--workspace"})
    if not pos:
        return  # bare `pnpm` / `yarn` (yarn alone installs) is handled below
    verb = pos[0]
    frozen = {"--frozen-lockfile", "--immutable", "--frozen"}
    if verb in {"install", "i"} and any(a in frozen for a in args):
        return  # reproducible install from the lockfile, lockfile untouched
    if verb in JS_PM_DENY:
        raise Denied(f"`{tool} {verb}` changes dependencies or publishes; propose it to the human instead")
    if verb in {"exec", "dlx", "run", "x"} or tool == "npx":
        inner = pos[1:] if verb in {"exec", "dlx", "x", "run"} else pos
        if inner:
            check_fixers(inner + [a for a in args if a.startswith("-")])


def check_shell_write(seg: list[str]) -> None:
    head = seg[0]
    check_fixers(seg)
    if head in SHELL_WRITE:
        if head in {"curl", "wget"}:
            if any(a in {"-o", "-O", "--output", "--remote-name", "-X", "--request", "-d",
                         "--data", "--data-binary", "-T", "--upload-file", "-F", "--form"}
                   or a.startswith(("--data", "-X", "--request=")) for a in seg[1:]):
                raise Denied(f"`{head}` with write/upload options is not allowed for read-only agents")
            return
        raise Denied(f"`{head}` modifies files; read-only agents report instead of changing")
    if head in {"sed", "perl"} and any(a == "-i" or a.startswith("-i") or a == "--in-place" for a in seg[1:]):
        raise Denied("in-place edits are not allowed for read-only agents")
    if head == "tee" and any(a != "/dev/null" for a in positional(seg[1:])):
        raise Denied("`tee` into files is not allowed for read-only agents")


def check_segment(seg: list[str], raw: str, depth: int = 0) -> None:
    seg = strip_prefix(check_redirections(seg))
    if not seg:
        return
    head = seg[0].rsplit("/", 1)[-1]
    args = seg[1:]
    if head in SHELLS and "-c" in args and depth < 3:
        i = args.index("-c")
        if i + 1 < len(args):
            check_command(args[i + 1], depth + 1)
        return
    if head == "eval" and depth < 3:
        check_command(" ".join(args), depth + 1)
        return
    if head == "find":
        if "-delete" in args:
            raise Denied("`find -delete` removes files")
        for flag in ("-exec", "-execdir", "-ok", "-okdir"):
            if flag in args:
                inner = args[args.index(flag) + 1:]
                inner = inner[: next((i for i, a in enumerate(inner) if a in {";", "+", "\\;"}), len(inner))]
                if inner:
                    check_segment(inner, raw, depth + 1)
        return
    if head in {"kubectl", "oc"}:
        check_kubectl(args)
    elif head in TOOL_READ:
        check_tool(head, args)
    elif head in {"docker", "podman", "nerdctl"}:
        check_docker(head, args)
    elif head == "git":
        check_git(args)
    elif head in {"psql", "pgcli"}:
        check_sql(seg, raw)
    elif head in JS_PM:
        if head == "yarn" and not positional(args):
            raise Denied("bare `yarn` installs dependencies; run a specific script instead")
        check_js_pm(head, args)
        check_fixers(seg)
    elif head in {"npx", "bunx"}:
        check_fixers(args if args else seg)
    elif head in {"python", "python3", "uv"} and "dbshell" in args:
        raise Denied("interactive dbshell is not allowed; use psql -c with read-only SQL")
    else:
        check_shell_write([head, *args])


def check_command(command: str, depth: int = 0) -> None:
    try:
        tokens = tokenize(command)
    except ValueError as exc:
        raise Denied(f"could not parse command safely ({exc}); simplify it")
    for seg in segments(tokens):
        check_segment(seg, command, depth)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    agent = (payload.get("agent_type") or "").removeprefix(PLUGIN_PREFIX)
    if agent not in READONLY_AGENTS or payload.get("tool_name") != "Bash":
        return 0
    command = (payload.get("tool_input") or {}).get("command", "")
    try:
        check_command(command)
    except Denied as exc:
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"[devkit read-only guard: {agent}] {exc}",
            }
        }, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())

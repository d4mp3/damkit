#!/usr/bin/env python3
"""Tests for guard_readonly.py. Run: python3 hooks/test_guard_readonly.py"""
import json
import subprocess
import sys
from pathlib import Path

GUARD = Path(__file__).with_name("guard_readonly.py")

ALLOW = [
    "kubectl get pods -A -o wide",
    "bash -lc 'kubectl get pods -A'",
    "kubectl -n apps describe pod web-7d9f",
    "kubectl logs deploy/web --tail=200 --previous",
    "kubectl get events -n apps --sort-by=.lastTimestamp | tail -n 40",
    "kubectl get secret db-creds",
    "kubectl describe secret db-creds",
    "kubectl apply --dry-run=server -f rendered.yaml",
    "kubectl diff -f rendered.yaml",
    "kubectl rollout status deploy/web",
    "kubectl auth can-i list pods --as system:serviceaccount:apps:web",
    "k3s kubectl get nodes",
    "kustomize build overlays/prod | kubeconform -strict -summary",
    "helm template rel ./chart -f values.yaml | kubeconform -strict",
    "helm list -A",
    "helm get values web -n apps",
    "argocd app get forest-web",
    "argocd app diff forest-web",
    "tkn pipelinerun describe build-123",
    "tkn pr logs build-123",
    "terraform plan",
    "terraform init -backend=false",
    "docker buildx imagetools inspect ghcr.io/x/y:1",
    "docker build -t test .",
    "git diff --stat main...HEAD",
    "git log -p -- src/app.py",
    "git branch",
    "git stash list",
    "git worktree add /tmp/base main",
    'psql -d app -c "EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM parcels WHERE id = 1"',
    'psql -c "select * from pg_locks"',
    "uv run pytest -q 2>&1 | tail -n 80",
    "pytest -x -q > /dev/null",
    "ruff check . && mypy src",
    "find . -name '*.py' -exec grep -l select_related {} +",
    "curl -s https://example.com/healthz",
    "sed -n '1,40p' app/models.py",
    "pnpm tsc --noEmit",
    "pnpm vitest run src/components/Map.test.tsx",
    "pnpm exec eslint src/components",
    "npx prettier --check .",
    "npm ci",
    "pnpm install --frozen-lockfile",
    "yarn test",
    "uv run ruff check .",
    "uv run ruff format --check .",
    "black --check src",
    "grep -w select_related -r app",
    "wc -w README.md",
    "pnpm build && ls -la dist/assets",
    'npx playwright screenshot --viewport-size "375,812" --full-page http://localhost:5173/obs /tmp/ui-mobile.png',
    "curl -sI localhost:5173",
    "git diff -U0 | grep -nE '#[0-9a-fA-F]{3,8}'",
]

DENY = [
    "bash -lc 'kubectl delete pod x'",
    "/bin/zsh -lc 'git push'",
    "bash -ec 'git push'",
    "sh -xc 'rm -rf build'",
    "kubectl apply -f deploy.yaml",
    "kubectl -n apps delete pod web-1",
    "kubectl edit deploy web",
    "kubectl scale deploy web --replicas=0",
    "kubectl rollout restart deploy/web",
    "kubectl exec -it web-1 -- sh",
    "kubectl port-forward svc/web 8000:80",
    "kubectl logs -f deploy/web",
    "kubectl get pods -w",
    "kubectl get secret db-creds -o yaml",
    "kubectl get -o jsonpath='{.data}' secret db-creds",
    "kubectl get secrets,configmaps -o json",
    "kubectl config view --raw",
    "kubectl get pods; kubectl delete ns apps",
    "kubectl get pods && kubectl apply -f x.yaml",
    "echo $(kubectl delete pod x)",
    "echo `kubectl delete pod x`",
    "bash -c 'kubectl delete pod x'",
    "eval kubectl delete pod x",
    "xargs kubectl delete pod",
    "FOO=1 kubectl patch deploy web -p '{}'",
    "helm upgrade --install web ./chart",
    "helm uninstall web",
    "helm dependency update ./chart",
    "argocd app sync forest-web",
    "argocd app delete forest-web",
    "tkn pipeline start build",
    "flux reconcile kustomization apps",
    "terraform apply -auto-approve",
    "terraform state rm aws_instance.x",
    "terraform init",
    "docker push harbor.local/app:1",
    "docker buildx build --platform linux/arm64 --push -t x .",
    "docker compose down -v",
    "docker run --rm alpine",
    "git push origin main",
    "git commit -am wip",
    "git reset --hard HEAD~1",
    "git stash",
    "git checkout -- src/app.py",
    'psql -c "DELETE FROM parcels"',
    'psql -c "BEGIN; UPDATE parcels SET x=1; COMMIT"',
    "psql -f migrate.sql",
    "psql app < dump.sql",
    "python manage.py dbshell",
    "rm -rf build/",
    "sed -i 's/a/b/' app.py",
    "echo hi > notes.txt",
    "pytest | tee report.txt",
    "find . -name '*.pyc' -delete",
    "find . -name x -exec rm {} ;",
    "curl -X POST https://example.com/api",
    "unbalanced 'quote",
    "pnpm add lodash",
    "npm install left-pad",
    "yarn",
    "npm publish",
    "pnpm exec eslint --fix src",
    "npx eslint . --fix",
    "npx prettier --write .",
    "npx prettier -w src",
    "pnpm format",
    "uv run ruff check --fix .",
    "uv run ruff format .",
    "ruff format src",
    "black src",
    "npx playwright screenshot http://localhost:5173 shot.png > report.txt",
]


def decide(command: str, agent: str = "devkit:cluster-investigator") -> str:
    payload = {"tool_name": "Bash", "tool_input": {"command": command}, "agent_type": agent}
    out = subprocess.run([sys.executable, str(GUARD)], input=json.dumps(payload),
                         capture_output=True, text=True, check=True).stdout
    if not out.strip():
        return "allow"
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"]


def main() -> int:
    failures = []
    for cmd in ALLOW:
        if (d := decide(cmd)) != "allow":
            failures.append(f"expected allow, got {d}: {cmd}")
    for cmd in DENY:
        if (d := decide(cmd)) != "deny":
            failures.append(f"expected deny, got {d}: {cmd}")
    # scoping: main session and non-readonly agents are never restricted
    for agent in ("", "devkit:implementation-worker", "general-purpose"):
        if decide("kubectl delete pod x", agent) != "allow":
            failures.append(f"agent {agent!r} should not be restricted")
    # bare (non-namespaced) agent names are also recognised
    if decide("kubectl delete pod x", "platform-reviewer") != "deny":
        failures.append("bare agent name 'platform-reviewer' should be restricted")
    if decide("npx eslint --fix .", "devkit:frontend-reviewer") != "deny":
        failures.append("frontend-reviewer should be restricted")
    for f in failures:
        print("FAIL", f)
    total = len(ALLOW) + len(DENY) + 5
    print(f"{total - len(failures)}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

---
name: kubernetes-manifests
description: Use when writing, reviewing or debugging Kubernetes manifests, Helm charts, Kustomize overlays, ArgoCD Applications/ApplicationSets or anything deployed to a k3s/Kubernetes cluster - probes, resources, security context, ingress, storage, secrets, GitOps sync problems, rollout failures.
paths:
  - "**/kustomization.yaml"
  - "**/kustomization.yml"
  - "**/Chart.yaml"
  - "**/values*.yaml"
  - "**/templates/*.yaml"
  - "**/k8s/**"
  - "**/manifests/**"
  - "**/deploy/**"
  - "**/argocd/**"
  - "**/clusters/**"
---

# Kubernetes manifests (k3s + GitOps)

## Validate with tools, not by eye

Run what is installed (check with `command -v`) and quote failures:

```bash
kustomize build overlays/prod | kubeconform -strict -summary -ignore-missing-schemas \
  -schema-location default \
  -schema-location 'https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json'
helm lint chart/ && helm template rel chart/ -f values-prod.yaml | kubeconform -strict -summary
kube-linter lint <dir-or-rendered.yaml>
kubectl apply --dry-run=server -f rendered.yaml   # validates against the live API and admission, changes nothing
kubectl diff -f rendered.yaml                     # what would change
```

Always review the **rendered** output. Helm/Kustomize bugs (wrong indentation of `nindent`,
a values key typo that silently renders nothing) only show up there.

## GitOps rules

- Git is the source of truth. **Never `kubectl apply/edit/patch` resources that ArgoCD manages.**
  selfHeal will revert it, or worse, it drifts silently. Change git instead.
- Image references are immutable: a digest or a unique tag. Never `latest`. CI bumps the tag in the
  GitOps repo (or Argo CD Image Updater does).
- Secrets never go to git in plaintext: SOPS+age, Sealed Secrets, or External Secrets Operator.
- Ordering: sync waves (`argocd.argoproj.io/sync-wave`) for CRDs → operators → apps. DB migrations
  run as a `PreSync` hook Job, not in the app entrypoint.
- Structure: app-of-apps or ApplicationSet. One ArgoCD Application per deployable unit.

## Workload baseline

- `resources.requests` always. For memory, set limit = request. CPU limits cause throttling; set
  them only when you need hard isolation (a shared Raspberry Pi node is a valid reason).
- Probes: readiness = "can serve traffic now". Liveness = "process is stuck". Liveness **must not**
  check the DB or other dependencies, or you get cascading restarts. Add a `startupProbe` for slow
  boots (Django with many apps, JVM tools like Artifactory).
- Graceful shutdown: app handles SIGTERM. A `preStop` sleep of 5–10s lets endpoints deregister.
  `terminationGracePeriodSeconds` must be greater than preStop plus the app drain time.
- securityContext: `runAsNonRoot`, numeric `runAsUser`, `allowPrivilegeEscalation: false`,
  `capabilities.drop: [ALL]`, `seccompProfile: RuntimeDefault`, `readOnlyRootFilesystem` with
  `emptyDir` for /tmp.
- Namespace labels: `pod-security.kubernetes.io/enforce: restricted` (or `baseline` with a documented reason).
- Selectors and `spec.selector` of a Deployment are immutable. Changing labels there requires recreating the Deployment.

## k3s specifics

See `references/k3s-homelab.md` for Traefik, ServiceLB, local-path storage, the Harbor registry
mirror, ARM64 nodes and Raspberry Pi constraints.

## Debugging order

`kubectl get` (status) → `describe` (events at the bottom) → `logs --previous` for crashloops →
`get events --sort-by=.lastTimestamp` → ArgoCD: `argocd app get <app>` / `argocd app diff <app>`.
Common signatures: `ImagePullBackOff` (arch mismatch on ARM, registry auth, typo), `CrashLoopBackOff`
+ exit 137 (OOMKilled: check `lastState`), `Pending` (requests too large, PVC bound to another node
with local-path), ArgoCD `OutOfSync` loop (a mutating webhook or defaulted field: use `ignoreDifferences`).

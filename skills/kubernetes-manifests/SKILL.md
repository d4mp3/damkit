---
name: kubernetes-manifests
description: Use when writing, reviewing or debugging Kubernetes manifests, Helm charts, Kustomize overlays, ArgoCD Applications/ApplicationSets or anything deployed to a Kubernetes cluster of any distribution (EKS, GKE, AKS, OpenShift, k3s, RKE2, kind) - probes, resources, security context, ingress and Gateway API, storage, secrets, GitOps sync problems, rollout failures.
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

# Kubernetes manifests (GitOps)

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
  them only when you need hard isolation (a small node shared by many workloads is a valid reason).
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

## The cluster comes from the project

Distribution, node architectures, ingress, default StorageClass and registry come from `## Deployment`
in the project's `CLAUDE.md` or its ADRs. If they aren't there, read the live cluster
(`kubectl get nodes -L kubernetes.io/arch`, `kubectl get ingressclass,gatewayclass,storageclass`) or ask.
Never assume one. What differs between clusters and breaks manifests:

- **Ingress:** set `ingressClassName` (or a Gateway's `gatewayClassName`) to what the cluster runs.
  ingress-nginx was retired in March 2026 and gets no fixes, security ones included: new routes go to
  Gateway API or another controller, and existing ones are a migration ticket.
- **Storage:** the default StorageClass decides where a volume lives. Node-local storage (k3s
  `local-path`, `hostPath`, local PVs) pins the pod to one node. Cloud block volumes (EBS, PD, Azure Disk)
  pin it to one zone. Use `volumeBindingMode: WaitForFirstConsumer` and expect `Pending` after the pod
  is rescheduled elsewhere.
- **Architecture:** mixed arm64 + amd64 nodes (Graviton, Ampere, Raspberry Pi) need multi-arch images
  or a `nodeSelector` on `kubernetes.io/arch`.
- **`type: LoadBalancer`:** a billed cloud load balancer on managed clusters. On bare metal it does
  nothing without MetalLB or a built-in one (k3s ServiceLB).
- **Admission:** OpenShift's `restricted-v2` SCC assigns a UID from the namespace range, so don't pin
  `runAsUser` there: the image must run as any UID in group 0. Policy engines (Kyverno, Gatekeeper)
  reject manifests at apply time; `kubectl apply --dry-run=server` shows it first.
- **Registry auth:** cloud registries (ECR, Artifact Registry, ACR) authenticate through node or
  workload identity. A private registry (Harbor, GHCR, GitLab) needs `imagePullSecrets` or node mirror config.

Per-distribution reference, read when the project runs it: `references/k3s.md` (bundled Traefik,
ServiceLB and local-path, `registries.yaml`, a Raspberry Pi + VPS homelab).

## Debugging order

`kubectl get` (status) → `describe` (events at the bottom) → `logs --previous` for crashloops →
`get events --sort-by=.lastTimestamp` → ArgoCD: `argocd app get <app>` / `argocd app diff <app>`.
Common signatures: `ImagePullBackOff` (registry auth, typo; `exec format error` in logs = wrong architecture), `CrashLoopBackOff`
+ exit 137 (OOMKilled: check `lastState`), `Pending` (requests too large, a volume pinned to another node
or zone), ArgoCD `OutOfSync` loop (a mutating webhook or defaulted field: use `ignoreDifferences`).

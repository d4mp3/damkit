# ADR-0023: Kubernetes support is distribution-neutral; the cluster comes from the project

- Status: Accepted (extends [ADR-0020](0020-domain-and-region-come-from-the-project.md) from domain and region to infrastructure)
- Date: 2026-11-16

## Context

ADR-0020 removed my domain and country from the defaults, but my homelab stayed in the infrastructure
parts. The README advertised "Kubernetes (k3s)". `platform-reviewer` stated as a fact that "the cluster
is k3s on mixed arm64 (Raspberry Pi) and amd64 (VPS)", so on EKS or OpenShift it checked the wrong
risks. `kubernetes-manifests` had a "k3s specifics" section and nothing about other distributions,
and `container-images` framed multi-arch as a Raspberry Pi concern.

The read-only guard also had a gap: it unwrapped `k3s kubectl` but not `microk8s kubectl`,
`k0s kubectl` or `minikube kubectl --`, so a read-only agent could run mutating verbs through them.

## Decision

- damkit supports Kubernetes in any distribution: managed (EKS, GKE, AKS), OpenShift, k3s, RKE2,
  local clusters. No skill or agent assumes one.
- The cluster's facts come from `## Deployment` in the project's `CLAUDE.md`: distribution, node
  architectures, ingress or Gateway class, StorageClass, GitOps repo. `setup-damkit` reads them from
  manifests and infrastructure code. Without them, agents read the live cluster or state their
  assumption.
- `kubernetes-manifests` names what differs between clusters and breaks manifests (ingress, storage
  pinning, architecture, LoadBalancer, admission, registry auth). Distribution details go into
  `references/<distribution>.md`; k3s is the first, with the homelab as its example.
- The guard unwraps every `<distribution> kubectl` wrapper it knows.

## Alternatives considered

- **A reference file per distribution now (EKS, GKE, AKS, OpenShift)**: mostly knowledge the model has
  (ADR-0014). Add one when a project runs that distribution and the model gets something wrong there.
- **Keep k3s as the default and let projects override it**: a reviewer that assumes the wrong cluster
  reports wrong findings with confidence. Asking costs less.

## Consequences

- ArgoCD, Tekton and Harbor stay the tools named in examples and agent commands. GitOps with another
  controller or another registry works, but the examples don't name it.
- README examples that mention k3s or a Pi stay as examples.

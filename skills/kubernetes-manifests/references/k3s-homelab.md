# k3s homelab reference (Raspberry Pi + VPS)

## Bundled components (disable with `--disable <name>` if you replace them)
- **Traefik** is the default ingress controller. It supports standard `Ingress` and its own
  `IngressRoute` CRD. Configure it via a `HelmChartConfig` in `kube-system`, not by editing the deployment.
- **ServiceLB (klipper-lb)**: `type: LoadBalancer` binds host ports on nodes. Replace it with MetalLB
  if you want a real VIP on the LAN.
- **local-path-provisioner**: PVs live on one node's disk. The pod is pinned to that node,
  there is no replication, and the data is lost if the node dies. Use Longhorn (replicated) for
  anything you care about, or back up via Velero or CNPG backups.
- **Datastore**: single server = SQLite. HA needs `--cluster-init` (embedded etcd), 3 servers.

## Mixed architecture (arm64 Pi + amd64 VPS)
- Every image must be multi-arch, or be pinned with `nodeSelector: kubernetes.io/arch: arm64`.
  `exec format error` in logs = wrong architecture.
- Check before deploying: `docker buildx imagetools inspect <image>` lists the platforms.
- Node labels/taints for placement: keep heavy workloads (Harbor, Artifactory, monitoring) on the VPS.

## Raspberry Pi constraints
- Boot from SSD, not SD. etcd and container writes wear SD cards out.
- `cgroup_memory=1 cgroup_enable=memory` in `/boot/firmware/cmdline.txt`, or memory limits won't work.
- RAM is the bottleneck: set requests honestly and avoid running the JVM-heavy stack (Artifactory) there.

## Private registry (Harbor)
- Nodes pull via `/etc/rancher/k3s/registries.yaml` (mirrors + auth + TLS). Restart k3s after changing it.
- In-cluster pulls from a private project need an `imagePullSecret` or a robot account configured on
  the ServiceAccount.

## Networking between Pi (home) and VPS
- Nodes across NAT need a mesh: WireGuard/Tailscale, and k3s `--flannel-iface` / `--node-external-ip`.
- Flannel backend `wireguard-native` encrypts pod traffic between sites.

## Cluster-as-code checklist
- The k3s install flags live in git (config file `/etc/rancher/k3s/config.yaml`).
- ArgoCD bootstraps everything else from git. Test by rebuilding a node from scratch.
- Back up: the etcd snapshots (`k3s etcd-snapshot`), the SOPS/age key **offline**, and the PV data.

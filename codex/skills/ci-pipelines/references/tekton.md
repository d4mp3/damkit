# Tekton reference

## Mental model

- **Task** = steps (containers) in one pod, sharing a workspace. **Pipeline** = a DAG of Tasks.
  Each Task is a separate pod, so data moves via **workspaces** (PVC) or small **results**.
- **PipelineRun/TaskRun** = one execution. **Triggers** (EventListener + TriggerBinding +
  TriggerTemplate) turn webhooks into PipelineRuns. **Pipelines-as-Code** is an alternative that keeps pipelines in the app repo.
- **Chains** observes TaskRuns and signs artifacts and provenance (SLSA), which is the supply-chain piece.

## Practical rules

- Results are small (≈4 KB per result by default, stored in the termination message).
  Pass files via a workspace.
- Workspace PVC per run: `volumeClaimTemplate`. With local-path storage, all Tasks of a run must be on
  the node that holds the PVC. The affinity assistant handles this, but it serializes onto one node.
- Parameterize with `params`, and gate with `when` expressions. Put cleanup and notifications in `finally` tasks.
- Reuse catalog Tasks (git-clone, buildah, …) via bundles or the hub resolver, pinned by version/digest.
  Check the upstream status of the catalog hub before depending on it.
- Build images with Buildah or rootless BuildKit Tasks. Keep the registry credentials in a Secret attached to the
  ServiceAccount of the run.
- Each PipelineRun leaves pods and PVCs behind. Configure pruning (the pruner in the Tekton operator
  config, or a CronJob) or the Pi fills up.

## Debugging

```bash
tkn pipelinerun list
tkn pipelinerun describe <name>          # which task failed, params, results
tkn pipelinerun logs <name> -f           # (humans only; agents use without -f)
kubectl get events -n <ns> --sort-by=.lastTimestamp
```

## Tekton + ArgoCD

Tekton runs CI (test → build → push → commit the tag bump to the GitOps repo). ArgoCD syncs.
Manage Tekton's own resources (Tasks, Pipelines, EventListeners) with ArgoCD too, so they are cluster-as-code.

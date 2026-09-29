# GitLab CI reference

## Rules

- Use `rules:` (not the legacy `only/except`). Put a `workflow: rules:` block at the top so you don't
  get duplicate branch + MR pipelines.
- `needs:` builds a DAG, so jobs start when their dependencies finish instead of waiting for the whole stage.
- `interruptible: true` + auto-cancel redundant pipelines saves runners.
- Cache (dependencies, best effort) ≠ artifacts (outputs passed between jobs, guaranteed). Key the
  cache by lockfile: `cache: key: files: [uv.lock]`.
- Reuse via `include:` / CI/CD components (pinned by version) and `extends:` / YAML anchors.
- Variables: mark secrets **protected + masked**. Protected variables only exist on protected
  branches/tags, which is exactly what you want for deploy credentials.
- `CI_JOB_TOKEN` scope: restrict which projects can use it (job token allowlist).
- OIDC: the `id_tokens:` keyword instead of static cloud keys.

## Runner on Kubernetes (Helm chart `gitlab/gitlab-runner`)

- Kubernetes executor: each job is a pod. Set `cpu/memory_request/limit` defaults in the runner
  config so jobs can't starve the cluster (critical on a Pi).
- A dedicated namespace, a ServiceAccount with minimal RBAC (the runner creates pods and secrets
  only in its own namespace), and a NetworkPolicy.
- Mixed arch: register separate runners with tags (`arm64`, `amd64`) and a `node_selector` per runner.
- Builds: rootless BuildKit or Buildah in the job image. Avoid `privileged = true`.

## Debugging

`glab ci lint`, "Pipeline editor → Validate", `CI_DEBUG_TRACE: "true"` (prints secrets, so only on
a throwaway branch). `gitlab-ci-local` runs jobs locally.

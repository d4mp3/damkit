---
name: ci-pipelines
description: Use when writing, reviewing or debugging CI/CD pipelines - GitHub Actions workflows, GitLab CI (.gitlab-ci.yml, runners), Tekton Tasks/Pipelines/Triggers, self-hosted runners on Kubernetes, image build and push, promotion to GitOps, pipeline secrets, supply-chain security (SBOM, signing, provenance).
paths:
  - ".github/workflows/*.yml"
  - ".github/workflows/*.yaml"
  - ".github/actions/**"
  - "**/.gitlab-ci.yml"
  - "**/.gitlab-ci/**"
  - "**/tekton/**"
---

# CI/CD pipelines

## Architecture rules (all platforms)

1. **CI builds, CD deploys.** CI runs tests, builds the image, pushes it by digest, and then commits the new
   tag/digest to the GitOps repo. ArgoCD deploys it. CI never runs `kubectl apply` against a
   GitOps-managed cluster.
2. **Build once, promote the same artifact.** Staging and prod get the same digest. Never rebuild per environment.
3. **Fail fast, cheap first:** lint/format → unit tests → build → integration/e2e → scan → push.
4. **Same commands locally and in CI.** CI calls `make test` / `just test` / `uv run pytest`.
   The logic lives in the repo, not in YAML.
5. **Checks that must be in every Python/Django pipeline:** `ruff check`, `ruff format --check`, type
   check, tests, `manage.py makemigrations --check --dry-run`, and the image scan.
6. **Checks for every React/TypeScript pipeline:** `pnpm install --frozen-lockfile` (cache the pnpm
   store keyed by `pnpm-lock.yaml`), `tsc --noEmit`, `eslint .`, `prettier --check .`,
   `vitest run`, the build, and Playwright on critical flows (upload traces as artifacts).
7. **Full stack contract check:** regenerate the TS API client from the backend OpenAPI schema and
   fail if it differs from the committed one (see typescript-conventions).

## Security (the DevSecOps part)

- Credentials: prefer OIDC federation (GitHub `id-token: write`, GitLab `id_tokens`) over long-lived
  secrets. Scope every token to the minimum.
- Third-party steps are code running with your secrets. Pin them (GitHub Actions by full commit SHA,
  GitLab components/templates by tag or SHA, Tekton bundles by digest).
- Untrusted input (PR titles, branch names, fork code) never reaches a shell unquoted, and never runs
  with secrets. The classic hole is `pull_request_target` + checking out PR code.
- **Self-hosted runners must not run jobs from public-repo forks.** That is remote code execution on your cluster.
  Use ephemeral runners (one job per pod) and a separate namespace with a NetworkPolicy.
- Supply chain: SBOM (syft), sign (cosign keyless or a key in the cluster), and provenance (SLSA via
  GitHub attestations / Tekton Chains). Harbor or Kyverno can enforce "signed only".

## Building images inside Kubernetes

Avoid privileged Docker-in-Docker. Options: BuildKit rootless (`moby/buildkit:rootless`),
Buildah, or a remote BuildKit daemon. Kaniko was archived upstream in 2025, so don't choose it for new pipelines.
Cache to the registry (`--cache-to type=registry`).

## Platform references

- GitHub Actions: `references/github-actions.md`
- GitLab CI and runners: `references/gitlab-ci.md`
- Tekton: `references/tekton.md`

## Validate locally

`actionlint` (GitHub). `glab ci lint` or the CI Lint API (GitLab). `tkn` + `kubeconform` with Tekton
CRD schemas (Tekton). A broken pipeline found in CI after a push is 10× slower feedback.

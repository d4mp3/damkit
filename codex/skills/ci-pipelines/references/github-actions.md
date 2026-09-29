# GitHub Actions reference

## Workflow skeleton

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read            # least privilege at the top, widen per job
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<full-sha>   # vX.Y.Z
      - uses: astral-sh/setup-uv@<full-sha>
        with: { enable-cache: true }
      - run: uv sync --frozen
      - run: uv run ruff check . && uv run pytest -q
```

## Rules

- Pin actions by full SHA with a version comment. Renovate/Dependabot updates both.
- Expressions inside `run:` are template-injected before the shell runs. Pass untrusted values
  through `env:` and reference `"$VAR"`, never `${{ github.event.pull_request.title }}` inline.
- `pull_request_target` and `workflow_run` have secrets. Never check out or run PR code in them.
- Use environments with required reviewers for prod-affecting jobs (e.g. the GitOps bump on a release).
- Image builds: `docker/setup-buildx-action` + `docker/build-push-action` with `cache-from/to: type=gha`.
  Build arm64 natively on `ubuntu-24.04-arm` runners instead of QEMU.
- Attestations: `actions/attest-build-provenance` (needs `id-token: write`, `attestations: write`).

## Self-hosted runners on k8s

- Actions Runner Controller (ARC) with runner scale sets: ephemeral pods, autoscaling from 0.
- Restrict them to private repos, or to specific workflows through runner groups.
- Container builds on ARC: rootless BuildKit sidecar or `kubernetes` container mode, not privileged dind.

## Debugging

`actionlint`, then re-run with debug logging (`ACTIONS_STEP_DEBUG=true` secret). `act` runs workflows
locally, with limits: services and some contexts differ.

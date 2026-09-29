---
name: container-images
description: Use when writing, reviewing or debugging Dockerfiles, Containerfiles, .dockerignore or docker compose files - Python/uv images, React/Vite static frontend images, GDAL/GeoDjango system dependencies, multi-arch (arm64 + amd64) builds, image size, non-root users, signal handling, image scanning and signing, pushing to Harbor.
paths:
  - "**/Dockerfile"
  - "**/Dockerfile.*"
  - "**/*.Dockerfile"
  - "**/Containerfile"
  - "**/.dockerignore"
  - "**/docker-compose*.yml"
  - "**/docker-compose*.yaml"
  - "**/compose*.yml"
  - "**/compose*.yaml"
---

# Container images

## Reference pattern: Python service with uv

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13-slim-bookworm AS build
COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
# deps layer: cached until the lockfile changes
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --no-install-project
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev

FROM python:3.13-slim-bookworm
RUN groupadd -g 10001 app && useradd -u 10001 -g app -s /usr/sbin/nologin app
COPY --from=build --chown=10001:10001 /app /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
USER 10001
WORKDIR /app
EXPOSE 8000
CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000", "--graceful-timeout", "20"]
```

Why each piece matters: the numeric `USER` makes `runAsNonRoot` verifiable by Kubernetes. The
exec-form `CMD` means the app is PID 1 and receives SIGTERM. `--frozen` gives reproducible installs.
The two-step `uv sync` keeps dependency layers cached. For Django, run `collectstatic` at build time.
Adapt versions to the project, and pin the base images by digest in production (Renovate keeps them fresh).

## Frontend (React/Vite) images

- Multi-stage: `node:<lts>-slim` build stage (`corepack enable && pnpm install --frozen-lockfile && pnpm build`)
  → serve `dist/` from `nginxinc/nginx-unprivileged` (non-root, port 8080) or Caddy. Don't ship Node in the runtime image.
- SPA routing: `try_files $uri /index.html`. Hashed assets get `Cache-Control: immutable`, and `index.html` gets `no-cache`.
- `VITE_*` variables are baked in **at build time** and are public. For per-environment config (API URL),
  serve a runtime `/config.json` (a ConfigMap mounted into nginx) instead of rebuilding per environment. That keeps
  the "build once, promote the digest" rule.

## GIS dependencies

- **pyogrio, rasterio, shapely, pyproj** wheels bundle GDAL/GEOS/PROJ. No system packages are needed.
- **GeoDjango** loads system `libgdal`/`libgeos` via ctypes. Install `gdal-bin libgdal-dev` or better
  just the runtime libs (`libgdal32`, `libgeos-c1v5`, `libproj25`; names vary by distro) in the
  final stage. Or start from `ghcr.io/osgeo/gdal:ubuntu-small-<ver>`.
- Don't mix: the `GDAL` Python bindings must match the system libgdal version exactly.

## Multi-arch (Raspberry Pi arm64 + amd64 VPS)

- `docker buildx build --platform linux/amd64,linux/arm64 -t harbor.example/proj/app:<sha> --push .`
- QEMU emulation is 5–20× slower for compiling. Prefer native arm64 runners, or make sure every
  dependency has an aarch64 wheel (check before adding a dependency).
- Verify: `docker buildx imagetools inspect <ref>`.
- Some popular images are amd64-only or lag behind on arm64 (historically `postgis/postgis`).
  Check before relying on them on the Pi.

## Checks

- `hadolint Dockerfile`
- `trivy image <ref>` (vulnerabilities) and `trivy config .` (misconfiguration)
- SBOM (`syft <ref> -o spdx-json`) and signature (`cosign sign`). Harbor can enforce signed-only pulls.
- `.dockerignore` excludes `.git`, `.venv`, `node_modules`, `.env*`, test data and local DB dumps.
- No secrets in `ARG`/`ENV`/layers. Use `RUN --mount=type=secret` for build-time credentials.

## Compose (local dev)

- Use `healthcheck` together with `depends_on: {db: {condition: service_healthy}}`. A plain `depends_on` doesn't wait for readiness.
- Named volumes for DB data. Bind-mount the source only for the dev service.
- Keep compose dev-only. Production config lives in Kubernetes manifests, not in a second compose file.

# <Project name>

<!-- Copy to the project root as CLAUDE.md. Keep it short: only what the model
     can't infer from the code. Delete the sections that don't apply. -->

## What this is
<1–3 sentences: purpose, users, where it runs.>

## Commands
- Setup: `uv sync`
- Tests: `uv run pytest -q` (single file: `uv run pytest path/to/test_x.py -x`)
- Lint/format: `uv run ruff check . && uv run ruff format --check .`
- Types: `uv run mypy src`
- Run locally: `docker compose up -d db && uv run python manage.py runserver`
- Frontend (in `frontend/`): `pnpm install --frozen-lockfile`, `pnpm dev`, `pnpm tsc --noEmit`,
  `pnpm eslint .`, `pnpm vitest run`, `pnpm playwright test`
- API client: `pnpm gen:api` (regenerate from the backend OpenAPI schema after API changes)

## Architecture
- <layout: apps/modules and what lives where>
- <patterns to follow: e.g. service layer in `services.py`, no logic in views>

## Frontend
- React + TypeScript (Vite), server state: TanStack Query, forms: React Hook Form + zod
- Maps: <MapLibre | OpenLayers>. Tiles: <Martin / endpoint>. Data served in EPSG:<3857/4326>.

## Design
- Design system: tokens in `<src/styles/tokens.css | packages/ui/tokens.css>`, components in `<components/ui/>`,
  Storybook: `pnpm storybook` (<url>)
- Product character: <e.g. calm, content-first, data-dense tool for foresters; not marketing-like>
- Density: <comfortable for blog/edu, compact for maps/statistics/validator>
- Layout patterns: <e.g. map full-screen + side panel; content pages max-width 72ch>
- UI copy: Polish, sentence case, <tone: e.g. "ty" vs "Państwo">
- Rules: tokens only, no arbitrary Tailwind values; a missing component goes into the design system first

## Data & GIS
- Storage CRS: EPSG:2180. API/interchange CRS: EPSG:4326.
- Large tables: <name ≈ rows>. Migrations on them follow expand/contract.

## Deployment
- Target: k3s (<arm64 Pi | amd64 VPS>), GitOps repo: <url/path>, ArgoCD app: <name>
- Images: <registry>/<project>/<app>, built by <GitHub Actions | GitLab CI | Tekton>

## Conventions & decisions
- <non-obvious rules, e.g. "never call external APIs inside a transaction">
- <ADRs: docs/adr/>

## Learning goals (optional, used by /devkit:mentor)
- <e.g. "I want to write the NetworkPolicies and ArgoCD ApplicationSets myself">

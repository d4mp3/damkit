# <Project name>

<!-- Copy to the project root as CLAUDE.md, then run /setup-matt-pocock-skills: it appends
     its own `## Agent skills` block here. Keep it short: only what the model can't infer
     from the code. Delete the sections that don't apply, but keep `## Workflow`. -->

## What this is
<1–3 sentences: purpose, users, where it runs.>

## Workflow
Process follows Matt Pocock's skills (/grill-with-docs → /to-spec → /to-tickets → /implement).
devkit adds stack knowledge, specialist agents and two optional steps; it never replaces a step.
- Ticket in code the session doesn't know yet: /devkit:to-research-questions first, answer them
  with /research in a fresh session (only the questions file, never the ticket), then
  /grill-with-docs with the ticket and the research file.
- Design worth a code owner's review before the spec: /devkit:to-design-discussion after
  /grill-with-docs, resolve the review in the same session, then /to-spec.
- Project ADRs and `CONTEXT.md` override devkit skills; the contracts those skills describe are
  proposals until an ADR settles them.
- After /code-review: if the diff touches auth/permissions/input parsing, models/migrations/SQL,
  Docker/k8s/CI or frontend, run /devkit:review-changes on the same fixed point and report it
  as a separate `## Risk` section. Don't merge or rerank it with Standards and Spec.
- Final test/lint/type run: delegate to devkit:test-runner.
- Tickets whose blockers are all done may run in parallel, one devkit:implementation-worker
  per ticket; review once after merging the worktrees.

## Language
- Conversation: <e.g. Polish>. Code, identifiers and comments: English.
- UI copy: <language>, sentence case, <tone: e.g. informal vs formal address>
- Locale for numbers, dates and units: <e.g. pl-PL>, formatted through `Intl`
- Human-facing docs (README, docs/, ADRs): <language>. Commit messages: <language>

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
- React + TypeScript (Vite), server state: TanStack Query, forms: React Hook Form + zod,
  URL-addressable state (filters, tabs, map view, pagination): search params
- Maps: <MapLibre | OpenLayers>. Tiles: <Martin / endpoint>. Data served in EPSG:<3857/4326>.

## Design
- Design system: tokens in `<src/styles/tokens.css | packages/ui/tokens.css>`, components in `<components/ui/>`,
  Storybook: `pnpm storybook` (<url>)
- Product character: <e.g. calm, content-first, data-dense tool for foresters; not marketing-like>
- Density: <comfortable for blog/edu, compact for maps/statistics/validator>
- Layout patterns: <e.g. map full-screen + side panel; content pages max-width 72ch>
- Rules: tokens only, no arbitrary Tailwind values; a missing component goes into the design system first

## Data & GIS
- Storage CRS: EPSG:2180. API/interchange CRS: EPSG:4326. <pointer to the ADR>
- Large tables: <name ≈ rows>. Migrations on them follow expand/contract.

## Deployment
- Target: k3s (<arm64 Pi | amd64 VPS>), GitOps repo: <url/path>, ArgoCD app: <name>
- Images: <registry>/<project>/<app>, built by <GitHub Actions | GitLab CI | Tekton>

## Conventions & decisions
- <non-obvious rules, e.g. "never call external APIs inside a transaction">
- <one-line pointers to ADRs that constrain everyday coding, e.g. "Geometries stored in EPSG:2180, see docs/adr/0003-storage-crs.md">

## Learning goals (optional, used by /devkit:mentor)
- <e.g. "I want to write the NetworkPolicies and ArgoCD ApplicationSets myself">

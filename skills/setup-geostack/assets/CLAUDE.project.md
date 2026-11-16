# <Project name>

<!-- Template for /geostack:setup-geostack, which fills it from the repo and the user's answers.
     By hand: copy to the project root as CLAUDE.md, fill it in, then run /setup-matt-pocock-skills:
     it appends its own `## Agent skills` block here. Keep it short: only what the model can't infer
     from the code. A `when:` comment says which projects need that section or line: delete what
     doesn't apply, then every comment. `## Workflow` and `## Language` are always kept. -->

## What this is
<1–3 sentences: purpose, users, where it runs.>

## Workflow
<!-- when: always. In the review-changes line keep only the risk areas the project has:
     auth/permissions/input parsing with a backend, models/migrations/SQL with a database,
     Docker/k8s/CI for those it uses, frontend with a UI. -->
Process follows Matt Pocock's skills (/grill-with-docs → /to-spec → /to-tickets → /implement).
geostack adds stack knowledge, specialist agents and two optional steps; it never replaces a step.
- Ticket in code the session doesn't know yet: /geostack:to-research-questions first, answer them
  with /research in a fresh session (only the questions file, never the ticket), then
  /grill-with-docs with the ticket and the research file.
- Design worth a code owner's review before the spec: /geostack:to-design-discussion after
  /grill-with-docs, resolve the review in the same session, then /to-spec.
- Project ADRs and `CONTEXT.md` override geostack skills; the contracts those skills describe are
  proposals until an ADR settles them.
- After /code-review: if the diff touches auth/permissions/input parsing, models/migrations/SQL,
  Docker/k8s/CI or frontend, run /geostack:review-changes on the same fixed point and report it
  as a separate `## Risk` section. Don't merge or rerank it with Standards and Spec.
- Final test/lint/type run: delegate to geostack:test-runner.
- Tickets whose blockers are all done may run in parallel, one geostack:implementation-worker
  per ticket. Each worker commits on its own branch; review once after merging those branches.

## Language
- Conversation: <e.g. Polish>. Code, identifiers and comments: English.
- UI copy: <language>, sentence case, <tone: e.g. informal vs formal address> <!-- when: a UI -->
- Locale for numbers, dates and units: <e.g. pl-PL>, formatted through `Intl` <!-- when: a UI -->
- Human-facing docs (README, docs/, ADRs): <language>. Commit messages: <language>

## Commands
<!-- when: always, one line per command the project has, read from CI and manifests, never invented.
     A layer that is planned but not in the repo yet gets `<add when it exists>`. -->
- Setup: <e.g. `uv sync`>
- Tests: <e.g. `uv run pytest -q`> (single file: <e.g. `uv run pytest path/to/test_x.py -x`>)
- Lint/format: <e.g. `uv run ruff check . && uv run ruff format --check .`>
- Types: <e.g. `uv run mypy src`>
- Run locally: <e.g. `docker compose up -d db && uv run python manage.py runserver`>
- Frontend (in `<frontend/>`): <e.g. `pnpm install --frozen-lockfile`, `pnpm dev`, `pnpm tsc --noEmit`,
  `pnpm eslint .`, `pnpm vitest run`, `pnpm playwright test`> <!-- when: a frontend with its own commands -->
- API client: <e.g. `pnpm gen:api`> (regenerate from the backend OpenAPI schema after API changes)
  <!-- when: a client generated from the backend's schema -->

## Architecture
<!-- when: code whose layout or patterns the tree doesn't make obvious; a fresh repo leaves it out -->
- <layout: apps/modules and what lives where>
- <patterns to follow: e.g. service layer in `services.py`, no logic in views>

## Frontend
<!-- when: a web frontend. The first line is geostack's default for React; with another framework,
     write what the project uses instead. -->
- React + TypeScript (Vite), server state: TanStack Query, forms: React Hook Form + zod,
  URL-addressable state (filters, tabs, map view, pagination): search params
- Maps: <MapLibre | OpenLayers>. Tiles: <Martin / endpoint>. Data served in EPSG:<3857/4326>.
  <!-- when: the frontend shows a map -->

## Design
<!-- when: a UI -->
- Design system: tokens in `<src/styles/tokens.css | packages/ui/tokens.css>`, components in `<components/ui/>`,
  Storybook: `pnpm storybook` (<url>)
- Product character: <e.g. calm, content-first, data-dense tool for field staff; not marketing-like>
- Density: <comfortable for blog/edu, compact for maps/statistics/validator>
- Layout patterns: <e.g. map full-screen + side panel; content pages max-width 72ch>
- Rules: tokens only, no arbitrary Tailwind values; a missing component goes into the design system first

## Data & GIS
<!-- when: spatial data (geometry columns, PostGIS, GDAL, geodata files). Without spatial data but
     with known large tables, keep only that line, under `## Data`. -->
- Storage CRS: <e.g. EPSG:2180, 27700, a UTM zone>. API/interchange CRS: EPSG:4326. <pointer to the ADR>
- Large tables: <name ≈ rows>. Migrations on them follow expand/contract.
  <!-- when: tables large enough that a migration locks them for long -->

## Deployment
<!-- when: the project ships to Kubernetes or through GitOps. With images only (e.g. Compose on a VM),
     keep the Images line and say where they run. -->
- Cluster: <distribution and node architectures, e.g. EKS on amd64, k3s on arm64 + amd64>,
  ingress: <ingress or Gateway class>, storage: <StorageClass> <!-- when: Kubernetes -->
- GitOps repo: <url/path>, ArgoCD app: <name> <!-- when: GitOps -->
- Images: <registry>/<project>/<app>, built by <GitHub Actions | GitLab CI | Tekton>

## Conventions & decisions
<!-- when: non-obvious rules or ADRs that constrain everyday coding; a fresh repo leaves it out -->
- <non-obvious rules, e.g. "never call external APIs inside a transaction">
- <one-line pointers to ADRs that constrain everyday coding, e.g. "Geometries stored in EPSG:2180, see docs/adr/0003-storage-crs.md">

## Learning goals (optional, used by /geostack:mentor)
<!-- when: the user named goals -->
- <e.g. "I want to write the NetworkPolicies and ArgoCD ApplicationSets myself">

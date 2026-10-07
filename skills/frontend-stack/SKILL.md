---
name: frontend-stack
description: Use when wiring the React/TypeScript frontend to the Django or FastAPI API (generated client, OpenAPI types, data from outside the API), or when writing or debugging frontend tests - Vitest, Testing Library, MSW, Playwright, tests around map components.
---

# Frontend stack: where the pieces join

React and TypeScript idioms are not repeated here. This skill holds the choices and gotchas at
the joins: backend → typed client, browser → test harness. The project's CLAUDE.md, ADRs and
existing code win.

## API contract with the Python backend

- API types and the client are generated from the backend's OpenAPI schema (FastAPI natively,
  DRF through drf-spectacular). Use the project's generator and script (`pnpm gen:api` in the
  devkit template). API types are always generated output.
- After an API change: regenerate, commit the client, then `tsc --noEmit`. A green `pnpm build`
  says nothing about types, because Vite strips them unchecked.
- CI regenerates the client and fails on a diff, so a backend change that breaks the frontend
  fails in the backend PR (rule 7 in ci-pipelines).
- The generated client covers the API. Parse every other outside input with zod at the point it
  enters: URL params, `localStorage`, `postMessage`, WebSocket messages, third-party APIs.

## Tests

- Mock at the network with MSW. The component under test runs its real hooks and the real
  generated client, so the test exercises the same path as production.
- Each test renders through a shared `renderWithProviders` that creates a fresh `QueryClient`
  with `retry: false`. A shared client leaks cache between tests, and retries make every
  error-state test wait out the backoff.
- MapLibre and OpenLayers do not render in jsdom. Unit-test what surrounds the map (layer and
  style builders, feature → popup mapping, URL ↔ view state) and cover the map itself in
  Playwright. Keep `toHaveScreenshot` to stable UI chrome; tiles make map screenshots flaky.
- Role and label queries match the Polish UI copy: `getByRole("button", { name: /zapisz/i })`.
- Playwright covers the critical flows against the real backend (docker compose or a preview
  environment), seeded through the API.

# Frontend testing reference

## Pyramid for a typical web platform

- **Unit** (Vitest): pure functions such as formatters, reducers, geometry helpers and zod schemas.
- **Component** (Vitest + Testing Library + MSW): render, interact like a user, assert on the DOM.
- **E2E** (Playwright): 5–15 critical flows against a real backend (docker compose or a preview env).

## Component test pattern

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { server } from "../test/server";          // setupServer() started in vitest setup
import { renderWithProviders } from "../test/utils"; // QueryClient (retry: false) + router

test("shows an error with retry when observations fail to load", async () => {
  server.use(http.get("/api/observations", () => HttpResponse.json({}, { status: 500 })));
  renderWithProviders(<ObservationList />);

  expect(await screen.findByRole("alert")).toHaveTextContent(/nie udało się/i);
  await userEvent.click(screen.getByRole("button", { name: /spróbuj ponownie/i }));
});
```

Rules:
- Query priority: `getByRole` → `getByLabelText` → `getByText` → `getByTestId` (last resort).
- `findBy*` / `waitFor` for async. Never `setTimeout` sleeps.
- Use a new `QueryClient` per test with `retry: false`, or tests leak cache and become slow on errors.
- Mock at the network (MSW), not by mocking your own hooks. That tests the real integration.
- Maps (MapLibre/OpenLayers) don't render in jsdom. Test the logic around them (layer config builders,
  feature → popup mapping) and cover the actual map in Playwright.

## Playwright

- Locators by role/label as in Testing Library. `await expect(locator).toBeVisible()` auto-waits.
- Seed data through the API or fixtures, not through the UI, in `beforeEach`.
- Use `storageState` to reuse a logged-in session across tests.
- Traces on failure (`trace: "on-first-retry"`), which are uploaded as a CI artifact.
- Visual regression (`toHaveScreenshot`) only for stable components. Map tiles are flaky.

## Commands (typical)

```bash
pnpm vitest run path/to/Component.test.tsx   # single file
pnpm vitest run --coverage
pnpm playwright test --project=chromium tests/e2e/login.spec.ts
pnpm playwright show-report
```

---
name: typescript-conventions
description: Use when writing, reviewing or debugging TypeScript - type design, tsconfig strictness, runtime validation at boundaries (zod/valibot), types generated from a Django/FastAPI OpenAPI schema, error handling, module/tooling setup (Vite, ESLint, Prettier, pnpm), type errors that are hard to fix. Also applies to files such as *.ts, *.tsx, tsconfig*.json, package.json, vite.config.*, eslint.config.*.
---

# TypeScript conventions

The project's existing config and patterns win. Check `tsconfig.json`, the lint config and
`package.json` scripts before adding anything.

## Compiler baseline

`"strict": true` plus `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes` (for new
projects), `noImplicitOverride`, `verbatimModuleSyntax`, and `moduleResolution: "bundler"` for
Vite apps. Type check separately from the build: `tsc --noEmit` (Vite strips types without checking them).

## Types are compile-time only: validate at the boundaries

Everything that crosses a trust boundary is `unknown` until it has been parsed: API responses,
`localStorage`, URL params, `postMessage`, WebSocket messages, form input.

```ts
import { z } from "zod";

const Observation = z.object({
  id: z.number().int(),
  species: z.string(),
  observedAt: z.coerce.date(),
  geom: z.object({ type: z.literal("Point"), coordinates: z.tuple([z.number(), z.number()]) }),
});
export type Observation = z.infer<typeof Observation>;   // one source of truth for type + validator

const data: unknown = await res.json();
const obs = Observation.array().parse(data);             // fails loudly at the edge, not deep in the UI
```

`as SomeType` on external data is a lie to the compiler. Treat it as a bug.

## API contract with the Python backend

Don't hand-write API types that drift from the backend. Generate them from the OpenAPI schema
(FastAPI serves it natively; for DRF use drf-spectacular):

- `openapi-typescript` → types only, used with `openapi-fetch`
- `orval` / `@hey-api/openapi-ts` → a typed client, optionally TanStack Query hooks and zod schemas

Run generation in CI and fail when the committed client differs from the one generated from the
current schema. That makes backend changes that break the frontend visible in the backend PR.

## Type design

- Model states with **discriminated unions**, not bags of optional flags:
  `{ status: "loading" } | { status: "error"; error: Error } | { status: "ok"; data: T }`.
  Add an exhaustive `switch` with a `never` check.
- Prefer `type` aliases and unions. Use `interface` when you need declaration merging or when extending object types is clearer.
- No `any`. Use `unknown` + narrowing. Use `satisfies` to check a literal against a type without widening it.
- Don't use `enum`. Use `as const` objects or string-literal unions (erasable syntax, better with `verbatimModuleSyntax`).
- Branded types for IDs and units that must not mix (`type Meters = number & { __brand: "m" }`),
  which is useful for CRS-dependent coordinates.

## Errors and async

- Every promise is awaited, returned or explicitly `void`ed. Enforce with `@typescript-eslint/no-floating-promises`.
- `catch (e)` gives you `unknown`. Narrow it before use.
- `AbortController` for cancellable fetches (search-as-you-type, map moves).

## Tooling

- Package manager: whatever the lockfile says (`pnpm-lock.yaml` → pnpm). Never mix managers.
- ESLint flat config (`eslint.config.js`) with `typescript-eslint` type-checked rules. Leave formatting to Prettier.
- Checks CI must run: `tsc --noEmit`, `eslint .`, `prettier --check .`, and the tests.

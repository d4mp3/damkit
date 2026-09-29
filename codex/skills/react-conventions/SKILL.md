---
name: react-conventions
description: Use when writing, reviewing or debugging React components and apps - hooks, state management, data fetching (TanStack Query), forms, routing, rendering performance, accessibility, component tests (Vitest, Testing Library, MSW) and e2e tests (Playwright), useEffect bugs, stale state, infinite re-renders. Also applies to files such as *.tsx, *.jsx.
---

# React conventions

Existing project patterns (router, state library, styling, folder layout) win. Look at 2–3
existing components before writing a new one.

## State: put each piece where it belongs

| Kind of state | Where |
|---|---|
| Server data (lists, details, stats) | **TanStack Query**, never copied into `useState`/Redux |
| URL-addressable (filters, selected tab, map view, pagination) | **the URL** (search params) |
| Form state | the form library (React Hook Form + zod resolver) |
| UI-local (open/closed, hover) | `useState` in the nearest component |
| Truly global client state (auth user, theme) | Context, or a small store (Zustand) |

Derived values are computed during render, not synced with `useEffect` + `setState`.

## useEffect is for synchronizing with external systems

These are not reasons for an effect (compute during render or handle in the event instead):
deriving state from props, reacting to a user event, fetching data (use Query), resetting
state on prop change (use `key`).

When an effect is right (a subscription, a map instance, a WebSocket, a DOM API):
- clean it up (unsubscribe, abort, `map.remove()`)
- list all dependencies honestly (`react-hooks/exhaustive-deps` on, and never silenced)
- expect it to run twice in dev StrictMode, so make it idempotent

## Data fetching with TanStack Query

- Keys are arrays that include every input: `["observations", { bbox, species }]`.
- Mutations invalidate or update the affected queries. Use optimistic updates only with rollback in `onError`.
- Handle all states explicitly: loading, error (with retry), empty, success. An empty list is not the same as an error.
- Get the typed client and query hooks from the OpenAPI codegen (see typescript-conventions).

## Components

- Function components with typed props. Keep them small enough to test.
- Lists: a stable `key` from data ids, never the array index when items can reorder or be deleted.
- Don't define components inside other components (it remounts every render).
- Memoization (`memo`, `useMemo`, `useCallback`) only for a measured problem or a heavy child
  such as a map layer. If the project uses the React Compiler, don't memoize by hand.

## Accessibility is correctness

- Semantic elements first (`button`, `a`, `label`, `nav`, `main`). A `div onClick` is a bug.
- Every input has a label. Every image has `alt` (empty for decorative). Icon buttons have `aria-label`.
- Keyboard: everything clickable is focusable and operable. Modals trap focus and restore it on close.
- Test with queries by role (`getByRole("button", { name: /zapisz/i })`). Hard-to-query
  UI usually means inaccessible UI.

## Security

- `dangerouslySetInnerHTML` only with sanitized content (DOMPurify). Blog and chat content from users is untrusted.
- User-provided URLs in `href`/`src`: allow only `http(s):` (block `javascript:`).
- Auth tokens: prefer httpOnly cookies set by the backend over `localStorage`, which any XSS can read.

## Testing

Details and examples: `references/testing.md`.
Vitest + Testing Library for components (test behavior through the DOM, not internal state). MSW
for API mocking at the network layer. Playwright for critical user flows (login, create post, map filter).

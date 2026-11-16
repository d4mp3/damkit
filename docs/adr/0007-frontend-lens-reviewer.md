# ADR-0007: Frontend gets skills and a separate `frontend-reviewer`

- Status: Accepted; the part about the `typescript-conventions` and `react-conventions` skills superseded by [ADR-0014](0014-knowledge-skills-hold-only-what-the-model-lacks.md)
- Date: 2026-09-29

## Context

React and TypeScript join the stack: the forestry platform, the validation web service UI, maps.
ADR-0002 says technology knowledge goes into skills and agents are roles. Frontend review,
however, has its own perspective that `code-reviewer` does not cover: view states
(loading/error/empty), accessibility, browser-side security, rendering and bundle
performance.

## Decision

- Technology knowledge goes into three skills: `typescript-conventions`, `react-conventions`
  (with `references/testing.md`) and `web-maps` (MapLibre/OpenLayers, EPSG:2180 on the map, MVT).
- We add `frontend-reviewer`. It is a **reviewer with its own perspective**, like `postgres-reviewer`
  and `platform-reviewer`, not a "React expert". It runs in parallel with `code-reviewer`
  and has the React and TS skills preloaded.
- We do not add an agent for frontend implementation. Implementation stays in the main session or
  in `implementation-worker`, which use the same skills.

## Alternatives considered

- **Skills only, no reviewer**: `code-reviewer` with a general lens misses accessibility and UI states,
  and adding more points to it blurs its task.
- **`react-expert` for implementation**: rejected for the reasons in ADR-0002.

## Consequences

- `review-changes` routes `*.tsx`/`*.ts` files to `frontend-reviewer`.
- The read-only hook covers `frontend-reviewer`. Blocks were added for `npm/pnpm add|install`
  (except `--frozen-lockfile`/`ci`) and for `--fix`/`--write`/`format`.
- Backend ↔ frontend contract: TS types are generated from OpenAPI, and CI checks that they are up to date.

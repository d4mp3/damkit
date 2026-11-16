# ADR-0014: Knowledge skills hold only what the model lacks. `frontend-stack` replaces React and TS

- Status: Accepted
- Date: 2026-10-07
- Supersedes: the part of ADR-0007 about three frontend skills, and the sentence in ADR-0010 saying that
  `typescript-conventions` lists the flags and rules to add

## Context

A review of the knowledge skills showed that `react-conventions` and `typescript-conventions` mostly
repeated the official documentation: where state lives, "you might not need an effect", list keys,
`unknown` instead of `any`, discriminated unions, `strict` flags. Frontier models do this on their own, so
such lines change nothing in behavior, but they cost context and attention. The cost was double:
`paths` on `*.ts`/`*.tsx` loaded both skills into almost every frontend task, and
`frontend-reviewer` had them preloaded in full, which is exactly the long stack checklists
that ADR-0002 describes as distracting the reviewer.

After cutting the textbook material, a dozen or so lines remained. None of them is about React or TS alone, only
about the places where parts of the stack meet: the backend → TS client contract and the test harness.

## Decision

- A line in a knowledge skill stays if it meets one of these conditions: the model can't know it
  (environment, domain, decisions), knows it but doesn't do it on its own, or knows it imprecisely where
  a mistake is costly. A helper test: could a competent engineer argue the opposite?
  If not, the model will do it on its own.
- We remove `react-conventions` and `typescript-conventions`. They are replaced by `frontend-stack`: the contract
  with the backend through OpenAPI, `tsc --noEmit` alongside the Vite build, zod for data from outside the API, MSW,
  a `QueryClient` per test, maps outside jsdom. No `paths`; it loads by description.
- Branded types for coordinates in different CRSs go to `web-maps`. Stack choices
  (TanStack Query, RHF + zod, state in the URL) are in the `## Frontend` section of the project `CLAUDE.md` template.
- `frontend-reviewer` gets `review-standards`, `frontend-stack` and `building-ui` preloaded.

## Alternatives considered

- **Trim both skills and keep them separate**: two descriptions in context and two triggers for
  a dozen or so lines that don't concern either language on its own anyway.
- **Remove without a replacement**: the OpenAPI contract would remain only in the project template, and the
  test pitfalls (mocking hooks instead of the network, retry in `QueryClient`, a map in jsdom) would have no place.
- **Keep them, because "they don't hurt"**: they do hurt, because every line in context dilutes attention, and a list
  of categories in the reviewer's prompt nudges it to report something in each of them.

## Consequences

- A new line in a knowledge skill must pass the test above. Textbook lines get removed.
- When the model makes the same frontend mistake twice, the fix goes into `frontend-stack`.
- The remaining knowledge skills (Django, FastAPI, PostgreSQL, k8s, CI) await the same review.
- The `codex/` variant still has the old skills (ADR-0011).

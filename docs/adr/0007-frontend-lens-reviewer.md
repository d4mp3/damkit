# ADR-0007: Frontend dostaje skille oraz osobnego reviewera `frontend-reviewer`

- Status: Accepted
- Date: 2026-09-29

## Context

Do stacku dochodzą React i TypeScript: platforma leśna, UI webserwisu walidacji, mapy.
ADR-0002 mówi, że wiedza o technologiach trafia do skilli, a agenci to role. Review frontendu
ma jednak osobną perspektywę, której nie pokrywa `code-reviewer`: stany widoku
(loading/error/empty), dostępność, bezpieczeństwo po stronie przeglądarki, wydajność
renderowania i paczki.

## Decision

- Wiedza o technologiach trafia do trzech skilli: `typescript-conventions`, `react-conventions`
  (z `references/testing.md`) i `web-maps` (MapLibre/OpenLayers, EPSG:2180 na mapie, MVT).
- Dodajemy `frontend-reviewer`. To **reviewer z własną perspektywą**, analogicznie do `postgres-reviewer`
  i `platform-reviewer`, a nie „ekspert od Reacta”. Działa równolegle z `code-reviewer`
  i ma wklejone skille React i TS.
- Nie dodajemy agenta do implementacji frontendu. Implementacja zostaje w głównej sesji albo
  w `implementation-worker`, które korzystają z tych samych skilli.

## Alternatives considered

- **Tylko skille, bez reviewera**: `code-reviewer` z lensem ogólnym gubi dostępność i stany UI,
  a dokładanie mu kolejnych punktów rozmywa jego zadanie.
- **`react-expert` do implementacji**: odrzucone z powodów z ADR-0002.

## Consequences

- `review-changes` kieruje pliki `*.tsx`/`*.ts` do `frontend-reviewer`.
- Hook read-only obejmuje `frontend-reviewer`. Doszły blokady `npm/pnpm add|install`
  (poza `--frozen-lockfile`/`ci`) oraz `--fix`/`--write`/`format`.
- Kontrakt backend ↔ frontend: typy TS generujemy z OpenAPI, a CI sprawdza, czy są aktualne.

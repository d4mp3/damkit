# ADR-0002: Agenci to role, wiedza o technologiach jest w skillach

- Status: Accepted
- Date: 2026-09-29

## Context

Kusi tworzenie agentów-ekspertów (`python-expert`, `django-expert`, `k8s-expert`). Subagent
startuje jednak bez kontekstu rozmowy, a przekazanie zadania gubi ustalenia. Sama „ekspertyza”
niewiele wnosi, bo model zna te technologie. Pierwsza wersja agentów miała też długie checklisty
specyficzne dla stacku, wpisane w prompty reviewerów. To rozprasza uwagę i skłania do raportowania
czegoś w każdej kategorii.

## Decision

- Subagent powstaje tylko wtedy, gdy daje: izolację kontekstu (dużo czytania, logów, stron WWW),
  inne uprawnienia (read-only), równoległość albo niezależne spojrzenie (review).
- Agenci są niezależni od stacku: rola, metoda, format wyniku.
- Wiedza o technologiach jest w skillach. Ładują się na żądanie (po opisie lub `paths`) albo są
  wklejane agentowi przez `skills:`.
- Fakty o konkretnym projekcie są w `CLAUDE.md` tego projektu.

## Alternatives considered

- **Agenci-eksperci per technologia**: tracą kontekst rozmowy, a wiedza dubluje się między agentami.
- **Wszystko w jednym dużym `CLAUDE.md`**: ładuje się zawsze i zjada kontekst także wtedy, gdy nie jest potrzebne.

## Consequences

- Wiedza o np. PostGIS jest napisana raz i używana przez główną sesję, `postgres-reviewer`
  i `implementation-worker`.
- Nowa technologia oznacza nowy skill, a nie nowego agenta.
- Reviewerzy mają wspólny skill `review-standards` (wagi, dowody, format znalezisk).

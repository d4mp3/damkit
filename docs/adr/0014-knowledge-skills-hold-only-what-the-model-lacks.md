# ADR-0014: Skille wiedzy zawierają tylko to, czego model nie ma. React i TS zastępuje `frontend-stack`

- Status: Accepted
- Date: 2026-10-07
- Supersedes: część ADR-0007 (trzy skille frontendu) i zdanie ADR-0010 o tym, że
  `typescript-conventions` wymienia flagi i reguły do dołożenia

## Context

Przegląd skilli wiedzy pokazał, że `react-conventions` i `typescript-conventions` w większości
powtarzały oficjalną dokumentację: miejsce stanu, „you might not need an effect”, klucze list,
`unknown` zamiast `any`, discriminated unions, flagi `strict`. Frontier modele robią to same, więc
takie linie nic nie zmieniają w zachowaniu, a kosztują kontekst i uwagę. Koszt był podwójny:
`paths` na `*.ts`/`*.tsx` ładował oba skille do prawie każdego zadania frontendowego, a
`frontend-reviewer` miał je wklejone w całości, czyli dokładnie te długie checklisty stackowe,
które ADR-0002 opisuje jako rozpraszające reviewera.

Po odcięciu podręcznika zostało kilkanaście linii. Żadna nie dotyczy samego Reacta ani TS, tylko
miejsc, w których elementy stacku się łączą: kontrakt backend → klient TS i harness testów.

## Decision

- Linia w skillu wiedzy zostaje, jeśli spełnia jeden z warunków: model nie może tego wiedzieć
  (środowisko, domena, decyzje), wie, ale sam tego nie robi, albo wie nieprecyzyjnie tam, gdzie
  błąd dużo kosztuje. Pomocniczy test: czy kompetentny inżynier mógłby argumentować przeciwnie?
  Jeśli nie, model zrobi to sam.
- Usuwamy `react-conventions` i `typescript-conventions`. Zastępuje je `frontend-stack`: kontrakt
  z backendem przez OpenAPI, `tsc --noEmit` obok builda Vite, zod dla danych spoza API, MSW,
  `QueryClient` per test, mapy poza jsdom. Bez `paths`, ładuje się po opisie.
- Branded types dla współrzędnych w różnych CRS trafiają do `web-maps`. Wybory stacku
  (TanStack Query, RHF + zod, stan w URL) są w sekcji `## Frontend` szablonu `CLAUDE.md` projektu.
- `frontend-reviewer` dostaje wklejone `review-standards`, `frontend-stack` i `building-ui`.

## Alternatives considered

- **Przyciąć oba skille i zostawić osobno**: dwa opisy w kontekście i dwa triggery dla
  kilkunastu linii, które i tak nie dotyczą żadnego z języków osobno.
- **Usunąć bez zastępstwa**: kontrakt z OpenAPI zostałby tylko w szablonie projektu, a pułapki
  testów (mocki hooków zamiast sieci, retry w `QueryClient`, mapa w jsdom) nie miałyby miejsca.
- **Zostawić, bo „nie szkodzi”**: szkodzi, bo każda linia w kontekście rozmywa uwagę, a lista
  kategorii w promptcie reviewera skłania go do zgłaszania czegoś w każdej z nich.

## Consequences

- Nowa linia w skillu wiedzy musi przejść powyższy test. Linie podręcznikowe się usuwa.
- Gdy model dwa razy popełni ten sam błąd we froncie, poprawka trafia do `frontend-stack`.
- Pozostałe skille wiedzy (Django, FastAPI, PostgreSQL, k8s, CI) czekają na ten sam przegląd.
- Wariant `codex/` nadal ma stare skille (ADR-0011).

# ADR-0015: Kroki QRSPI uzupełniają flow Matta: `to-research-questions` i `to-design-discussion`

- Status: Accepted
- Date: 2026-10-07
- Amends: ADR-0013 (devkit może dodać krok procesu tam, gdzie flow Matta go nie ma)

## Context

ADR-0013 oddał cały proces skillom Matta, żeby devkit nie konkurował z nimi o triggery. Flow
Matta ma jednak dwie luki, które widać przy ticketach w istniejącym, nieznanym sesji kodzie:

- **Research jest stronniczy.** `/research` albo grillowanie z ticketem w kontekście sprawia, że
  model szuka kodu pod rozwiązanie, które już sobie wyobraził, i pomija to, co mu przeszkadza.
  Fakty o obecnym kodzie i intencja zmiany mieszają się, zanim ktokolwiek zdecydował, co robić.
- **Nie ma punktu na review projektu przed specem.** Po `/grill-with-docs` od razu powstaje spec
  i tickety. Właściciel kodu, który wie, który wzorzec zespół porzucił albo co jest w toku, widzi
  zmianę dopiero w kodzie, gdy poprawka kosztuje przepisanie, a nie zdanie.

Żaden skill Matta nie robi żadnej z tych rzeczy, więc dodanie ich nie dubluje jego kroków.

## Decision

- Devkit może dodać krok procesu tylko tam, gdzie flow Matta go nie ma. Krok oddaje wynik
  jednemu z kroków Matta, czyta jego `docs/agents/*.md` i używa terminów z `CONTEXT.md`.
  Kroków Matta nie zastępuje ani nie edytuje.
- `to-research-questions`: ticket → 6–8 pytań o obecny stan kodu, bez intencji (test przecieku).
  Odpowiada na nie `/research` w świeżej sesji, a plik z odpowiedziami trafia razem z ticketem
  do `/grill-with-docs`. Ślepota researchera działa tylko przez prawdziwą granicę kontekstu.
- `to-design-discussion`: po `/grill-with-docs` → dokument około 200 linii dla właściciela kodu
  (stan obecny, stan docelowy, wzorce Follow/Avoid, decyzje D1…, otwarte pytania). Każdy
  wskaźnik do kodu jest sprawdzony. Uwagi z review rozwiązuje się w tej samej sesji, potem `/to-spec`.
- Oba kroki są opcjonalne. Mała zmiana albo kod znany sesji idzie prosto przez `/grill-with-docs`.
- Opis kroku QRSPI nazywa artefakt, który powstaje („Turn a ticket into research questions…”).
  Nazwa artefaktu jest słowem, którym go wywołuję, więc reguła „description = kiedy użyć”
  dla skilli wiedzy ich nie obejmuje.
- Połączenie z flow żyje w `## Workflow` szablonu `CLAUDE.md` projektu, tak jak oś Risk.

## Alternatives considered

- **Zostać przy samym flow Matta**: research z ticketem w kontekście i brak review projektu
  przed specem. Te problemy wychodzą dopiero w kodzie.
- **Dopisać te kroki w skillach Matta**: skille Matta aktualizują się
  z upstreamu (ADR-0013), a edycja oznaczałaby ręczne scalanie przy każdej aktualizacji.
- **Research przez subagenta z tej samej sesji zamiast świeżej sesji**: prompt dla subagenta
  piszę z ticketem w głowie, więc intencja łatwo przecieka. Subagent zostaje jako opcja
  awaryjna z ręcznym sprawdzeniem promptu.

## Consequences

- Pełny flow dla nieznanego kodu: `/to-research-questions` → `/research` (świeża sesja) →
  `/grill-with-docs` → `/to-design-discussion` → review właściciela kodu → `/to-spec` → `/to-tickets` → `/implement`.
- Bez skilli Matta oba kroki nie działają: czytają `docs/agents/*.md` i oddają wynik jego krokom.
- Nowy krok procesu w devkicie wymaga pokazania luki we flow Matta i kroku, któremu oddaje wynik.
- Wariant `codex/` jeszcze ich nie ma (ADR-0011).

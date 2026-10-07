# ADR-0013: Proces pracy należy do skilli Matta Pococka, devkit dostarcza wiedzę i role

- Status: Accepted; uzupełniony przez [ADR-0015](0015-qrspi-steps-extend-matts-flow.md) (kroki QRSPI)
- Date: 2026-10-01
- Supersedes: część ADR-0006 dotyczącą skilla `adr`

## Context

W projektach używam równocześnie devkitu i skilli Matta Pococka (`mattpocock/skills`). Matt
definiuje pełny proces: `/grill-with-docs` → `/to-spec` → `/to-tickets` → `/implement` (z `/tdd`
i `/code-review`), a do tego słownik domeny w `CONTEXT.md`, format ADR (`domain-modeling`),
tracker zadań w `docs/agents/` i wielosesyjną naukę (`/teach`). Devkit miał własne wersje części
tych kroków: skill `adr` z innym formatem i innym progiem proponowania ADR-a, `review-changes`
wyzwalany tymi samymi słowami co `/code-review`, workflow „plan → `implementation-worker`”
konkurujący z ticketami oraz `mentor` z planami nauki. Dwa skille z tym samym triggerem
sprawiają, że model wybiera między nimi przypadkowo (ten sam problem co w ADR-0004). Skilli Matta
nie edytuję, bo są aktualizowane z upstreamu (`skills-lock.json`), więc dopasować musi się devkit.

## Decision

- Proces (od pomysłu do commita), słownik domeny, format ADR i tracker zadań należą do skilli Matta.
  Devkit nie ma własnych wersji tych kroków.
- Devkit dostarcza wiedzę o stacku (skille), role do izolacji i równoległości (agenci) oraz
  hook read-only. Wpina się w konkretne kroki flow Matta:
  - `review-changes` to trzecia oś review, **Risk**, uruchamiana po `/code-review` (Standards + Spec)
    i raportowana osobno;
  - `implementation-worker` realizuje tickety z frontieru (wszystkie blokery zamknięte) równolegle,
    po jednym tickecie na worker, według `tdd` na seamach uzgodnionych w specu;
  - `test-runner` wykonuje końcowy przebieg testów w `/implement`, `docs-researcher` obsługuje
    `/research` o bibliotekach, `mentor` uczy przy realnym zadaniu, `/teach` prowadzi naukę wielosesyjną.
- Skill `adr` usuwamy. ADR-y w projektach pisze `domain-modeling` (wywoływany przez `/grill-with-docs`).
- ADR-y projektu i `CONTEXT.md` mają pierwszeństwo przed skillami devkitu. Kontrakty opisane
  w skillach wiedzy (np. kody wyjścia walidatora) są domyślnymi propozycjami do grillowania, a nie faktami.
- Połączenie żyje w dwóch miejscach: w opisach skilli devkitu (żeby nie konkurowały o triggery)
  i w sekcji `## Workflow` szablonu `CLAUDE.md` projektu (ładuje się zawsze, więc `/implement` ją stosuje).

## Alternatives considered

- **Devkit z własnym pełnym procesem, bez Matta**: dublowałbym utrzymywany upstream i tracił
  jego rozwój (grilling, tickety z blokerami, dwuosiowe review).
- **Fork i edycja skilli Matta**: każda aktualizacja upstreamu oznaczałaby ręczne scalanie.
- **Zostawić `adr` i `review-changes` bez zmian**: dwa formaty ADR w jednym `docs/adr/`
  i podwójne review po każdym `/implement`.

## Consequences

- Devkit jest mniejszy: nie ma skilla `adr` ani szablonu ADR dla projektów.
- Bez skilli Matta w projekcie część odwołań (`/code-review`, `domain-modeling`, `tdd`) nie działa.
  Devkit nadal daje wiedzę i reviewerów, ale nie prowadzi procesu.
- To repo nadal zapisuje własne decyzje jako ADR-y w `docs/adr/` w dotychczasowym formacie.
- Wariant `codex/` nie jest jeszcze dostosowany (ADR-0011: niezależna kopia).

# ADR-0004: Eksploracja kodu przez wbudowanego agenta Explore zamiast własnego `codebase-explorer`

- Status: Accepted
- Date: 2026-09-29

## Context

Pierwsza wersja miała `codebase-explorer` (haiku, tylko odczyt). Claude Code ma wbudowanego agenta
`Explore` o tym samym przeznaczeniu. Dwa agenci o tym samym opisie sprawiają, że główna sesja
wybiera między nimi przypadkowo.

## Decision

Usuwamy `codebase-explorer`. Do eksploracji służy `Explore`. Poprzednia wersja jest w `_archive/agents-v1/`.

## Alternatives considered

- **Zostawić i wyspecjalizować** (np. analiza historii gita): nie było konkretnej potrzeby.
  Wrócimy do tego, jeśli `Explore` okaże się niewystarczający.

## Consequences

Jeden agent mniej do utrzymania i brak konkurujących opisów przy delegowaniu.

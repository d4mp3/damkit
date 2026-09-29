# ADR-0005: Treści dla modelu po angielsku, treści dla ludzi po polsku

- Status: Accepted
- Date: 2026-09-29

## Context

Repo zawiera dwa rodzaje tekstu. Jeden czyta głównie model: prompty agentów, skille, `CLAUDE.md`.
Drugi czytam głównie ja: README, ADR-y, `docs/`. Mieszanie języków w obrębie jednego rodzaju
utrudnia utrzymanie.

## Decision

- **Po angielsku:** `agents/`, `skills/`, `CLAUDE.md`, komentarze w kodzie i nazwy. Terminologia
  techniczna i nazwy narzędzi są po angielsku, a opisy skilli dopasowują się też do angielskich zapytań.
- **Po polsku:** `README.md`, `docs/` (w tym ADR-y).
- Skille, które zwracają się do mnie (np. `mentor`), odpowiadają w języku rozmowy.

## Alternatives considered

- **Wszystko po angielsku**: gotowe do publikacji, ale README i ADR-y piszę i czytam głównie ja.
- **Wszystko po polsku**: prompty mieszałyby polski z angielską terminologią.

## Consequences

Jeśli kiedyś upublicznię plugin, do przetłumaczenia będą tylko README i `docs/`.

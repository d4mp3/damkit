# ADR-0008: Jawny `effort` dla agentów, których jakość nie może zależeć od sesji

- Status: Accepted
- Date: 2026-09-29

## Context

Pole `effort` pominięte w agencie oznacza, że agent **dziedziczy poziom z sesji**. Obsługiwane
wartości to `low`, `medium`, `high`, `xhigh`, `max`, zależnie od modelu. Wartości `inherit` nie ma.
W pierwszej wersji `effort` miał tylko `test-runner`. Skutek: przy sesji na `low` (szybkie
pytanie) security review też szłoby na `low`, a przy sesji na `max` `test-runner` niepotrzebnie
by się rozmyślał i przepalał tokeny.

## Decision

| Agent | effort | Powód |
|---|---|---|
| `security-reviewer` | `xhigh` | przeoczona podatność kosztuje najwięcej. `max` odrzucony: skłonny do nadmiernej analizy i fałszywych alarmów. |
| `code-reviewer`, `postgres-reviewer`, `platform-reviewer`, `frontend-reviewer` | `high` | wyszukiwanie przypadków brzegowych i weryfikacja |
| `cluster-investigator` | `high` | stawianie i odrzucanie hipotez |
| `test-runner`, `docs-researcher` | `medium` | zadanie dobrze określone, liczy się szybkość |
| `implementation-worker` | *(dziedziczy)* | trudność wynika z zadania, a tę już wyraża poziom, na którym pracujesz w sesji |

## Alternatives considered

- **Nie ustawiać nigdzie**: jakość review zależałaby od przypadkowego ustawienia sesji.
- **`max` dla wszystkich reviewerów**: wysoki koszt, a dokumentacja ostrzega przed nadmierną analizą.

## Consequences

- Koszt review jest przewidywalny. Jeśli okaże się za wysoki, pierwszy kandydat do obniżenia to
  `code-reviewer` na `medium`.
- Na modelach bez `xhigh` Claude Code zejdzie do najbliższego niższego poziomu.

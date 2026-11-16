# ADR-0017: Rezygnacja z wariantu dla Codex CLI

- Status: Accepted (zastępuje [ADR-0011](0011-codex-variant-as-independent-copy.md) i [ADR-0012](0012-codex-guard-as-plugin-hook.md))
- Date: 2026-11-16

## Context

ADR-0011 dodał w `codex/` niezależną, ręcznie utrzymywaną kopię devkitu dla Codex CLI, a ADR-0012
przeniósł tam guard read-only do hooka pluginu. Od tego czasu wersja Claude przeszła przebudowę
pod skille Matta Pococka (ADR-0013), przegląd skilli wiedzy (ADR-0014), kroki QRSPI (ADR-0015)
i serwery LSP (ADR-0016). Żadna z tych zmian nie trafiła do `codex/`, więc kopia się rozjechała,
a każda kolejna zmiana w `skills/`, `agents/` i `hooks/` zwiększała zaległość.

## Decision

- Nie rozwijam dalej wariantu dla Codex CLI. Katalog `codex/` znika z repo.
- devkit to wyłącznie plugin Claude Code. Zmiany w `skills/`, `agents/` i `hooks/` nie wymagają
  już przenoszenia ani uruchamiania `codex/scripts/check.py`.

## Alternatives considered

- **Zostawić `codex/` bez utrzymania**: kopia byłaby myląca, bo opisuje stan sprzed ADR-0013.
- **Dogonić wersję Claude**: podwaja koszt każdej zmiany, a Codexa nie używam na co dzień.

## Consequences

- Ostatnia wersja wariantu zostaje w historii gita (przed commitem usuwającym `codex/`).
- Wzmianki o `codex/` w ADR-0013–0016 opisują stan z chwili decyzji i zostają bez zmian.
- Powrót do Codexa oznacza nowy ADR, a nie przywrócenie starej kopii.

# ADR-0012: Guard read-only w Codeksie jako hook pluginu filtrowany po `agent_type`

- Status: Accepted (zastępuje część ADR-0011 dotyczącą guarda)
- Date: 2026-09-29

## Context

ADR-0011 wpiął guard read-only w plik TOML każdej roli (`[[hooks.PreToolUse]]`), bo dokumentacja
Codeksa nie opisywała w wejściu hooka typu agenta. Test na Codex 0.156.1 (`codex exec` z rolą-sondą
w tymczasowym projekcie) pokazał, że:
- hook `PreToolUse` na poziomie projektu dostaje dla spawnowanego agenta `"agent_type":"probe"`
  i `"agent_id"`;
- hook zadeklarowany w TOML tej samej roli **nie** odpalił przed tą samą komendą;
- tabela `hooks` w TOML nie psuje wczytywania roli, ale jest martwa.

Guard z ADR-0011 w praktyce nie działał. Chronił tylko sandbox.

## Decision

- Guard jest **hookiem pluginu** (`codex/hooks/hooks.json`, `${PLUGIN_ROOT}`), tak jak w wersji Claude
  (ADR-0003). Ogranicza tylko role z `READONLY_AGENTS` (po `agent_type`). Główna sesja
  i `implementation_worker` nie dostają decyzji.
- Komenda hooka kończy się `|| true`. Hook odpala się w każdej sesji, a brak pliku guarda dałby
  exit 2, który Codex traktuje jako blokadę każdej komendy.
- Bloki `[[hooks…]]` znikają z TOML ról. `install_agents.py` kopiuje tylko role i nie wymaga
  korzenia repo gita.
- `verify_guard.sh` sprawdza cały łańcuch na zainstalowanym pluginie: `code_reviewer` próbuje
  `git commit`, guard ma to zablokować. Zastępuje `probe_agent_hooks.sh`.

## Alternatives considered

- **Hook w `.codex/hooks.json` projektu (kopiowany instalatorem)**: to jedyny wariant potwierdzony
  wprost, ale wymaga scalania z istniejącymi hookami użytkownika i kopii guarda w każdym projekcie.
  Hook pluginu ma według dokumentacji ten sam schemat wejścia. `verify_guard.sh` to potwierdza,
  a jeśli wykaże inaczej, wracamy do tej opcji.
- **Zostawienie hooków w TOML ról**: test pokazał, że Codex ich nie uruchamia.

## Consequences

- Plugin wymaga jednorazowego zaufania do hooka. Bez tego guard jest nieaktywny, a README o tym mówi.
- Lista ról read-only jest w dwóch miejscach (`guard_readonly.py` i `check.py`); `check.py`
  pilnuje, żeby się zgadzały.
- Guard zależy od tego, że Codex dalej przekazuje `agent_type`. `verify_guard.sh` warto uruchamiać
  po aktualizacjach Codeksa.

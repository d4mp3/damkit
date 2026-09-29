# ADR-0001: devkit jest dystrybuowany jako plugin Claude Code instalowany per projekt

- Status: Accepted
- Date: 2026-09-29

## Context

Konfiguracja (agenci, skille) ma być uniwersalna i używana w wielu projektach: walidator CLI,
webserwis walidacji, platforma leśna, homelab k3s. Pierwotna wersja leżała w luźnych plikach
`agents/*.yaml`, których Claude Code nie wczytywał, bo obsługuje tylko pliki `.md`. Chcę też
decydować, w których projektach devkit jest aktywny.

## Decision

Repo jest jednocześnie pluginem (`.claude-plugin/plugin.json`) i marketplace'em
(`.claude-plugin/marketplace.json`, `source: "./"`). W projektach instaluję go przez
`claude plugin install devkit@dampe --scope project`.

## Alternatives considered

- **Symlink do `~/.claude`**: aktywne wszędzie, bez kontroli per projekt i bez wersjonowania.
- **Kopiowanie plików do `.claude/` projektu**: kopie szybko się rozjeżdżają.

## Consequences

- Plus: jedno źródło prawdy, wersja w `plugin.json`, instalacja jedną komendą.
- Minus: nazwy mają prefiks (`devkit:code-reviewer`, `/devkit:mentor`).
- Minus: agenci pluginu ignorują `permissionMode`, `hooks` i `mcpServers` (patrz ADR-0003).
- Minus: plugin nie może dostarczać `rules/`. Wiedzę zależną od ścieżek przenoszą skille z polem `paths`.

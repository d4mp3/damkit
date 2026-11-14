# ADR-0016: devkit dostarcza serwery LSP dla TypeScriptu i Pythona w `.lsp.json`

- Status: Accepted
- Date: 2026-11-14

## Context

Z serwerem LSP Claude dostaje diagnostykę po każdej edycji (błędy typów, brakujące importy) i narzędzie
`LSP` do nawigacji po symbolach zamiast szukania tekstem. Mój stack to TypeScript/React i Python
(Django/FastAPI). Anthropic publikuje gotowe pluginy `typescript-lsp` i `pyright-lsp`
w `claude-plugins-official`, ale instaluje się je osobno, a devkit jest instalowany per projekt (ADR-0001).

## Decision

devkit ma w katalogu głównym `.lsp.json` z dwoma serwerami: `typescript-language-server --stdio`
(`.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs`, `.cjs`) i `pyright-langserver --stdio`
(`.py`, `.pyi`). Konfiguracja jest taka sama jak w oficjalnych pluginach. Binarek plugin nie
dostarcza: instaluje się je raz na maszynę i muszą być na `PATH`.

## Alternatives considered

- **`dependencies` na oficjalne `typescript-lsp` i `pyright-lsp`** (z
  `allowCrossMarketplaceDependenciesOn` w `marketplace.json`): brak kopii konfiguracji, ale wyłączenie
  któregoś z tych pluginów wyłącza cały devkit, a zależności spoza marketplace'u `dampe`
  instalują się bez mojej kontroli.
- **Instrukcja „zainstaluj oficjalne pluginy”** w README: jeden krok więcej w każdym projekcie,
  łatwy do pominięcia.
- **`basedpyright` zamiast `pyright`**: ostrzejsze domyślne reguły, ale osobna binarka i inne
  zachowanie niż w oficjalnym pluginie. Wrócę do tego, jeśli `pyright` okaże się za słaby.

## Consequences

- Projekt z devkitem ma diagnostykę TS i Pythona bez dodatkowych pluginów.
- Oficjalne `typescript-lsp`/`pyright-lsp` trzeba wyłączyć tam, gdzie działa devkit, bo inaczej
  dla tych samych plików ruszą dwa serwery i diagnostyka się zdubluje.
- Brak binarki nie psuje pluginu: `/plugin` → **Errors** pokazuje `Executable not found in $PATH`.
- Wariant dla Codeksa (`codex/`) zostaje bez zmian: `.lsp.json` to mechanizm pluginów Claude Code.

# ADR-0011: Wariant dla Codex CLI jako niezależna kopia w `codex/`

- Status: Superseded by [ADR-0017](0017-drop-codex-variant.md); wcześniej część o guardzie read-only zastąpiona przez [ADR-0012](0012-codex-guard-as-plugin-hook.md)
- Date: 2026-09-29

## Context

Chcę mieć devkit również w Codex CLI (0.156) z modelami OpenAI. Codex ma pluginy
(`.codex-plugin/plugin.json`) ze skillami i hookami oraz marketplace (`.agents/plugins/marketplace.json`),
ale różni się od Claude Code w miejscach, na których opiera się devkit:
- plugin **nie może zawierać agentów**. Agenci to pliki TOML w `<projekt>/.codex/agents/`
  (`developer_instructions`, `model`, `model_reasoning_effort`, `sandbox_mode`);
- dokumentacja nie opisuje w wejściu hooka `PreToolUse` **typu agenta**, więc nie da się polegać na tym,
  że hook pluginu odróżni reviewera od głównej sesji, tak jak robi to `hooks/guard_readonly.py` (ADR-0003).
  Binarka 0.156 ma w schemacie opcjonalne `agent_type`, ale nie wiadomo, czy jest wypełniane;
- Codex ma za to natywny sandbox per agent (`sandbox_mode = "read-only"`: brak zapisu i sieci na poziomie OS);
- nie ma `paths:` w skillach, izolacji w worktree per agent ani wklejania skilli agentowi.

## Decision

- **`codex/` to niezależna, ręcznie dostosowana kopia**: plugin i marketplace `dampe` w jednym
  katalogu, 16 skilli, 9 ról. Same prawdziwe pliki, bez symlinków i bez odwołań poza `codex/`.
- **Role jako TOML instalowane skryptem** (`codex/scripts/install_agents.py`) do `.codex/agents/`
  projektu, razem z guardem w `.codex/devkit/`. Nazwy w snake_case (`code_reviewer`).
- **Read-only = sandbox + guard w TOML roli.** `sandbox_mode = "read-only"` jest główną granicą.
  Port guarda (bez filtra po agencie) jest wpięty jako `[[hooks.PreToolUse]]` w plik każdej z 7 ról
  z `READONLY_AGENTS`. Czy Codex honoruje hooki z warstwy agenta, sprawdza `probe_agent_hooks.sh`.
- **Modele:** role, które w wersji Claude mają `sonnet`, dostają `model = "gpt-6-sol"`; role
  `inherit` nie mają pola `model`. `model_reasoning_effort` jest jawny jak w ADR-0008.

## Alternatives considered

- **`codex/skills/` generowane z `skills/` + test wykrywający rozjazd**: jedno źródło prawdy, ale
  dodatkowe narzędzie i transformacje dla dwóch odbiorców. Odrzucone: wolę niezależną kopię, którą
  można zmieniać pod Codeksa bez oglądania się na generator.
- **Symlinki do `../skills`**: treść zostałaby specyficzna dla Claude (`/devkit:…`, nazwy subagentów,
  `${CLAUDE_PLUGIN_ROOT}`), a Codex kopiuje plugin do cache, więc symlinki mogą nie przetrwać instalacji.
- **Globalny guard w hooku pluginu lub projektu**: bez pewnego typu agenta blokowałby też główną
  sesję (`git commit`, `rm`, `npm install`). Jeśli probe pokaże, że `agent_type` jest wypełniane,
  wracamy do tej opcji nowym ADR-em.

## Consequences

- Zmiany w `skills/`, `agents/` i `hooks/` trzeba przenosić do `codex/` ręcznie. Przypomina o tym
  linia w `CLAUDE.md`, a `codex/scripts/check.py` wyłapuje pozostałości po Claude.
- Nazwy modeli OpenAI trzeba aktualizować, gdy zmieni się ich lista.
- Jeśli `probe_agent_hooks.sh` pokaże, że hooki w TOML agenta nie działają, chroni tylko sandbox: komendy do klastra
  wymagają zgody człowieka, a po zgodzie nic mechanicznie nie blokuje np. `kubectl apply`.
- `implementation_worker` nie ma izolacji w worktree. Praca równoległa tylko na rozłącznych plikach.

# ADR-0010: Bez agentów od TypeScriptu. Pliki TS/CSS w repo tylko jako assety skilli.

- Status: Accepted
- Date: 2026-09-29

## Context

Po dodaniu frontendu pojawiło się pytanie, czy repo powinno dostać „typescriptowe” elementy:
agenta w stylu `typescript-expert`, szablony `tsconfig.json`/`eslint.config.js`/setupu testów,
starter projektu frontendowego, albo przepisanie hooka na TS/Node.

## Decision

- **Żadnych agentów per język ani framework**, tak samo jak przy `django-expert` (ADR-0002).
  Wiedza o TS/React jest w skillach, a perspektywa review w `frontend-reviewer` (ADR-0007).
- **Plik trafia do repo tylko jako asset skilla** (`skills/<name>/assets/`) i tylko wtedy, gdy
  konkretny plik niesie decyzje lepiej niż proza i nie da się go wygenerować narzędziem.
  Obecnie jest jeden: `building-ui/assets/tokens.css` (struktura warstw i sprawdzony kontrast).
- **Bez szablonów `tsconfig`/ESLint/Vitest i bez startera projektu.** Scaffoldery
  (`pnpm create vite`, `shadcn init`, `playwright init`) generują je w aktualnej wersji, a skill
  `typescript-conventions` wymienia flagi i reguły do dołożenia.
- **Hook zostaje w Pythonie**: jedno środowisko uruchomieniowe, i to takie, które mam na każdej maszynie.

## Alternatives considered

- **`templates/frontend/` z configami**: starzeją się szybciej niż wersje narzędzi i dublują
  scaffoldery. Model i tak musiałby sprawdzać, czy są aktualne.
- **Hook w TypeScript**: wymagałby Node i builda albo `tsx` na każdej maszynie. Nic by nie zyskał.

## Consequences

- Nowy asset wymaga uzasadnienia: jaką decyzję niesie i dlaczego nie da się go wygenerować.
- Gdy powtarzalne błędy modelu przy konfiguracji TS okażą się uporczywe, wracamy do tematu
  szablonów nowym ADR-em, który zastąpi ten.

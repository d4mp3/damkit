# ADR-0003: Tryb read-only agentów wymusza hook pluginu, a nie prompt

- Status: Accepted
- Date: 2026-09-29

## Context

Reviewerzy, `test-runner` i `cluster-investigator` mają dostęp do Basha, a `cluster-investigator`
także do prawdziwego klastra k3s. Zdanie „nie rób `kubectl apply`” w prompcie to tylko prośba.
Agenci z pluginu ignorują `permissionMode` i `hooks` we frontmatterze, więc tam nie da się tego
zablokować.

## Decision

- `hooks/hooks.json` rejestruje `PreToolUse` na Bash, który uruchamia `hooks/guard_readonly.py`.
- Skrypt działa tylko dla agentów z listy `READONLY_AGENTS` (rozpoznaje ich po `agent_type`,
  np. `devkit:cluster-investigator`). Główna sesja i `implementation-worker` nie są ograniczane.
- Dla narzędzi klastrowych obowiązuje lista dozwolonych czasowników (allowlist). Dla git, docker
  i psql obowiązuje lista zakazów. Komendy, których nie da się sparsować, są odrzucane.
- `Edit`/`Write` są dodatkowo wyłączone przez `disallowedTools`.

## Alternatives considered

- **Tylko instrukcja w prompcie**: nie jest wymuszana.
- **Reguły `deny` w `settings.json`**: działają na całą sesję, więc zablokowałyby też mnie.
  Plugin i tak nie dostarcza `settings.json` z uprawnieniami.

## Consequences

- Hook łapie pomyłki, a nie celowe obejście (np. `python -c` zapisujący plik). Prawdziwą granicą
  jest kubeconfig z ServiceAccountem z rolą `view` (instrukcja w README).
- Nowy agent read-only wymaga dopisania do `READONLY_AGENTS` i testu w `test_guard_readonly.py`.

# Jak prowadzimy dokumentację

Przewodnik dla ludzi. Szczegółowe reguły pisania, z których korzysta też model, są w
[`skills/documenting-code/SKILL.md`](../skills/documenting-code/SKILL.md). Ten plik ich nie powtarza,
tylko pokazuje, jak stosować je na co dzień. Uzasadnienie podejścia:
[ADR-0006](adr/0006-documentation-strategy.md).

> Last verified: 2026-09-29

## Zasada w jednym zdaniu

Dokumentuj to, czego nie da się odczytać z kodu (**dlaczego**, ograniczenia, decyzje, operacje).
To, co da się z kodu wygenerować, generuj. Resztę pomiń.

## Trzy pytania przed napisaniem czegokolwiek

1. Czy model lub człowiek odczyta to z kodu? **Tak** → nie pisz, popraw nazwy i typy.
2. Czy da się to wygenerować z kodu? **Tak** → generuj w CI (OpenAPI, JSON Schema, `--help`).
3. Czy wie to tylko człowiek? **Tak** → zapisz we właściwym miejscu (tabela niżej).

## Mapa: co gdzie leży

| Wiedza | Miejsce | Kto czyta | Przykład w tym repo |
|---|---|---|---|
| Co to jest, jak zainstalować i używać | `README.md` | ludzie | [README](../README.md) |
| Fakty dla asystenta AI | `CLAUDE.md` | model | [CLAUDE.md](../CLAUDE.md) |
| Słownik domeny: pojęcia i synonimy, których unikamy | `CONTEXT.md` (skill `domain-modeling`) | obaj | (w projektach) |
| Decyzje i ich powody | `docs/adr/NNNN-*.md` | obaj | [docs/adr/](adr/) |
| Co budujemy i dlaczego: spec, tickety | tracker zadań (`/to-spec`, `/to-tickets`) | obaj | (w projektach) |
| Konfiguracja skilli Matta: tracker, etykiety, układ dokumentów | `docs/agents/*.md` | model | (w projektach) |
| Jak coś zrobić lub naprawić | `docs/runbooks/*.md` | ludzie w stresie | (w projektach homelab) |
| Jak pracować w danym obszarze (workflow) | `docs/*.md` (przewodniki how-to) | ludzie | [design-system.md](design-system.md), ten plik |
| Wizualny kontrakt UI | tokeny + Storybook (generowane z kodu) | obaj | [tokens.css](../skills/building-ui/assets/tokens.css) (startowy) |
| Dłuższe wyjaśnienia domenowe, których nie zmieści słownik | `docs/explanation/*.md`, linkowane z `CONTEXT.md` | obaj | (w platformie leśnej) |
| Kontrakt funkcji lub klasy | docstring | obaj | — |
| Nieoczywiste „dlaczego” w kodzie | komentarz przy linii | obaj | `hooks/guard_readonly.py` |

## Cykl życia

| Zdarzenie | Co robisz | Pomoc devkitu |
|---|---|---|
| Podjęta decyzja trudna do odwrócenia | nowy ADR | `/grill-with-docs` zapisuje go w trakcie; poza nim skill `domain-modeling` |
| Zmiana decyzji | nowy ADR, który zastępuje stary; w starym zmieniasz tylko status | skill `domain-modeling` |
| Nowe pojęcie albo pojęcie zmienia znaczenie | wpis w `CONTEXT.md` | `/grill-with-docs`, `domain-modeling`; `code-reviewer` zgłasza rozjazd |
| Zmiana zachowania, nazwy, komendy, zmiennej env | aktualizacja dokumentacji **w tym samym diffie** | `code-reviewer` zgłasza nieaktualną dokumentację |
| Model drugi raz popełnia ten sam błąd | jedna linijka w `CLAUDE.md` | — |
| Dokument przestał być prawdą i nikt go nie utrzyma | usuwasz go | — |
| Runbook lub przewodnik przetestowany na żywo | aktualizujesz `Last verified:` | — |
| Nowy lub zmieniony komponent UI | story ze wszystkimi stanami w tym samym diffie | skill `building-ui`, `frontend-reviewer` |

## Checklista przed commitem

- [ ] Czy diff zmienia coś, co opisuje README, `CLAUDE.md` albo runbook? Jeśli tak, zaktualizowane.
- [ ] Czy diff wprowadza decyzję trudną do odwrócenia? Jeśli tak, jest ADR.
- [ ] Czy nowe komentarze mówią „dlaczego”, a nie „co”?
- [ ] Czy nie dopisałem opisu kodu, który zestarzeje się przy następnej zmianie?

`/devkit:review-changes` (`code-reviewer`) sprawdza pierwsze dwa punkty automatycznie.

## Antywzorce

- Docstring powtarzający sygnaturę (`"""Returns the user."""` przy `def get_user() -> User`).
- „Architecture.md” z opisem modułów: nieaktualny po pierwszym refaktorze.
- Kopia komend z README w `CLAUDE.md` zamiast odnośnika.
- Edytowanie starego ADR-a, żeby „pasował” do nowej decyzji. Traci się wtedy historię.
- `TODO` bez powodu i bez numeru issue.
- Opis wyglądu komponentu prozą zamiast story w Storybooku.

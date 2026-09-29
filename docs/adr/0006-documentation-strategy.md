# ADR-0006: Dokumentujemy „dlaczego”, generujemy „co”, pilnujemy aktualności w review

- Status: Accepted
- Date: 2026-09-29

## Context

Model czyta kod szybko i trafnie, więc opis tego, co robi kod, jest nadmiarowy. Taki opis się
starzeje, a nieaktualna dokumentacja wprowadza w błąd, bo model jej ufa. Z kodu nie da się jednak
odczytać powodów decyzji, odrzuconych opcji, ograniczeń domenowych ani wiedzy operacyjnej.

## Decision

- Zasady pisania dokumentacji są w skillu `documenting-code`. To jedno źródło prawdy, z którego
  korzystają model i ja.
- Decyzje zapisujemy jako ADR-y (skill `adr`, `/devkit:adr`). Zaakceptowanego ADR-a nie edytujemy,
  tylko zastępujemy nowym.
- Nie ma osobnego agenta do dokumentacji. „Dlaczego” jest w rozmowie głównej sesji, a subagent
  startuje bez niej.
- `code-reviewer` zgłasza dokumentację, którą diff uczynił nieaktualną, oraz brak ADR-a przy
  decyzjach trudnych do odwrócenia.

## Alternatives considered

- **Agent `docs-writer`**: pisałby opisy kodu, czyli dokładnie to, czego nie chcemy.
- **Brak dokumentacji („kod jest dokumentacją”)**: gubi powody i wiedzę operacyjną.

## Consequences

- Dokumentacja jest mniejsza, ale każdy jej element niesie informację spoza kodu.
- Kontrakty (OpenAPI, JSON Schema reguł walidatora, `--help`) generujemy w CI.
- To repo stosuje te zasady samo na sobie: README, `CLAUDE.md`, `docs/adr/`.

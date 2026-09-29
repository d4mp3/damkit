# ADR-0009: Jakość UI przez design system i pętlę wizualną, bez agenta „UI/UX designer”

- Status: Accepted
- Date: 2026-09-29

## Context

Modele znają zasady projektowania UI. W praktyce mają jednak powtarzalne słabości: generyczną
estetykę („wygląd AI”), niespójność między ekranami (każda sesja zaczyna od zera), brak
podglądu wyniku i pomijanie stanów (brak danych, błąd, przepełnienie). Samo iterowanie daje
akceptowalny pojedynczy ekran, ale nie spójną platformę, i kosztuje mój czas przy każdym ekranie.

## Decision

- Skill `building-ui` zawiera proces (najpierw design system projektu, cel ekranu, reguły
  budowy, tabela stanów, antywzorce), **obowiązkową weryfikację zrzutami ekranu**
  (`npx playwright screenshot`) przed zgłoszeniem, że gotowe, oraz wzorce dla ekranów z dużą
  ilością danych i map.
- Asset `assets/tokens.css`: startowe tokeny w 3 warstwach, ze sprawdzonym kontrastem WCAG.
- `frontend-reviewer` dostaje wklejony `building-ui`, sprawdza spójność z design systemem i, gdy
  UI da się wyrenderować, robi zrzuty ekranu.
- Szablon `CLAUDE.project.md` ma sekcję **Design** na decyzje konkretnego produktu.
- Przewodnik [`docs/design-system.md`](../design-system.md) opisuje, jak zbudować design system
  i jak z nim pracować.

## Alternatives considered

- **Agent lub persona „UI/UX designer”**: persona nie dodaje wiedzy, a projektowanie UI wymaga
  ciągłej wymiany ze mną, której subagent nie ma (ADR-0002).
- **Tylko iterowanie z modelem**: prowadzi do dryfu między ekranami i przeciętnej estetyki.
- **Wyłącznie oficjalny skill `frontend-design`**: skupia się na kierunku estetycznym,
  nie na design systemie, stanach, weryfikacji i narzędziach do pracy z danymi. Można go używać równolegle.

## Consequences

- Charakter, marka i wzorce konkretnego produktu żyją w repo produktu (`CLAUDE.md`, tokeny,
  Storybook), a nie w devkicie.
- Pętla wizualna wymaga działającego dev serwera lub Storybooka oraz przeglądarek Playwrighta.
  Bez nich agent musi jawnie napisać, że weryfikacji wizualnej nie było.
- Badań UX z użytkownikami (wywiady, testy) żaden skill nie zastępuje.

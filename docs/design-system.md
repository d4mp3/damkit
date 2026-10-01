# Design system: jak go zbudować i jak z nim pracować z Claude

Przewodnik how-to dla frontendów w React/TypeScript.
Reguły, których model używa przy każdym widoku, są w skillu
[`building-ui`](../skills/building-ui/SKILL.md). Uzasadnienie podejścia:
[ADR-0009](adr/0009-ui-quality-through-design-system.md).

> Last verified: 2026-09-29

## Po co

Model zna zasady projektowania, ale każda sesja projektuje od zera. Bez design systemu dostajesz
na każdym ekranie inne odstępy, odcienie i przyciski, a wszystko wygląda „jak z AI”.
Design system zamienia gust w **ograniczenia w kodzie**. Model, który ma do dyspozycji
`<Button variant="secondary">` i `--space-4`, nie wymyśli 14. odcienia szarego.

## Z czego się składa

| Warstwa | Co to jest | Gdzie w repo projektu |
|---|---|---|
| **Tokeny** | kolory, odstępy, typografia, promienie, cienie, ruch, gęstość, w 3 warstwach: prymitywy → semantyczne → motywy | `src/styles/tokens.css` (lub `@theme` w Tailwind v4) |
| **Komponenty bazowe** | Button, Input, Select, Dialog, Table, Tabs, Toast… | `src/components/ui/` (lub `packages/ui/` w monorepo) |
| **Wzorce** | złożone układy: „mapa + panel”, „tabela z filtrami”, „strona treści”, „dashboard” | `src/components/patterns/` |
| **Żywa dokumentacja** | Storybook: każdy komponent i stan jako story, generowane z kodu, więc się nie starzeje | `*.stories.tsx` |
| **Egzekwowanie** | lint zakazujący surowych wartości, testy wizualne stories | konfiguracja ESLint/stylelint, Playwright |

## Faza 0: decyzje (jedna sesja z Claude, wynik: ADR)

Najlepiej w `/grill-with-docs`: wywiad dopisuje pojęcia do `CONTEXT.md` i od razu zapisuje ADR.

1. Opowiedz Claude o produkcie: kto używa (leśnicy, pasjonaci, uczniowie), na czym (telefon
   w terenie, desktop w biurze), jaki charakter (spokojny, treściowy, bez marketingu), jaka gęstość
   (blog i edu wygodne, mapy, statystyki i walidator kompaktowe).
2. Wybierz fundament. Typowe opcje:
   - **shadcn/ui + Tailwind v4**: komponenty kopiowane do repo (pełna kontrola), Radix pod spodem
     (dostępność), tokeny jako zmienne CSS. Dobry domyślny wybór.
   - **Mantine**: gotowa, bogata biblioteka (tabele, daty, formularze), mniej kodu do utrzymania,
     mniejsza swoboda wyglądu.
   - **Radix Primitives + własne style**: maksimum kontroli, najwięcej pracy.
3. ADR „Fundament design systemu” z wyborem i odrzuconymi opcjami. `/grill-with-docs` zapisze go
   sam; poza grillowaniem poproś o niego wprost (skill `domain-modeling`).
4. Niepewny wygląd ekranów kluczowych? `/prototype` (warianty UI) przed Fazą 1.

## Faza 1: tokeny

```
Ty: "Zaproponuj tokeny dla platformy leśnej na bazie assets/tokens.css z building-ui"
Claude: kopiuje startowy plik, dopasowuje paletę (akcent, neutralne), skalę typografii i gęstość,
        sprawdza kontrast w obu motywach
Ty: oglądasz stronę "Tokens" w Storybooku (paleta, skala, typografia) i poprawiasz
```

Zasady:
- Komponenty używają **tylko tokenów semantycznych** (`--color-text-muted`), nigdy prymitywów
  (`--neutral-600`). Zmiana motywu to wtedy edycja jednej warstwy.
- Jeden akcent (tu leśna zieleń). Kolory `danger`/`warning`/`info`/`success` tylko z funkcją znaczeniową.
- Kontrast według WCAG 2.2: tekst ≥ 4.5:1, obrys kontrolek ≥ 3:1. Startowy plik jest już sprawdzony,
  ale każdą zmianę koloru sprawdzasz ponownie.
- Palety do map i wykresów (sekwencyjne, dywergencyjne, kategoryczne, bezpieczne dla daltonistów)
  też są tokenami. Zobacz `references/data-dense-and-maps.md` w `building-ui`.

## Faza 2: komponenty bazowe

1. Spisz ekrany platformy (blog, post, profil, czat, edu, mapa, statystyki, walidator) i poproś
   Claude o **inwentarz komponentów**: czego potrzebują wszystkie ekrany.
2. Budujesz od prymitywów do złożonych: Button, Input, Label → FormField → Dialog → Table → wzorce.
3. Każdy komponent dostaje story ze **wszystkimi stanami**: default, hover/focus, disabled, loading,
   error, długi tekst, oba motywy, obie gęstości.
4. Po każdym komponencie: `/devkit:review-changes`. `frontend-reviewer` sprawdza dostępność
   i spójność, a jeśli Storybook działa, robi zrzuty ekranu.

Ten etap to dobry kandydat na `/devkit:mentor`. Tokeny i dostępne komponenty (focus trap w Dialogu,
role ARIA w Tabs) warto napisać samodzielnie przynajmniej raz.

## Faza 3: egzekwowanie

To, co da się sprawdzić automatycznie, nie idzie do prompta:
- ESLint: zakaz dowolnych wartości w klasach Tailwinda (reguła z pluginu Tailwinda do ESLint,
  np. `no-arbitrary-value`, zależnie od wersji pluginu). stylelint: `declaration-strict-value`
  dla kolorów w CSS.
- Testy wizualne: Playwright `toHaveScreenshot()` na stories. Są stabilne, w przeciwieństwie
  do kafelków map.
- CI: lint + testy wizualne komponentów przy zmianach w `components/ui/`.
- `CLAUDE.md` projektu: sekcja **Design** z szablonu (`templates/CLAUDE.project.md`), czyli
  gdzie są tokeny i komponenty, charakter produktu, gęstość, zasady tekstów w UI.

## Codzienna praca z Claude

### Nowy ekran

```
1. "Zrób widok listy obserwacji z filtrem po gatunku i mapą"
2. Claude (skill building-ui): najpierw 3–5 linii o celu ekranu, akcji głównej i regionach
     → akceptujesz lub poprawiasz strukturę, zanim powstanie kod
3. Implementacja wyłącznie z komponentów i tokenów DS, ze wszystkimi stanami
4. Pętla wizualna: zrzuty 375 px i 1280 px (+ dark), Claude ogląda i poprawia
5. /devkit:review-changes → frontend-reviewer (kod + zrzuty) → poprawki
```

### Brakuje komponentu

Nie robisz jednorazowego komponentu w feature. Kolejność: komponent w `components/ui/`
+ story + review, a dopiero potem użycie w feature. Claude powinien to zaproponować sam.
Jeśli tego nie zrobi, `frontend-reviewer` zgłosi duplikat.

### Zmiana tokenu

1. Zmiana w warstwie semantycznej (np. `--color-accent`).
2. Zrzuty kluczowych stories i ekranów przed i po. Przy testach wizualnych Playwright pokaże różnice.
3. Sprawdzenie kontrastu.
4. Zmiana znacząca (nowy akcent, nowa skala)? Nowy ADR, który zastępuje poprzedni.

### Masz makiety w Figmie

Jeśli projektujesz w Figmie, połącz connector Figma. Claude odczyta makietę, ale implementuje
**z komponentów i tokenów DS**, a nie z wartości wpisanych na sztywno z makiety. Rozbieżność
między makietą a tokenami to pytanie do Ciebie, a nie powód do dodania nowego koloru.

## Antywzorce

- Styl wpisany wprost w feature „bo tylko tutaj”: po miesiącu masz 5 wersji tego samego przycisku.
- Ślepe kopiowanie szablonu dashboardu z internetu: to marketingowa estetyka w narzędziu roboczym.
- Tokeny jako jedyna dokumentacja („jest w CSS”): bez Storybooka nikt, łącznie z modelem,
  nie widzi, co już istnieje.
- „Wygląda OK” bez zrzutu ekranu: model nie widzi UI, dopóki go nie wyrenderuje i nie obejrzy.
- Kolor jako jedyny nośnik informacji (statusy, legenda mapy).

# devkit

Plugin do Claude Code wspierający codzienną pracę i rozwój w stacku
**Python/Django/FastAPI · React/TypeScript · PostgreSQL/PostGIS · dane GIS i mapy webowe · Docker · Kubernetes (k3s) · GitOps · CI/CD**.

devkit dostarcza:
- **agentów (subagentów)** do zadań, które warto odizolować: implementacja w osobnym worktree,
  niezależne review (kod, bezpieczeństwo, baza, infrastruktura, frontend), testy, diagnoza klastra,
  research dokumentacji;
- **skille**, czyli wiedzę o technologiach i kilka procesów (review ryzyka, nauka przy zadaniu,
  budowanie UI), ładowane dopiero wtedy, gdy są potrzebne;
- **hook read-only**, który technicznie blokuje reviewerom zmiany w klastrze, repo, bazie i plikach;
- **serwery LSP** dla TypeScriptu i Pythona: diagnostyka po każdej edycji i nawigacja po symbolach;
- **wzorce pracy**: dokumentacja (ADR-y, `CLAUDE.md`), design system, szablon `CLAUDE.md` dla
  projektów. To repo stosuje je samo na sobie.

devkit jest zaprojektowany do pracy **obok skilli Matta Pococka** ([`mattpocock/skills`](https://github.com/mattpocock/skills)):
Matt prowadzi proces (od pomysłu przez spec i tickety do commita), a devkit dostarcza wiedzę
o stacku i wyspecjalizowanych agentów, którzy wpinają się w kroki tego procesu
([ADR-0013](docs/adr/0013-process-belongs-to-matt-pocock-skills.md)). Jak to połączyć:
[Praca obok skilli Matta Pococka](#praca-obok-skilli-matta-pococka).

---

## Spis treści

1. [Instalacja](#instalacja)
2. [Jak to jest zbudowane](#jak-to-jest-zbudowane)
3. [Praca obok skilli Matta Pococka](#praca-obok-skilli-matta-pococka)
4. [Agenci](#agenci)
5. [Skille](#skille)
6. [Jak korzystać: wywoływanie](#jak-korzystać-wywoływanie)
7. [Workflowy](#workflowy)
8. [Bezpieczeństwo: hook read-only](#bezpieczeństwo-hook-read-only)
9. [Serwery LSP](#serwery-lsp)
10. [Dokumentacja i decyzje](#dokumentacja-i-decyzje)
11. [Codex](#codex)
12. [Rozwijanie devkitu](#rozwijanie-devkitu)
13. [Zawartość repo](#zawartość-repo)

---

## Instalacja

```bash
# 1. raz na maszynę: zarejestruj to repo jako marketplace (ścieżka lokalna lub URL gita)
claude plugin marketplace add ~/dev/devkit

# 2. w każdym projekcie, w którym chcesz devkit:
cd ~/dev/moj-projekt
claude plugin install devkit@dampe --scope project   # zapisuje .claude/settings.json: commituj go

# 3. po zmianach w tym repo:
claude plugin marketplace update dampe
```

Test bez instalacji: `claude --plugin-dir ~/dev/devkit`.

Nowy projekt razem ze skillami Matta: [setup krok po kroku](#1-setup-nowego-projektu-raz).
W skrócie: plugin → `npx skills@latest add mattpocock/skills` → szablon
[`templates/CLAUDE.project.md`](templates/CLAUDE.project.md) jako `CLAUDE.md` → `/setup-matt-pocock-skills`.

**Wymagania:** `python3` (hook), serwery LSP na `PATH` (raz na maszynę, [szczegóły](#serwery-lsp)), opcjonalnie narzędzia wykorzystywane przez skille i agentów:
`kubeconform`, `kube-linter`, `hadolint`, `actionlint`, `trivy`, Playwright (zrzuty ekranu UI).
Agenci sprawdzają, co jest zainstalowane, i nie zakładają reszty.

---

## Jak to jest zbudowane

Trzy warstwy, każda z inną odpowiedzialnością ([ADR-0002](docs/adr/0002-agents-are-roles-skills-are-knowledge.md)):

| Warstwa | Gdzie | Co zawiera | Kiedy się ładuje |
|---|---|---|---|
| **Agent** | `agents/` (plugin) | **rolę**: metodę pracy, narzędzia, format wyniku. Bez wiedzy o stacku. | gdy główna sesja deleguje zadanie |
| **Skill** | `skills/` (plugin) | **wiedzę o technologii** lub **proces**, opcjonalnie `references/` (cięższe materiały) i `assets/` (pliki do skopiowania) | na żądanie: po opisie, po ścieżce pliku (`paths`), przez `/devkit:…`, albo wklejony agentowi (`skills:`) |
| **CLAUDE.md** | w projekcie | **fakty o projekcie**: komendy, architektura, CRS, design, deploy | zawsze, w danym projekcie |

Co gdzie trafia:
- **Agent** tylko wtedy, gdy potrzebujesz izolacji kontekstu (dużo logów, plików, stron WWW),
  innych uprawnień (read-only), równoległości albo niezależnego spojrzenia (review).
  Nie tworzymy agentów w stylu `django-expert`, `typescript-expert` ani „UI/UX designer”: tracą
  kontekst rozmowy, a model i tak zna te technologie ([ADR-0010](docs/adr/0010-typescript-files-only-as-assets.md),
  [ADR-0009](docs/adr/0009-ui-quality-through-design-system.md)).
- **Skill** dla wiedzy i procesów. Wartość jest w tym, czego model nie wie: Twoich konwencjach,
  pułapkach i sposobie weryfikacji.
- **Asset** (plik w `skills/<name>/assets/`) tylko wtedy, gdy konkretny plik niesie decyzje lepiej
  niż proza i nie da się go wygenerować narzędziem. Obecnie jest jeden: `building-ui/assets/tokens.css`.
- **Hook** dla każdej reguły, którą da się wymusić mechanicznie.

---

## Praca obok skilli Matta Pococka

**Matt prowadzi proces, devkit dostarcza wiedzę i specjalistów**
([ADR-0013](docs/adr/0013-process-belongs-to-matt-pocock-skills.md)). Skilli Matta się nie
edytuje, bo aktualizują się z upstreamu (`skills-lock.json`). Dlatego to devkit się dopasowuje
na dwa sposoby:

- **opisy skilli devkitu nie konkurują o te same słowa**: „review” należy do `/code-review`,
  ADR-y do `domain-modeling`, nauka wielosesyjna do `/teach`;
- **połączenie jest zapisane w projekcie**: sekcja `## Workflow` w szablonie `CLAUDE.md` ładuje
  się zawsze, więc `/implement` Matta wie, kiedy sięgnąć po reviewerów i agentów devkitu.

### Kto za co odpowiada

| Obszar | Matt | devkit |
|---|---|---|
| Od pomysłu do commita | `/grill-with-docs` → `/to-spec` → `/to-tickets` → `/implement` (z `/tdd`) | dwa opcjonalne kroki QRSPI w lukach flow: `/devkit:to-research-questions` przed grillem, `/devkit:to-design-discussion` przed specem ([ADR-0015](docs/adr/0015-qrspi-steps-extend-matts-flow.md)) |
| Słownik domeny | `CONTEXT.md` (`domain-modeling`) | skille używają jego terminów |
| Decyzje | ADR-y w formacie `domain-modeling`, zapisywane przez `/grill-with-docs` | `code-reviewer` zgłasza brakujący ADR; skille wiedzy podsuwają decyzje typowe dla stacku |
| Tracker, etykiety | `docs/agents/*.md` (`/setup-matt-pocock-skills`), `/triage` | worker i `review-changes` czytają tickety według `docs/agents/issue-tracker.md` |
| Review | osie **Standards** i **Spec** (`/code-review`) | oś **Risk** (`/devkit:review-changes` + 5 reviewerów) |
| Wiedza o technologiach | brak | Django, FastAPI, TS, React, UI, mapy, PostGIS, walidacja geo, k8s, obrazy, CI |
| Izolacja i równoległość | `/implement` per ticket z `/clear` | `implementation-worker` (frontier ticketów w worktree), `test-runner`, `cluster-investigator`, `docs-researcher` |
| Trudne błędy | `/diagnosing-bugs` | `test-runner` (pętla odtwarzająca błąd), `cluster-investigator`, `postgres-reviewer` (EXPLAIN) |
| Research | `/research` (plik z cytatami w repo) | `docs-researcher` jako agent dla pytań o wersje bibliotek |
| Nauka | `/teach`: wielosesyjnie, w osobnym katalogu | `/devkit:mentor`: przy realnym zadaniu, `TODO(human)` |
| Dokumentacja | `writing-for-agents` (`CLAUDE.md`, `AGENTS.md`, skille) | `documenting-code` (README, docstringi, komentarze, runbooki; co gdzie trafia) |
| Prototyp | `/prototype` (logika albo warianty UI) | `building-ui` buduje wybraną strukturę docelowo, w design systemie |
| Bezpieczeństwo agentów | `git-guardrails-claude-code` (opcjonalnie) | hook read-only dla reviewerów; oba hooki działają obok siebie |

### 1. Setup nowego projektu (raz)

```bash
cd ~/dev/moj-projekt
claude plugin install devkit@dampe --scope project          # 1. devkit (zapisuje .claude/settings.json)
npx skills@latest add mattpocock/skills                     # 2. skille Matta (.claude/skills + skills-lock.json)
cp ~/dev/devkit/templates/CLAUDE.project.md CLAUDE.md       # 3. szablon: uzupełnij, zostaw sekcję ## Workflow
claude                                                      # 4. w sesji:
  /setup-matt-pocock-skills                                 #    tracker, etykiety triage, układ CONTEXT.md/ADR
```

Kolejność ma znaczenie. `/setup-matt-pocock-skills` edytuje istniejący `CLAUDE.md` (dopisuje blok
`## Agent skills` i pliki `docs/agents/*.md`), a nie tworzy osobnego `AGENTS.md`. Jeśli uruchomisz
go przed skopiowaniem szablonu, zapyta, który plik utworzyć, i reguły z `## Workflow` trafią
w inne miejsce niż wskaźniki Matta.

Po instalacji:
- `CONTEXT.md` i `docs/adr/` **nie** zakładaj z góry. Powstaną same przy pierwszym `/grill-with-docs`.
- Usuń skille Matta, których projekt nie potrzebuje, np. `migrate-to-shoehorn` i
  `scaffold-exercises` w projekcie bez kursów TS, albo `setup-pre-commit` (Husky), gdy używasz
  `pre-commit`. Każdy zbędny opis skilla to kontekst zużyty w każdej turze i szansa, że odpali się
  nie ten skill.
- **Nie włączaj obok drugiego frameworka procesowego** (np. superpowers). Dubluje grillowanie,
  planowanie, TDD, review i debugowanie, więc skille trzech źródeł konkurują o te same triggery.
  Wyłączenie w projekcie: `"enabledPlugins": {"superpowers@claude-plugins-official": false}`
  w `.claude/settings.json`.

### 2. Główny flow z punktami wpięcia devkitu

```
[opcjonalnie, ticket w kodzie, którego sesja nie zna]
/devkit:to-research-questions <ticket>  pytania o obecny kod, bez intencji
  → /research w świeżej sesji (tylko plik z pytaniami) → <obszar>-research.md
  ▼
/grill-with-docs                      wywiad → CONTEXT.md + ADR-y (z ticketem i plikiem research)
  │  devkit: skille wiedzy podsuwają pytania i sensowne domyślne (CRS, kody wyjścia walidatora,
  │          fundament design systemu, układ GitOps); docs-researcher, gdy odpowiedź zależy od wersji
  │
  ├─ pytanie wymaga działającego kodu? → /handoff → /prototype → /handoff z wnioskami
  │     devkit: web-maps i building-ui przy prototypie mapy lub ekranu
  ├─ projekt warto pokazać właścicielowi kodu? → /devkit:to-design-discussion
  │     ~200 linii: stan obecny i docelowy, wzorce Follow/Avoid, decyzje D1…, otwarte pytania;
  │     uwagi z review rozwiązujesz w tej samej sesji
  ▼
/to-spec → /to-tickets                spec i tickety z blokerami w trackerze
  │  sekcja "Testing Decisions" = seamy; implementation-worker pracuje tylko na nich
  ▼
/implement  (jeden ticket, /clear przed następnym)
  │  /tdd czerwone → zielone; skille wiedzy włączają się same po ścieżkach plików
  │  końcowy przebieg testów, lintów i typów → devkit:test-runner (logi poza kontekstem)
  │  /code-review <fixed-point>       ## Standards + ## Spec
  │  /devkit:review-changes <ten sam fixed-point>   ## Risk   (gdy diff dotyka auth, bazy,
  │                                                            infrastruktury albo frontendu)
  ▼
poprawki → commit (hook pre-commit, jeśli jest)
```

Kroki 1–3 (grill, spec, tickety) rób w jednym oknie kontekstu, bez `/clear`. Każdy `/implement`
zaczyna od świeżego kontekstu, więc reviewerzy devkitu biorą intencję z ticketu, a nie z rozmowy.

Mała zmiana bez specu: opis → `/tdd` (albo `/implement` w tej samej sesji) → `/code-review` →
`/devkit:review-changes` → commit. Oś Spec zgłosi wtedy „no spec available” i to jest w porządku.

### 3. Tickety równolegle: frontier i `implementation-worker`

Matt robi tickety po kolei. Gdy kilka ticketów ma zamknięte wszystkie blokery (tzw. **frontier**),
można je zrobić równolegle, każdy w osobnym worktree:

```
"Tickety #12, #13 i #15 mają zamknięte blokery. Każdy daj osobnemu implementation-worker,
 równolegle; commit w worktree"
  → worker: ticket + spec-rodzic → CONTEXT.md, ADR-y → /tdd na seamach ze specu → raport
       (Status, Ticket, kryteria akceptacji met/not met, weryfikacja)
  → worker bez uzgodnionych seamów albo z otwartym blokerem kończy jako "blocked" i niczego nie zgaduje
Scalasz worktree → devkit:test-runner → /code-review → /devkit:review-changes → zamykasz tickety
  → nowy frontier
```

- „commit w worktree” w poleceniu jest potrzebny, bo worker domyślnie nie commituje, a bez
  commitów nie ma czego scalić.
- Workerzy nie uruchamiają review. Review robisz raz, na scalonym diffie.
- Tickety, które się zazębiają (wspólne pliki, kolejne kroki expand–contract), rób po kolei.

### 4. Review: trzy osie, raportowane osobno

| Oś | Skąd | Pyta o | Kto |
|---|---|---|---|
| **Standards** | `/code-review` (Matt) | czy kod trzyma się udokumentowanych standardów repo; code smelle (Fowler) | sub-agent Matta |
| **Spec** | `/code-review` (Matt) | czy diff robi to, o co prosił ticket lub spec; brakujące wymagania, nadmiarowy zakres | sub-agent Matta |
| **Risk** | `/devkit:review-changes` | co się zepsuje: poprawność, regresje, luki w testach, bezpieczeństwo, blokady migracji, deploy, stany UI, nieaktualne docs i `CONTEXT.md` | `code-reviewer` + specjaliści według plików |

Osi się nie scala i nie ustawia w jednym rankingu, tak jak Matt nie scala Standards ze Spec.
Reviewerzy devkitu nie zgłaszają smelli ani zgodności ze specem, żeby nic nie było raportowane dwa razy.

### 5. Sytuacje poza głównym flow

| Sytuacja | Od czego zacząć | Rola devkitu |
|---|---|---|
| Decyzja architektoniczna | `/grill-with-docs` (zapisze ADR) | wskaźnik ADR-a w `CLAUDE.md`, komentarz `ADR-NNNN` w kodzie (`documenting-code`) |
| Trudny lub sporadyczny bug | `/diagnosing-bugs` | `test-runner` daje komendę odtwarzającą błąd, czyli pętlę z Fazy 1 |
| Czerwone CI | `devkit:test-runner` | gdy klasyfikacja to „needs diagnosis”, przejdź do `/diagnosing-bugs` |
| Awaria w klastrze | `devkit:cluster-investigator` | poprawka przez GitOps, potem oś Risk (`platform-reviewer`) |
| Wolne zapytanie, migracja | `devkit:postgres-reviewer` | EXPLAIN jako pętla dla `/diagnosing-bugs` |
| Upgrade biblioteki | `devkit:docs-researcher`, a gdy wynik ma zostać w repo, `/research` | zmiana decyzji: nowy ADR przez `/grill-with-docs` |
| Zgłoszenia z zewnątrz | `/triage` | brak (tickety z `/to-tickets` się nie triażuje) |
| Porządki w architekturze | `/improve-codebase-architecture` (słownik: `codebase-design`) | skille wiedzy dają kontekst stacku przy wybranym kandydacie |
| Nauka | `/teach` (plan, wiele sesji) albo `/devkit:mentor` (przy zadaniu) | mentor ćwiczy kamienie milowe z `/teach` na realnym kodzie |

### 6. Czego unikać

- `/devkit:review-changes` **zamiast** `/code-review`. To dodatkowa oś, a nie zamiennik.
- ADR-ów w innym formacie niż `domain-modeling`. Devkit nie ma już własnego szablonu ADR.
- Dawania `implementation-worker` ticketu z otwartym blokerem albo bez uzgodnionych seamów.
- Triażowania ticketów, które wyprodukował `/to-tickets`. Są gotowe dla agenta z założenia.
- Edycji skilli Matta. Dopasowania rób w devkicie albo w `## Workflow` w `CLAUDE.md` projektu.
- Drugiego frameworka procesowego obok tych dwóch.

### Bez skilli Matta

Devkit działa też sam: skille wiedzy, reviewerzy, `test-runner`, `cluster-investigator` i hook.
Odwołania do `/code-review`, `tdd`, `domain-modeling` i `docs/agents/` zostaną wtedy pominięte,
a oś Risk działa jako zwykłe review. Devkit nie prowadzi jednak procesu i nie pisze ADR-ów.

---

## Agenci

W sesji mają prefiks `devkit:`, np. `devkit:code-reviewer`.

| Agent | Kiedy używać | Model | Effort | Zapisuje? |
|---|---|---|---|---|
| `implementation-worker` | jeden ticket z frontieru (blokery zamknięte) albo jedno niezależne zadanie z kryteriami akceptacji. `/tdd` na seamach ze specu, osobny **git worktree**. | inherit | z sesji | tak (w worktree) |
| `code-reviewer` | oś Risk: poprawność, regresje, luki w testach, **nieaktualna dokumentacja i `CONTEXT.md`**, brak ADR-a (smelle i zgodność ze specem zostawia `/code-review`) | sonnet | high | nie |
| `security-reviewer` | endpointy, uprawnienia, wejście od użytkownika, uploady, sekrety, CI, obsługa tokenów i HTML we froncie | inherit | xhigh | nie |
| `postgres-reviewer` | migracje, modele, SQL, ciężkie zapytania ORM, zapytania przestrzenne (PostGIS) | inherit | high | nie |
| `platform-reviewer` | Dockerfile, compose, k8s/Helm/Kustomize, ArgoCD, pipeline'y CI | inherit | high | nie |
| `frontend-reviewer` | `.tsx`/`.ts`: stany UI, efekty, dostępność, typy na granicy API, XSS, spójność z design systemem, wydajność, mapy. Robi też **zrzuty ekranu**, jeśli UI działa. | inherit | high | nie |
| `test-runner` | testy, lintery i sprawdzanie typów (pytest, vitest, playwright, tsc…) oraz diagnoza błędów, bez zalewania głównego kontekstu; końcowy przebieg w `/implement`, trudne przypadki przekazuje do `/diagnosing-bugs` | sonnet | medium | nie |
| `cluster-investigator` | coś nie działa w klastrze: CrashLoop, Pending, ArgoCD OutOfSync, Tekton. Używa **kubectl tylko do odczytu**. | sonnet | high | nie |
| `docs-researcher` | odpowiedź zależy od wersji biblioteki lub narzędzia: upgrade, nowa opcja, deprecacje; także agent dla `/research` o bibliotekach | sonnet | medium | nie |

**Effort** jest ustawiony jawnie tam, gdzie jakość nie może zależeć od tego, na jakim poziomie
akurat pracujesz w sesji. Bez tego pola agent dziedziczy poziom sesji
([ADR-0008](docs/adr/0008-explicit-effort-per-role.md)).
Do eksploracji kodu służy wbudowany agent **`Explore`** ([ADR-0004](docs/adr/0004-use-builtin-explore.md)).

---

## Skille

### Procesy

| Skill | Wywołanie | Co robi |
|---|---|---|
| `review-changes` | `/devkit:review-changes [fixed-point]`, po `/code-review` | oś **Risk**: kieruje diff do właściwych reviewerów **równolegle**, łączy ich wyniki, sam sprawdza każde znalezisko critical/high i raportuje osobno od Standards i Spec |
| `mentor` | `/devkit:mentor [temat]` albo „naucz mnie…” | nauka przy realnym zadaniu: model mentalny, zadania `TODO(human)`, podpowiedzi stopniowane, podsumowanie, `LEARNING.md`. Plan nauki na wiele sesji: `/teach` |
| `to-research-questions` | `/devkit:to-research-questions <ticket>` przed `/grill-with-docs` | krok QRSPI: zamienia ticket na pytania o obecny kod bez śladu intencji, dla ślepego `/research` w świeżej sesji |
| `to-design-discussion` | `/devkit:to-design-discussion` po `/grill-with-docs` | krok QRSPI: dokument około 200 linii do review przez właściciela kodu przed `/to-spec`; każdy wskaźnik do kodu sprawdzony |
| `building-ui` | przy tworzeniu widoków, komponentów, stylów | design system projektu → cel ekranu → budowa z tokenów i komponentów → wszystkie stany → **zrzuty ekranu przed „gotowe”** |

### Wiedza (ładuje się sama, gdy pracujesz na pasujących plikach lub tematach)

| Skill | Włącza się przy |
|---|---|
| `django-conventions` | `models.py`, `views.py`, `serializers.py`, `migrations/`, `settings*` |
| `fastapi-conventions` | pracy z FastAPI (po opisie) |
| `frontend-stack` | łączeniu frontendu z API (po opisie): klient i typy z OpenAPI, kontrola dryfu w CI, zod dla danych spoza API; testy frontu (MSW, `QueryClient` per test, mapy poza jsdom, Playwright) |
| `web-maps` | mapach w React (po opisie): MapLibre vs OpenLayers, EPSG:2180 na mapie, MVT z PostGIS, błędy walidacji na mapie |
| `postgres-postgis` | `*.sql`, `migrations/`, `alembic/versions/`, zapytaniach przestrzennych |
| `geospatial-validation` | pracy nad walidatorem danych geo i webserwisem (po opisie) |
| `kubernetes-manifests` | `kustomization.yaml`, `Chart.yaml`, `values*.yaml`, `k8s/`, `manifests/`, `argocd/`… |
| `container-images` | `Dockerfile*`, `.dockerignore`, `compose*.yml` (Python/uv, GDAL, obrazy frontendu, multi-arch) |
| `ci-pipelines` | `.github/workflows/`, `.gitlab-ci.yml`, `tekton/` |
| `documenting-code` | pisaniu README, docstringów, komentarzy, runbooków; decyduje, co gdzie trafia (`CONTEXT.md`, ADR, tracker, `docs/`) |
| `review-standards` | wklejany reviewerom: wagi znalezisk, wymagane dowody, format (niewidoczny w menu `/`) |

---

## Jak korzystać: wywoływanie

| Chcę… | Jak |
|---|---|
| uruchomić skill | `/devkit:review-changes main` albo po prostu opisz zadanie: model sam dobierze skill |
| użyć konkretnego agenta | napisz „użyj cluster-investigator, żeby…” albo `@agent-devkit:cluster-investigator …` |
| kilka agentów naraz | „odpal security-reviewer i postgres-reviewer równolegle na tym diffie” |
| sprawdzić, co jest załadowane | `/agents` (agenci) i menu `/` (skille) |
| tryb nauki na całą sesję | `/devkit:mentor` na początku sesji, albo wbudowany styl `/output-style learning` |
| review ryzyka po `/code-review` | `/devkit:review-changes <ten sam fixed-point>` |

Wskazówka: agenci dostają **tylko to, co napiszesz w poleceniu**, bez historii rozmowy. Podawaj
cel, pliki, ograniczenia („tabela ma ~40M wierszy”, „działa na arm64 Pi”, „dev server na :5173”).
Skill `review-changes` robi to za Ciebie.

---

## Workflowy

Workflowy zakładają, że w projekcie są skille Matta (patrz
[Praca obok skilli Matta Pococka](#praca-obok-skilli-matta-pococka)). Workflowy 1–2 i 12–13 to
główny flow Matta z punktami wpięcia devkitu. Pozostałe to soczewki stackowe, które w ten flow
wchodzą.

| # | Sytuacja | Główne elementy |
|---|---|---|
| 1 | [Codzienna zmiana](#1-codzienna-zmiana-mały-feature-bugfix) | `/tdd` lub `/implement` + `/code-review` + oś Risk |
| 2 | [Większy feature, praca równoległa](#2-większy-feature-spec-tickety-i-praca-równoległa) | `/grill-with-docs` → `/to-spec` → `/to-tickets` → `implementation-worker` × frontier |
| 3 | [Feature fullstack](#3-feature-fullstack-api-w-django-lub-fastapi--widok-w-react) | backend → typy z OpenAPI → React |
| 4 | [Nowy widok UI](#4-nowy-widok-ui) | (`/prototype`) + `building-ui` + pętla zrzutów ekranu + `frontend-reviewer` |
| 5 | [Budowa design systemu](#5-budowa-design-systemu) | [`docs/design-system.md`](docs/design-system.md) |
| 6 | [Mapa z danymi przestrzennymi](#6-mapa-z-danymi-przestrzennymi) | `web-maps` + `postgres-postgis` |
| 7 | [Migracja bazy i PostGIS](#7-migracja-bazy-i-zapytania-postgis) | `postgres-reviewer` + EXPLAIN |
| 8 | [Awaria w klastrze](#8-coś-nie-działa-w-klastrze-k3s) | `cluster-investigator` → GitOps |
| 9 | [Nauka](#9-nauka-homelab-platform-engineering-frontend) | `/devkit:mentor` przy zadaniu, `/teach` na wiele sesji |
| 10 | [Upgrade, nowa technologia](#10-upgrade-lub-nowa-technologia) | `docs-researcher` / `/research` |
| 11 | [Czerwone CI](#11-czerwone-ci) | `test-runner` + `ci-pipelines` → `/diagnosing-bugs` |
| 12 | [Decyzja architektoniczna](#12-decyzja-architektoniczna) | `/grill-with-docs` → ADR |
| 13 | [Start nowego projektu](#13-start-nowego-projektu) | devkit + skille Matta + szablon `CLAUDE.md` + `/setup-matt-pocock-skills` |

### 1. Codzienna zmiana (mały feature, bugfix)

```
Ty: opisujesz zmianę (niejasna? krótkie /grill-with-docs)
  → /tdd dla jednego zachowania albo /implement w tej samej sesji
      (skille wiedzy włączają się same po plikach)
  → /code-review main                  ## Standards + ## Spec ("no spec available" bez ticketu)
  → /devkit:review-changes main        ## Risk
      ├─ code-reviewer       (zawsze)
      ├─ security-reviewer   (endpointy, uprawnienia, uploady, tokeny)
      ├─ postgres-reviewer   (modele, migracje, zapytania)
      ├─ platform-reviewer   (Docker, k8s, CI)
      └─ frontend-reviewer   (.tsx/.ts)
  → poprawki → "odpal test-runner" → commit
```

Najczęstszy tryb. Implementacja zostaje w głównej sesji, bo tam jest kontekst rozmowy.
Trudny bug zamiast drobnej poprawki? Zacznij od `/diagnosing-bugs`.

### 2. Większy feature: spec, tickety i praca równoległa

```
1. /grill-with-docs → CONTEXT.md i ADR-y (skille wiedzy podsuwają decyzje stackowe)
2. /to-spec  → seamy testów w "Testing Decisions" potwierdzasz Ty
3. /to-tickets → tickety z blokerami w trackerze
   (kroki 1–3 w jednym oknie kontekstu, bez /clear)
4a. Po kolei: /implement per ticket, /clear przed następnym
4b. Równolegle: tickety z frontieru → implementation-worker × N, "commit w worktree"
      → raport per ticket: Status, kryteria akceptacji, weryfikacja
5. Scalasz worktree → test-runner → /code-review → /devkit:review-changes → zamykasz tickety
6. Kolejny frontier → wróć do 4
```

Szczegóły: [Tickety równolegle](#3-tickety-równolegle-frontier-i-implementation-worker).
Tickety, które się zazębiają, rób po kolei, nawet jeśli formalnie nie blokują się nawzajem.

### 3. Feature fullstack: API w Django lub FastAPI + widok w React

```
1. Backend: endpoint + serializer/schema + testy (django/fastapi-conventions, /tdd na seamie API)
2. pnpm gen:api → typy i klient TS z OpenAPI (frontend-stack)
     → zmiana w API, która psuje frontend, wychodzi przy tsc, a nie na produkcji
3. Frontend: widok według workflow 4 (building-ui + frontend-stack)
4. /code-review → /devkit:review-changes → security + postgres (backend), frontend-reviewer (UI)
5. test-runner: pytest + vitest; Playwright dla krytycznego flow
```

W `/to-tickets` taki feature to zwykle jeden pionowy ticket (tracer bullet: API + typy + widok),
a nie osobne tickety „backend” i „frontend”.

### 4. Nowy widok UI

```
1. "Zrób widok listy obserwacji z filtrem po gatunku"
   (układ ekranu to otwarte pytanie? najpierw /prototype: kilka wariantów UI na jednej trasie)
2. building-ui: Claude szuka design systemu (tokeny, components/ui, Storybook)
     → 3–5 linii: cel ekranu, akcja główna, gęstość, regiony → akceptujesz strukturę
3. Implementacja wyłącznie z tokenów i komponentów DS; stany loading/empty/error/overflow
4. Pętla wizualna: npx playwright screenshot 375 px / 1280 px / dark → Claude ogląda PNG → poprawia
5. /code-review → /devkit:review-changes → frontend-reviewer (kod + własne zrzuty) → poprawki
```

Bez działającego dev serwera lub Storybooka Claude ma powiedzieć wprost, że weryfikacji wizualnej
nie było. Szczegóły i uzasadnienie: [ADR-0009](docs/adr/0009-ui-quality-through-design-system.md).

### 5. Budowa design systemu

Pełny przewodnik: **[`docs/design-system.md`](docs/design-system.md)**. W skrócie:

```
Faza 0  decyzje w /grill-with-docs: charakter produktu, gęstość, fundament (shadcn/ui+Tailwind v4 | Mantine | Radix) → ADR
Faza 1  tokeny: start z building-ui/assets/tokens.css → paleta, typografia, gęstość, kontrast → Storybook "Tokens"
Faza 2  komponenty: inwentarz z listy ekranów → prymitywy → złożone → wzorce; każdy ze stories wszystkich stanów
Faza 3  egzekwowanie: lint bez dowolnych wartości, testy wizualne stories w CI, sekcja Design w CLAUDE.md
Potem   brakujący komponent → najpierw do DS, potem do feature; zmiana tokenu → zrzuty przed/po
```

### 6. Mapa z danymi przestrzennymi

```
"Warstwa wydzieleń leśnych na mapie, filtrowana po gatunku"
  → web-maps: MapLibre (dane w 3857) czy OpenLayers (WMTS w 2180)?  (pytanie do /grill-with-docs, wynik: ADR)
  → skala danych: GeoJSON < ~5k obiektów, powyżej MVT z PostGIS (ST_AsMVT) → postgres-reviewer
  → building-ui (references/data-dense-and-maps): mapa + panel, bottom sheet na mobile, legenda
  → stan widoku w URL, dane przez TanStack Query z bbox i AbortSignal
  → frontend-reviewer: instancja mapy, sprzątanie efektów, dostępność kontrolek
```

### 7. Migracja bazy i zapytania PostGIS

```
1. Piszesz model lub migrację (postgres-postgis podpowiada bezpieczne wzorce)
2. python manage.py sqlmigrate app 00NN → "postgres-reviewer, oceń tę migrację; tabela ma ~N wierszy"
3. Reviewer podaje poziom blokady i ryzyko oraz EXPLAIN (ANALYZE, BUFFERS) do uruchomienia
4. Uruchamiasz EXPLAIN na danych zbliżonych do prod → wynik wklejasz → decyzja
```

Migracja dużej tabeli w `/to-tickets` to sekwencja expand–contract: osobne tickety na expand,
migrację danych i contract, z blokerami między nimi.

### 8. Coś nie działa w klastrze k3s

```
"cluster-investigator: aplikacja forest-web nie odpowiada od rana"
  → agent (tylko odczyt): context → get → describe → logs → events → argocd app get/diff
  → raport: przyczyna (confirmed/likely) + dowody + proponowana poprawka
Ty: poprawka w repo GitOps (nie kubectl apply!) → /devkit:review-changes (platform-reviewer) → commit → ArgoCD sync
```

Agent sam nie naprawia. Hook zablokuje mu `apply`, `delete`, `exec` i wypisywanie Secretów.
Przyczyna nie wychodzi z jednego przebiegu? `/diagnosing-bugs`, a `cluster-investigator` dostarcza mu dowodów.

### 9. Nauka: homelab, platform engineering, frontend

```
/devkit:mentor postaw ArgoCD z app-of-apps na moim k3s
  → model mentalny (≤10 linii) + typowe pułapki + link do dokumentacji
  → Claude robi rusztowanie, Ty piszesz fragmenty TODO(human)
  → "przewidź, co pokaże argocd app diff" → uruchomienie → porównanie
  → review Twojego kodu jak od seniora → podsumowanie + ćwiczenie + wpis w LEARNING.md
```

Działa tak samo dla frontendu (np. „naucz mnie focus trap w Dialogu”) i Go/Rust. Powiedz
„po prostu zrób”, a mentor przełączy się w normalny tryb.

Chcesz poznać temat w wielu sesjach (plan, lekcje, powtórki)? `/teach` w osobnym katalogu,
z misją opartą na Twoich projektach. Kamienie milowe ćwiczysz potem z `/devkit:mentor` na realnym kodzie.

### 10. Upgrade lub nowa technologia

```
"docs-researcher: co się zmienia przy upgrade ArgoCD z 2.x na 3.x w naszym setupie?"
  → agent sprawdza wersje w repo (Chart.yaml, lockfile) → oficjalne release notes → raport ze źródłami
  (wynik ma zostać w repo? /research: ten sam research jako plik z cytatami)
→ zmienia decyzję? /grill-with-docs → nowy ADR, który zastępuje stary
→ /to-spec + /to-tickets (workflow 2) albo od razu workflow 1
```

### 11. Czerwone CI

```
Wklejasz link lub log z GitHub Actions, GitLaba albo Tektona → "test-runner, zdiagnozuj"
  → odtwarza tymi samymi komendami co CI → klasyfikacja: bug / błędny test / środowisko / flaky / needs diagnosis
  → poprawka w głównej sesji
  → needs diagnosis: /diagnosing-bugs, a komenda od test-runner to jego pętla z Fazy 1
Pipeline sam się sypie? → platform-reviewer + ci-pipelines (actionlint, glab ci lint, tkn)
```

### 12. Decyzja architektoniczna

```
Rozmowa w /grill-with-docs: "geometrie trzymamy w 2180 czy 4326?" → decyzja
  → domain-modeling zapisuje docs/adr/NNNN-....md (krótko; odrzucone opcje, gdy warto je pamiętać)
  → nowe pojęcia trafiają do CONTEXT.md
  → jednolinijkowy wskaźnik w CLAUDE.md projektu, komentarz ADR-NNNN przy kodzie (documenting-code)
```

ADR powstaje, gdy decyzję trudno odwrócić, bez kontekstu jest zaskakująca i była prawdziwym
wyborem między alternatywami (wszystkie trzy). `code-reviewer` zgłosi brak ADR-a według tego samego kryterium.

### 13. Start nowego projektu

```
1. Setup: devkit + skille Matta + szablon CLAUDE.md + /setup-matt-pocock-skills
   (krok po kroku: "Praca obok skilli Matta Pococka" → "Setup nowego projektu")
2. /grill-with-docs o samym projekcie: stack, CRS, fundament design systemu, deploy → pierwsze ADR-y i CONTEXT.md
3. Frontend? → workflow 5 (design system) przed pierwszymi ekranami
4. Pierwszy feature → workflow 2 (albo 1, jeśli jest mały)
```

---

## Bezpieczeństwo: hook read-only

Agenci dostarczani w pluginie ignorują `permissionMode` i `hooks` we frontmatterze. Dlatego tryb
read-only wymusza hook `PreToolUse` na poziomie pluginu ([ADR-0003](docs/adr/0003-readonly-guard-hook.md)).
Dotyczy: `code-reviewer`, `security-reviewer`, `postgres-reviewer`, `platform-reviewer`,
`frontend-reviewer`, `test-runner`, `cluster-investigator`. **Główna sesja i `implementation-worker`
nie są ograniczane.** Sub-agentów skilli Matta (np. osi Standards i Spec w `/code-review`) hook też
nie dotyczy.

Blokuje:
- czasowniki zmieniające stan w `kubectl`/`helm`/`argocd`/`tkn`/`flux`/`terraform` (dozwolone
  są tylko odczyty, `diff` i `apply --dry-run`);
- `logs -f` i `get -w` (zawieszają agenta);
- wypisywanie wartości Secretów;
- `docker push`/`run`, `compose up`/`down`;
- `git push`/`commit`/`reset`/`stash`;
- DML/DDL przez `psql`;
- `npm`/`pnpm`/`yarn add|install|update|publish` (dozwolone `npm ci` i `install --frozen-lockfile`);
- poprawianie plików przez lintery i formattery: `--fix`, `--write`, `ruff format` / `black` bez `--check`;
- zapis plików z shella (`rm`, `mv`, `sed -i`, przekierowanie `>` do pliku…).

Dozwolone są m.in. testy, lintery w trybie sprawdzania, `tsc --noEmit` i `npx playwright screenshot`
(zrzuty do `/tmp`).

Hook łapie pomyłki, ale nie celowe obejście. Prawdziwą granicą dla klastra jest kubeconfig
z ServiceAccountem z rolą `view`, która nie widzi też Secretów:

```bash
kubectl create sa claude-readonly -n kube-system
kubectl create clusterrolebinding claude-readonly --clusterrole=view \
  --serviceaccount=kube-system:claude-readonly
# zbuduj kubeconfig dla tego SA i uruchamiaj: KUBECONFIG=~/.kube/claude-readonly.yaml claude
```

---

## Serwery LSP

devkit rejestruje w [`.lsp.json`](.lsp.json) dwa serwery języka
([ADR-0016](docs/adr/0016-lsp-servers-in-plugin.md)). Po każdej edycji pliku Claude dostaje błędy
typów i brakujące importy (`Found N new diagnostic issues`, rozwinięcie: `Ctrl+O`), a narzędzie
`LSP` szuka definicji i referencji po symbolach.

| Serwer | Pliki | Instalacja binarki (raz na maszynę) |
|---|---|---|
| `typescript-language-server` | `.ts` `.tsx` `.mts` `.cts` `.js` `.jsx` `.mjs` `.cjs` | `npm install -g typescript-language-server typescript` |
| `pyright-langserver` | `.py` `.pyi` | `uv tool install pyright` (albo `pipx install pyright`, `npm install -g pyright`) |

- Binarka musi być na `PATH` powłoki, z której startuje `claude`. Brak widać w `/plugin` → **Errors**
  (`Executable not found in $PATH`). Po instalacji wystarczy kolejna edycja pliku.
- TypeScript bierze `tsserver` z `node_modules` projektu, więc typy zgadzają się z wersją projektu.
  Pyright czyta `pyrightconfig.json` albo `[tool.pyright]` w `pyproject.toml` i potrzebuje aktywnego
  venv (`.venv` w katalogu projektu), żeby rozwiązać importy. W projekcie Django dołóż `django-stubs`.
- Wyłącz oficjalne `typescript-lsp` i `pyright-lsp`, jeśli je masz: dwa serwery dla tych samych
  plików dublują diagnostykę.

---

## Dokumentacja i decyzje

Podejście: **dokumentuj „dlaczego”, generuj „co”, pilnuj aktualności w review**
([ADR-0006](docs/adr/0006-documentation-strategy.md)). Treści dla modelu są po angielsku,
dla ludzi po polsku ([ADR-0005](docs/adr/0005-language-policy.md)).

| Dokument | Po co |
|---|---|
| [`docs/dokumentacja.md`](docs/dokumentacja.md) | jak prowadzimy dokumentację: mapa, cykl życia, checklista przed commitem |
| [`docs/design-system.md`](docs/design-system.md) | jak zbudować design system i pracować z nim z Claude |
| [`skills/documenting-code`](skills/documenting-code/SKILL.md) | reguły dokumentacji, z których korzysta model |
| [`CLAUDE.md`](CLAUDE.md) | konwencje dla pracy nad tym repo |
| [`templates/CLAUDE.project.md`](templates/CLAUDE.project.md) | szablon `CLAUDE.md` dla projektów |

Decyzje dotyczące samego devkitu:

| ADR | Decyzja |
|---|---|
| [0001](docs/adr/0001-distribute-as-plugin.md) | plugin instalowany per projekt |
| [0002](docs/adr/0002-agents-are-roles-skills-are-knowledge.md) | agenci to role, wiedza w skillach |
| [0003](docs/adr/0003-readonly-guard-hook.md) | read-only wymusza hook, a nie prompt |
| [0004](docs/adr/0004-use-builtin-explore.md) | eksploracja przez wbudowany `Explore` |
| [0005](docs/adr/0005-language-policy.md) | model po angielsku, ludzie po polsku |
| [0006](docs/adr/0006-documentation-strategy.md) | dokumentujemy „dlaczego”, generujemy „co” |
| [0007](docs/adr/0007-frontend-lens-reviewer.md) | frontend: skille + `frontend-reviewer` |
| [0008](docs/adr/0008-explicit-effort-per-role.md) | jawny `effort` per rola |
| [0009](docs/adr/0009-ui-quality-through-design-system.md) | jakość UI przez design system i zrzuty, bez agenta-designera |
| [0010](docs/adr/0010-typescript-files-only-as-assets.md) | bez agentów od TS; pliki TS/CSS tylko jako assety |
| [0011](docs/adr/0011-codex-variant-as-independent-copy.md) | wariant dla Codex CLI jako niezależna kopia w `codex/` |
| [0012](docs/adr/0012-codex-guard-as-plugin-hook.md) | guard read-only w Codeksie jako hook pluginu filtrowany po `agent_type` |
| [0013](docs/adr/0013-process-belongs-to-matt-pocock-skills.md) | proces należy do skilli Matta Pococka; devkit to wiedza i role, bez skilla `adr` |
| [0014](docs/adr/0014-knowledge-skills-hold-only-what-the-model-lacks.md) | skille wiedzy tylko z tym, czego model nie ma; React i TS zastępuje `frontend-stack` |
| [0015](docs/adr/0015-qrspi-steps-extend-matts-flow.md) | kroki QRSPI (`to-research-questions`, `to-design-discussion`) wypełniają luki we flow Matta |
| [0016](docs/adr/0016-lsp-servers-in-plugin.md) | serwery LSP (TypeScript, Pyright) w `.lsp.json` pluginu |

---

## Codex

Katalog [`codex/`](codex/README.md) zawiera **niezależną wersję devkitu dla Codex CLI** i modeli
OpenAI: plugin ze skillami, 9 ról jako agenci TOML, guard read-only i sandbox. To osobna kopia plików,
a nie symlinki ([ADR-0011](docs/adr/0011-codex-variant-as-independent-copy.md)). Instalacja i różnice
względem wersji Claude są w [`codex/README.md`](codex/README.md).

```bash
codex plugin marketplace add ~/dev/devkit/codex        # raz na maszynę
codex plugin add devkit@dampe                                 # skille + guard read-only
python3 ~/dev/devkit/codex/scripts/install_agents.py ~/dev/moj-projekt   # role
cp ~/dev/devkit/codex/templates/AGENTS.project.md ~/dev/moj-projekt/AGENTS.md
```

---

## Rozwijanie devkitu

Konwencje dla pracy nad tym repo są w [`CLAUDE.md`](CLAUDE.md). W skrócie:

```bash
claude plugin validate .                 # manifesty
python3 hooks/test_guard_readonly.py     # testy hooka
claude --plugin-dir .                    # test na żywo
```

- Nowa technologia to nowy **skill**, a nie nowy agent.
- Nie dubluj skilli procesowych Matta (grill, spec, tickety, tdd, review Standards/Spec, ADR-y,
  `/teach`). Opis nowego skilla nie może konkurować z ich triggerami; wpinaj się w ich kroki ([ADR-0013](docs/adr/0013-process-belongs-to-matt-pocock-skills.md)).
- Nowy krok procesu tylko tam, gdzie flow Matta ma lukę, i zawsze z wynikiem oddawanym jednemu z jego kroków, jak QRSPI ([ADR-0015](docs/adr/0015-qrspi-steps-extend-matts-flow.md)).
- Nowy agent read-only wymaga `disallowedTools`, wpisu w `READONLY_AGENTS` i testu.
- Nowy asset wymaga uzasadnienia: jaką decyzję niesie i dlaczego nie da się go wygenerować.
- Istotna zmiana podejścia to nowy ADR w `docs/adr/`.
- Każda zmiana zachowania oznacza podbicie `version` w `.claude-plugin/plugin.json`.

---

## Zawartość repo

```
.claude-plugin/
  plugin.json              # manifest pluginu "devkit"
  marketplace.json         # marketplace "dampe" (source: ./)
.lsp.json                  # serwery LSP: TypeScript, Pyright
agents/                    # 9 agentów (role)
skills/                    # 16 skilli (wiedza i procesy)
  <name>/SKILL.md          #   instrukcja
  <name>/references/       #   cięższe materiały, czytane na żądanie
  building-ui/assets/      #   tokens.css: startowe tokeny design systemu
hooks/
  hooks.json               # rejestracja PreToolUse → guard
  guard_readonly.py        # hook read-only
  test_guard_readonly.py   # testy hooka
templates/
  CLAUDE.project.md        # szablon CLAUDE.md dla projektów
docs/
  dokumentacja.md          # jak prowadzimy dokumentację
  design-system.md         # workflow design systemu
  adr/                     # decyzje (0001–0016)
CLAUDE.md                  # instrukcje dla Claude przy pracy nad tym repo
codex/                     # niezależna wersja dla Codex CLI (patrz codex/README.md)
_archive/agents-v1/        # poprzednie wersje agentów (niewczytywane)
```

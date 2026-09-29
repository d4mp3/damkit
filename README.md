# devkit

Plugin do Claude Code wspierający codzienną pracę i rozwój w stacku
**Python/Django/FastAPI · React/TypeScript · PostgreSQL/PostGIS · dane GIS i mapy webowe · Docker · Kubernetes (k3s) · GitOps · CI/CD**.

devkit dostarcza:
- **agentów (subagentów)** do zadań, które warto odizolować: implementacja w osobnym worktree,
  niezależne review (kod, bezpieczeństwo, baza, infrastruktura, frontend), testy, diagnoza klastra,
  research dokumentacji;
- **skille**, czyli wiedzę o technologiach i procesy (review, nauka, ADR, budowanie UI), ładowane
  dopiero wtedy, gdy są potrzebne;
- **hook read-only**, który technicznie blokuje reviewerom zmiany w klastrze, repo, bazie i plikach;
- **wzorce pracy**: dokumentacja (ADR-y, `CLAUDE.md`), design system, szablon `CLAUDE.md` dla
  projektów. To repo stosuje je samo na sobie.

---

## Spis treści

1. [Instalacja](#instalacja)
2. [Jak to jest zbudowane](#jak-to-jest-zbudowane)
3. [Agenci](#agenci)
4. [Skille](#skille)
5. [Jak korzystać: wywoływanie](#jak-korzystać-wywoływanie)
6. [Workflowy](#workflowy)
7. [Bezpieczeństwo: hook read-only](#bezpieczeństwo-hook-read-only)
8. [Dokumentacja i decyzje](#dokumentacja-i-decyzje)
9. [Rozwijanie devkitu](#rozwijanie-devkitu)
10. [Zawartość repo](#zawartość-repo)

---

## Instalacja

```bash
# 1. raz na maszynę: zarejestruj to repo jako marketplace (ścieżka lokalna lub URL gita)
claude plugin marketplace add ~/dev/claude-config

# 2. w każdym projekcie, w którym chcesz devkit:
cd ~/dev/moj-projekt
claude plugin install devkit@dampe --scope project   # zapisuje .claude/settings.json: commituj go

# 3. po zmianach w tym repo:
claude plugin marketplace update dampe
```

Test bez instalacji: `claude --plugin-dir ~/dev/claude-config`.

Nowy projekt: skopiuj [`templates/CLAUDE.project.md`](templates/CLAUDE.project.md) jako `CLAUDE.md`
i uzupełnij tylko to, czego nie da się odczytać z kodu: komendy, CRS, design, cel deployu.

**Wymagania:** `python3` (hook), opcjonalnie narzędzia wykorzystywane przez skille i agentów:
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

## Agenci

W sesji mają prefiks `devkit:`, np. `devkit:code-reviewer`.

| Agent | Kiedy używać | Model | Effort | Zapisuje? |
|---|---|---|---|---|
| `implementation-worker` | jedno jasno określone, niezależne zadanie z kryteriami akceptacji. Pracuje w osobnym **git worktree**. | inherit | z sesji | tak (w worktree) |
| `code-reviewer` | po implementacji: poprawność, regresje, testy, zbędna złożoność, **nieaktualna dokumentacja**, brak ADR-a | sonnet | high | nie |
| `security-reviewer` | endpointy, uprawnienia, wejście od użytkownika, uploady, sekrety, CI, obsługa tokenów i HTML we froncie | inherit | xhigh | nie |
| `postgres-reviewer` | migracje, modele, SQL, ciężkie zapytania ORM, zapytania przestrzenne (PostGIS) | inherit | high | nie |
| `platform-reviewer` | Dockerfile, compose, k8s/Helm/Kustomize, ArgoCD, pipeline'y CI | inherit | high | nie |
| `frontend-reviewer` | `.tsx`/`.ts`: stany UI, efekty, dostępność, typy na granicy API, XSS, spójność z design systemem, wydajność, mapy. Robi też **zrzuty ekranu**, jeśli UI działa. | inherit | high | nie |
| `test-runner` | testy, lintery i sprawdzanie typów (pytest, vitest, playwright, tsc…) oraz diagnoza błędów, bez zalewania głównego kontekstu | sonnet | medium | nie |
| `cluster-investigator` | coś nie działa w klastrze: CrashLoop, Pending, ArgoCD OutOfSync, Tekton. Używa **kubectl tylko do odczytu**. | sonnet | high | nie |
| `docs-researcher` | odpowiedź zależy od wersji biblioteki lub narzędzia: upgrade, nowa opcja, deprecacje | sonnet | medium | nie |

**Effort** jest ustawiony jawnie tam, gdzie jakość nie może zależeć od tego, na jakim poziomie
akurat pracujesz w sesji. Bez tego pola agent dziedziczy poziom sesji
([ADR-0008](docs/adr/0008-explicit-effort-per-role.md)).
Do eksploracji kodu służy wbudowany agent **`Explore`** ([ADR-0004](docs/adr/0004-use-builtin-explore.md)).

---

## Skille

### Procesy

| Skill | Wywołanie | Co robi |
|---|---|---|
| `review-changes` | `/devkit:review-changes [base]` | kieruje diff do właściwych reviewerów **równolegle**, łączy wyniki i sam sprawdza każde znalezisko critical/high |
| `mentor` | `/devkit:mentor [temat]` albo „naucz mnie…” | tryb nauki: model mentalny, zadania `TODO(human)`, podpowiedzi stopniowane, podsumowanie, `LEARNING.md` |
| `adr` | `/devkit:adr [tytuł]`, albo model sam zaproponuje | zapisuje decyzję w `docs/adr/` z kontekstem i odrzuconymi opcjami z rozmowy |
| `building-ui` | przy tworzeniu widoków, komponentów, stylów | design system projektu → cel ekranu → budowa z tokenów i komponentów → wszystkie stany → **zrzuty ekranu przed „gotowe”** |

### Wiedza (ładuje się sama, gdy pracujesz na pasujących plikach lub tematach)

| Skill | Włącza się przy |
|---|---|
| `django-conventions` | `models.py`, `views.py`, `serializers.py`, `migrations/`, `settings*` |
| `fastapi-conventions` | pracy z FastAPI (po opisie) |
| `typescript-conventions` | `*.ts`, `*.tsx`, `tsconfig*.json`, `package.json`, `vite.config.*`: strict, zod na granicach, typy z OpenAPI |
| `react-conventions` | `*.tsx`, `*.jsx`: stan, efekty, TanStack Query, dostępność, testy (Vitest, Testing Library, MSW, Playwright) |
| `web-maps` | mapach w React (po opisie): MapLibre vs OpenLayers, EPSG:2180 na mapie, MVT z PostGIS, błędy walidacji na mapie |
| `postgres-postgis` | `*.sql`, `migrations/`, `alembic/versions/`, zapytaniach przestrzennych |
| `geospatial-validation` | pracy nad walidatorem danych geo i webserwisem (po opisie) |
| `kubernetes-manifests` | `kustomization.yaml`, `Chart.yaml`, `values*.yaml`, `k8s/`, `manifests/`, `argocd/`… |
| `container-images` | `Dockerfile*`, `.dockerignore`, `compose*.yml` (Python/uv, GDAL, obrazy frontendu, multi-arch) |
| `ci-pipelines` | `.github/workflows/`, `.gitlab-ci.yml`, `tekton/` |
| `documenting-code` | pisaniu README, docstringów, komentarzy, `CLAUDE.md`, runbooków |
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

Wskazówka: agenci dostają **tylko to, co napiszesz w poleceniu**, bez historii rozmowy. Podawaj
cel, pliki, ograniczenia („tabela ma ~40M wierszy”, „działa na arm64 Pi”, „dev server na :5173”).
Skill `review-changes` robi to za Ciebie.

---

## Workflowy

| # | Sytuacja | Główne elementy |
|---|---|---|
| 1 | [Codzienna zmiana](#1-codzienna-zmiana-mały-feature-bugfix) | główna sesja + `review-changes` + `test-runner` |
| 2 | [Większy feature, praca równoległa](#2-większy-feature-z-planem-i-pracą-równoległą) | plan + `implementation-worker` × N |
| 3 | [Feature fullstack](#3-feature-fullstack-api-w-django-lub-fastapi--widok-w-react) | backend → typy z OpenAPI → React |
| 4 | [Nowy widok UI](#4-nowy-widok-ui) | `building-ui` + pętla zrzutów ekranu + `frontend-reviewer` |
| 5 | [Budowa design systemu](#5-budowa-design-systemu) | [`docs/design-system.md`](docs/design-system.md) |
| 6 | [Mapa z danymi przestrzennymi](#6-mapa-z-danymi-przestrzennymi) | `web-maps` + `postgres-postgis` |
| 7 | [Migracja bazy i PostGIS](#7-migracja-bazy-i-zapytania-postgis) | `postgres-reviewer` + EXPLAIN |
| 8 | [Awaria w klastrze](#8-coś-nie-działa-w-klastrze-k3s) | `cluster-investigator` → GitOps |
| 9 | [Nauka](#9-nauka-homelab-platform-engineering-frontend) | `/devkit:mentor` |
| 10 | [Upgrade, nowa technologia](#10-upgrade-lub-nowa-technologia) | `docs-researcher` |
| 11 | [Czerwone CI](#11-czerwone-ci) | `test-runner` + `ci-pipelines` |
| 12 | [Decyzja architektoniczna](#12-decyzja-architektoniczna) | `/devkit:adr` |
| 13 | [Start nowego projektu](#13-start-nowego-projektu) | instalacja + szablon `CLAUDE.md` + ADR-y |

### 1. Codzienna zmiana (mały feature, bugfix)

```
Ty: opisujesz zmianę → główna sesja implementuje (skille włączają się same po plikach)
  → /devkit:review-changes
      ├─ code-reviewer       (zawsze)
      ├─ security-reviewer   (endpointy, uprawnienia, uploady, tokeny)
      ├─ postgres-reviewer   (modele, migracje, zapytania)
      ├─ platform-reviewer   (Docker, k8s, CI)
      └─ frontend-reviewer   (.tsx/.ts)
  → poprawki → "odpal test-runner" → commit
```

Najczęstszy tryb. Implementacja zostaje w głównej sesji, bo tam jest kontekst rozmowy.

### 2. Większy feature z planem i pracą równoległą

```
1. Plan mode (Shift+Tab) lub "zaplanuj": główna sesja + Explore rozpoznają kod
2. Plan dzielisz na NIEZALEŻNE zadania z kryteriami akceptacji
3. "Każde zadanie daj implementation-worker, równolegle"
     → każdy worker w osobnym git worktree → raport: status, pliki, weryfikacja
4. Scalasz worktree → /devkit:review-changes → test-runner
5. Decyzja architektoniczna po drodze? → /devkit:adr
```

Tylko dla zadań, które naprawdę się nie zazębiają. Zadań powiązanych nie rozdzielaj.

### 3. Feature fullstack: API w Django lub FastAPI + widok w React

```
1. Backend: endpoint + serializer/schema + testy (django/fastapi-conventions)
2. pnpm gen:api → typy i klient TS z OpenAPI (typescript-conventions)
     → zmiana w API, która psuje frontend, wychodzi przy tsc, a nie na produkcji
3. Frontend: widok według workflow 4 (building-ui + react-conventions)
4. /devkit:review-changes → security + postgres (backend), frontend-reviewer (UI)
5. test-runner: pytest + vitest; Playwright dla krytycznego flow
```

### 4. Nowy widok UI

```
1. "Zrób widok listy obserwacji z filtrem po gatunku"
2. building-ui: Claude szuka design systemu (tokeny, components/ui, Storybook)
     → 3–5 linii: cel ekranu, akcja główna, gęstość, regiony → akceptujesz strukturę
3. Implementacja wyłącznie z tokenów i komponentów DS; stany loading/empty/error/overflow
4. Pętla wizualna: npx playwright screenshot 375 px / 1280 px / dark → Claude ogląda PNG → poprawia
5. /devkit:review-changes → frontend-reviewer (kod + własne zrzuty) → poprawki
```

Bez działającego dev serwera lub Storybooka Claude ma powiedzieć wprost, że weryfikacji wizualnej
nie było. Szczegóły i uzasadnienie: [ADR-0009](docs/adr/0009-ui-quality-through-design-system.md).

### 5. Budowa design systemu

Pełny przewodnik: **[`docs/design-system.md`](docs/design-system.md)**. W skrócie:

```
Faza 0  decyzje: charakter produktu, gęstość, fundament (shadcn/ui+Tailwind v4 | Mantine | Radix) → /devkit:adr
Faza 1  tokeny: start z building-ui/assets/tokens.css → paleta, typografia, gęstość, kontrast → Storybook "Tokens"
Faza 2  komponenty: inwentarz z listy ekranów → prymitywy → złożone → wzorce; każdy ze stories wszystkich stanów
Faza 3  egzekwowanie: lint bez dowolnych wartości, testy wizualne stories w CI, sekcja Design w CLAUDE.md
Potem   brakujący komponent → najpierw do DS, potem do feature; zmiana tokenu → zrzuty przed/po
```

### 6. Mapa z danymi przestrzennymi

```
"Warstwa wydzieleń leśnych na mapie, filtrowana po gatunku"
  → web-maps: MapLibre (dane w 3857) czy OpenLayers (WMTS w 2180)?
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

### 8. Coś nie działa w klastrze k3s

```
"cluster-investigator: aplikacja forest-web nie odpowiada od rana"
  → agent (tylko odczyt): context → get → describe → logs → events → argocd app get/diff
  → raport: przyczyna (confirmed/likely) + dowody + proponowana poprawka
Ty: poprawka w repo GitOps (nie kubectl apply!) → platform-reviewer na diffie → commit → ArgoCD sync
```

Agent sam nie naprawia. Hook zablokuje mu `apply`, `delete`, `exec` i wypisywanie Secretów.

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

### 10. Upgrade lub nowa technologia

```
"docs-researcher: co się zmienia przy upgrade ArgoCD z 2.x na 3.x w naszym setupie?"
  → agent sprawdza wersje w repo (Chart.yaml, lockfile) → oficjalne release notes → raport ze źródłami
→ plan zmian → workflow 1 lub 2 → /devkit:adr, jeśli decyzja jest istotna
```

### 11. Czerwone CI

```
Wklejasz link lub log z GitHub Actions, GitLaba albo Tektona → "test-runner, zdiagnozuj"
  → odtwarza tymi samymi komendami co CI → klasyfikacja: bug / błędny test / środowisko / flaky
  → poprawka w głównej sesji
Pipeline sam się sypie? → platform-reviewer + ci-pipelines (actionlint, glab ci lint, tkn)
```

### 12. Decyzja architektoniczna

```
Rozmowa: "geometrie trzymamy w 2180 czy 4326?" → decyzja
  → model proponuje ADR (albo /devkit:adr "CRS przechowywania geometrii")
  → docs/adr/NNNN-....md z kontekstem i odrzuconymi opcjami z rozmowy
  → jednolinijkowy wskaźnik w CLAUDE.md projektu
```

### 13. Start nowego projektu

```
1. claude plugin install devkit@dampe --scope project
2. cp ~/dev/claude-config/templates/CLAUDE.project.md CLAUDE.md → uzupełnij (bez sekcji, które nie dotyczą)
3. /devkit:adr dla pierwszych decyzji (stack, CRS, fundament design systemu, deploy)
4. Frontend? → workflow 5 (design system) przed pierwszymi ekranami
5. Pierwszy feature → workflow 1
```

---

## Bezpieczeństwo: hook read-only

Agenci dostarczani w pluginie ignorują `permissionMode` i `hooks` we frontmatterze. Dlatego tryb
read-only wymusza hook `PreToolUse` na poziomie pluginu ([ADR-0003](docs/adr/0003-readonly-guard-hook.md)).
Dotyczy: `code-reviewer`, `security-reviewer`, `postgres-reviewer`, `platform-reviewer`,
`frontend-reviewer`, `test-runner`, `cluster-investigator`. **Główna sesja i `implementation-worker`
nie są ograniczane.**

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

---

## Rozwijanie devkitu

Konwencje dla pracy nad tym repo są w [`CLAUDE.md`](CLAUDE.md). W skrócie:

```bash
claude plugin validate .                 # manifesty
python3 hooks/test_guard_readonly.py     # testy hooka
claude --plugin-dir .                    # test na żywo
```

- Nowa technologia to nowy **skill**, a nie nowy agent.
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
agents/                    # 9 agentów (role)
skills/                    # 16 skilli (wiedza i procesy)
  <name>/SKILL.md          #   instrukcja
  <name>/references/       #   cięższe materiały, czytane na żądanie
  building-ui/assets/      #   tokens.css: startowe tokeny design systemu
  adr/template.md          #   szablon ADR
hooks/
  hooks.json               # rejestracja PreToolUse → guard
  guard_readonly.py        # hook read-only
  test_guard_readonly.py   # testy hooka
templates/
  CLAUDE.project.md        # szablon CLAUDE.md dla projektów
docs/
  dokumentacja.md          # jak prowadzimy dokumentację
  design-system.md         # workflow design systemu
  adr/                     # decyzje (0001–0010)
CLAUDE.md                  # instrukcje dla Claude przy pracy nad tym repo
_archive/agents-v1/        # poprzednie wersje agentów (niewczytywane)
```

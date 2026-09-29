# devkit dla Codex

Wersja devkitu dla **Codex CLI** (0.156+) i modeli OpenAI. Daje te same role (9 agentów), tę samą
wiedzę (16 skilli) i te same wzorce pracy co plugin dla Claude Code w katalogu głównym repo, ale
korzysta z mechanizmów Codeksa: pluginu ze skillami i hookiem, agentów w TOML i sandboxa.

To **niezależna kopia**: wszystkie pliki leżą w `codex/`, bez symlinków i bez odwołań do plików spoza
tego katalogu ([ADR-0011](../docs/adr/0011-codex-variant-as-independent-copy.md)). Opis ról, skilli
i 13 workflowów jest w [README w katalogu głównym](../README.md). Tutaj są tylko instalacja i różnice.

---

## Instalacja

```bash
# 1. raz na maszynę: zarejestruj marketplace "dampe" (katalog codex/)
codex plugin marketplace add ~/dev/devkit/codex

# 2. raz na maszynę: zainstaluj plugin (skille + guard read-only). Wpis trafia do
#    ~/.codex/config.toml, więc działa we wszystkich projektach; samo marketplace add nic nie instaluje.
codex plugin add devkit@dampe

# 3. w projekcie: role agentów
python3 ~/dev/devkit/codex/scripts/install_agents.py ~/dev/moj-projekt
#    → .codex/agents/*.toml: commituj

# 4. instrukcje projektu
cp ~/dev/devkit/codex/templates/AGENTS.project.md ~/dev/moj-projekt/AGENTS.md
```

- Agenci wymagają włączonego multi-agent (`[features] multi_agent = true`; w 0.156 domyślnie włączone).
- Codex wczytuje `.codex/` projektu (agentów, config) dopiero wtedy, gdy projekt jest zaufany
  (pytanie przy pierwszym uruchomieniu).
- Hook guarda z pluginu Codex uruchamia dopiero po tym, jak mu zaufasz. Zatwierdź go, gdy Codex
  poprosi o przegląd hooków. Bez tego guard jest nieaktywny, a zostaje tylko sandbox.
- Po zmianach w tym repo: ponownie `codex plugin add devkit@dampe` (odświeża kopię pluginu w cache;
  `marketplace upgrade` działa tylko dla marketplace'ów z gita) i ponownie `install_agents.py` (agenci).
  Instalator nadpisuje tylko pliki 9 ról i wypisuje, co zmienił. `--dry-run` pokazuje zmiany bez zapisu.
- Sprawdź, czy wszystko działa: `bash ~/dev/devkit/codex/scripts/verify_guard.sh` (patrz
  [Bezpieczeństwo](#bezpieczeństwo-read-only)).

**Wymagania:** `python3`, `git`. Opcjonalnie te same narzędzia co w wersji Claude (`kubeconform`,
`kube-linter`, `hadolint`, `actionlint`, `trivy`, Playwright).

---

## Wywoływanie

| Chcę… | Jak |
|---|---|
| uruchomić skill | wybierz z `/skills` albo wpisz `$` i nazwę skilla. Model widzi skille z prefiksem pluginu (`devkit:review-changes`, `devkit:mentor`), więc w razie wątpliwości użyj pełnej nazwy. Możesz też po prostu opisać zadanie, a model sam dobierze skill po opisie. |
| użyć konkretnego agenta | „spawn agent `cluster_investigator`: aplikacja forest-web nie odpowiada” |
| kilka agentów naraz | „odpal `security_reviewer` i `postgres_reviewer` równolegle na tym diffie” albo `$review-changes` |
| eksplorować kod | wbudowany agent `explorer` |
| sprawdzić, co jest dostępne | `/skills` (skille), `.codex/agents/` w projekcie (role) |

Role devkitu trzeba uruchamiać z `agent_type` i `fork_turns: "none"` (reguła jest w szablonie
`AGENTS.project.md`). Pełny fork historii dziedziczy typ, model i effort rodzica i odrzuca `agent_type`.
Jeśli model obejdzie błąd, pomijając `agent_type`, dostaniesz zwykłego agenta z sandboxem sesji,
czyli bez read-only. Przy `fork_turns: "none"` agent dostaje tylko to, co napiszesz w poleceniu.
Podawaj cel, pliki i ograniczenia, tak jak w wersji Claude.

Codex ogranicza liczbę równoległych agentów (domyślnie kilka slotów, łącznie z główną sesją).
`$review-changes` uruchamia tyle reviewerów, ile jest slotów, a resztę po zwolnieniu miejsca.

---

## Agenci

| Agent | Model | Effort | Sandbox | Guard |
|---|---|---|---|---|
| `implementation_worker` | z sesji | z sesji | z sesji | nie |
| `code_reviewer` | `gpt-6-sol` | high | read-only | tak |
| `security_reviewer` | z sesji | xhigh | read-only | tak |
| `postgres_reviewer` | z sesji | high | read-only | tak |
| `platform_reviewer` | z sesji | high | read-only | tak |
| `frontend_reviewer` | z sesji | high | read-only | tak |
| `test_runner` | `gpt-6-sol` | medium | read-only | tak |
| `cluster_investigator` | `gpt-6-sol` | high | read-only | tak |
| `docs_researcher` | `gpt-6-sol` | medium | read-only | nie |

`gpt-6-sol` dostały role, które w wersji Claude działają na `sonnet`. Gdy OpenAI zmieni listę
modeli, zaktualizuj `model` w tych czterech plikach.

---

## Różnice względem wersji Claude

| Claude devkit | Codex devkit |
|---|---|
| agenci w pluginie (`agents/*.md`) | plugin nie może zawierać agentów: `agents/*.toml` kopiuje do projektu `install_agents.py` |
| nazwy `code-reviewer`… | `code_reviewer`… (snake_case) |
| `model: sonnet` / `inherit` | `model = "gpt-6-sol"` / brak pola |
| `effort` | `model_reasoning_effort` (te same wartości) |
| `skills:` wklejane agentowi | pierwszy krok w `developer_instructions`: „załaduj skill …” |
| `disallowedTools: Edit, Write` + hook pluginu filtrowany po `agent_type` | `sandbox_mode = "read-only"` + ten sam guard jako hook pluginu, filtrowany po `agent_type` (patrz niżej) |
| `implementation-worker` w osobnym worktree | brak izolacji per agent; worker pracuje w bieżącym drzewie, równolegle tylko na rozłącznych plikach. Worktree może założyć główna sesja. |
| wbudowany `Explore` | wbudowany `explorer` |
| `CLAUDE.md` | `AGENTS.md` |
| `/devkit:review-changes` | `/skills` albo `$devkit:review-changes` |
| `paths:` w skillach (włączanie po plikach) | brak; wzorce plików są dopisane do `description` |
| `review-standards` ukryty w menu | widoczny w `/skills` (reviewerzy ładują go sami) |

Skutki sandboxa read-only:
- **`test_runner`** wyłącza cache testów (`-p no:cacheprovider` itd.). Błąd zapisu odrzuconego przez
  sandbox raportuje jako **environment**, a nie jako bug.
- **`frontend_reviewer`** potrzebuje Twojej zgody na `curl` do dev serwera i na zrzuty ekranu
  (sieć i zapis). Bez zgody raportuje „Visual check: not performed (sandbox)”.
- **`cluster_investigator`**: sandbox blokuje sieć, więc każda komenda do klastra wymaga Twojej zgody.
  Agent grupuje odczyty, żeby tych próśb było mało.
- **`docs_researcher`** korzysta z narzędzia web search, a nie z sieci w shellu.

---

## Bezpieczeństwo: read-only

Główną granicą jest **sandbox Codeksa** (`sandbox_mode = "read-only"`). System operacyjny blokuje
zapis plików i sieć, niezależnie od tego, co model postanowi.

Guard (`hooks/guard_readonly.py`, port hooka z wersji Claude) dokłada reguły, których sandbox nie
wyrazi: gdy zgodzisz się na komendę, i tak zablokuje `kubectl apply`/`delete`/`exec`, wypisywanie
Secretów, `logs -f`, `git push` i resztę listy z [głównego README](../README.md#bezpieczeństwo-hook-read-only).
Działa jak w wersji Claude: to hook `PreToolUse` w pluginie (`hooks/hooks.json`). Codex przekazuje
w wejściu hooka `agent_type`, czyli nazwę roli, więc guard ogranicza tylko 7 ról read-only
(wszystkie z kolumną „Guard: tak”), a główna sesja i `implementation_worker` pozostają bez ograniczeń.

Sprawdzone testem na Codex 0.156.1:
- hook projektu dostaje `agent_type` roli;
- hooki zadeklarowane w pliku agenta (TOML) **nie** są uruchamiane, dlatego guard jest w pluginie.

Sprawdź cały łańcuch raz po instalacji i po każdej aktualizacji Codeksa:

```bash
bash ~/dev/devkit/codex/scripts/verify_guard.sh
```

Skrypt wywołuje model (kilka tanich tur) w tymczasowym projekcie. Każe roli `code_reviewer` wykonać
`git commit`, a guard z zainstalowanego pluginu ma to zablokować. Zaufanie do hooków omija tylko dla
tego jednego wywołania.
- `GUARD: works`: guard działa, masz obie warstwy.
- `GUARD: NOT ACTIVE`: rola uruchomiła komendę, a guard jej nie zablokował. Sprawdź, czy plugin ma
  wersję 0.6.0+ (`codex plugin list`) i czy zaufałeś jego hookowi.
- `INCONCLUSIVE`: rola w ogóle nie wykonała komendy (brak logowania, multi-agent wyłączony, rola się
  nie wczytała). Skrypt wypisuje payloady hooków i końcówkę wyjścia Codeksa.

Na niektórych maszynach sandbox Codeksa w ogóle się nie uruchamia, np. z błędem
`error building bubblewrap command: … unsupported host mount at /run/mnt/data`. Wtedy żadna rola
read-only nie wykona nawet `git diff`. To problem środowiska (montowania w ścieżce katalogu socketów
app-servera), a nie devkitu. Zacznij od `codex doctor`. Guard i tak zadziała, bo odpala się przed
sandboxem, ale reviewerzy bez działającego sandboxa są bezużyteczni.

**Nie akceptuj zgód typu „nie pytaj ponownie” / reguły prefiksu** (np. dla `kubectl`, `helm`, `git`,
`psql`) na prośbę roli read-only. Taka reguła wypuszcza wszystkie pasujące komendy poza sandbox bez
pytania, także w głównej sesji. Guard nadal zatrzyma wtedy `kubectl delete` u ról read-only, ale
w głównej sesji już nic.

Prawdziwą granicą dla klastra jest kubeconfig z ServiceAccountem z rolą `view`. Guard i sandbox
chronią przed pomyłką, a ServiceAccount także przed zgodą wydaną zbyt pochopnie:

```bash
kubectl create sa codex-readonly -n kube-system
kubectl create clusterrolebinding codex-readonly --clusterrole=view \
  --serviceaccount=kube-system:codex-readonly
# zbuduj kubeconfig dla tego SA i uruchamiaj: KUBECONFIG=~/.kube/codex-readonly.yaml codex
```

---

## Rozwijanie

Konwencje dla modelu są w [`AGENTS.md`](AGENTS.md).

```bash
python3 codex/scripts/check.py                # manifesty, skille, agenci (statycznie)
python3 codex/scripts/test_check.py           # testy walidatora
python3 codex/hooks/test_guard_readonly.py    # testy guarda
python3 codex/scripts/test_install_agents.py  # testy instalatora
bash codex/scripts/verify_guard.sh            # test guarda end-to-end (wywołuje model)
```

- Zmiana w `skills/`, `agents/` lub `hooks/` w katalogu głównym? Rozważ przeniesienie jej tutaj
  (ręcznie, to niezależna kopia) i uruchom `check.py`.
- Każda zmiana zachowania oznacza podbicie `version` w `.codex-plugin/plugin.json`.
- Nowa rola read-only: `sandbox_mode = "read-only"`, wpis w `READONLY_AGENTS` w `hooks/guard_readonly.py`
  i w `READONLY_GUARDED` w `scripts/check.py` (check pilnuje, żeby się zgadzały), plus test w
  `hooks/test_guard_readonly.py`. Nie dodawaj `[[hooks…]]` do TOML ról: Codex ich nie uruchamia.

---

## Zawartość katalogu

```
codex/
  .codex-plugin/plugin.json         # manifest pluginu "devkit" (skille, hook, interface)
  .agents/plugins/marketplace.json  # marketplace "dampe" (source: ./)
  skills/                           # 16 skilli (kopie dostosowane do Codeksa)
  agents/                           # 9 ról w TOML (instalowane do projektu, nie przez plugin)
  hooks/
    hooks.json                      # rejestracja PreToolUse → guard (hook pluginu)
    guard_readonly.py               # guard read-only, filtrowany po agent_type
    test_guard_readonly.py          # testy guarda
  scripts/
    install_agents.py               # kopiuje role do <projekt>/.codex/agents/
    check.py                        # walidacja statyczna
    test_check.py, test_install_agents.py
    verify_guard.sh                 # test guarda end-to-end (wywołuje model)
  templates/AGENTS.project.md       # szablon AGENTS.md dla projektów
  AGENTS.md                         # instrukcje dla modelu przy pracy nad codex/
  README.md                         # ten plik
```

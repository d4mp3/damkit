---
name: setup-geostack
description: "Write or complete the project's CLAUDE.md (geostack's workflow, the project's commands, its language settings) and its shared .claude/settings.json (deny rules, check hooks, the geostack plugin). Run once per project, before /setup-matt-pocock-skills."
disable-model-invocation: true
---

# Setup geostack

Write the project's `CLAUDE.md` from `${CLAUDE_PLUGIN_ROOT}/skills/setup-geostack/assets/CLAUDE.project.md`,
filled with what the repo shows and what only the user knows, and its shared `.claude/settings.json` from
`${CLAUDE_PLUGIN_ROOT}/skills/setup-geostack/assets/settings.project.json`. It is the step before
`/setup-matt-pocock-skills`, which appends its `## Agent skills` block to the `CLAUDE.md` it finds.
Running in this order keeps geostack's `## Workflow` rules and Matt's pointers in one file.

This skill records **facts**, not decisions. Storage CRS, map library, design system foundation and
deployment layout are decisions: they belong to `/grill-with-docs` and end in ADRs. Where the repo has
not settled one yet, leave the template's placeholder and mark it `<decide in /grill-with-docs>`.

## Process

### 1. Check the starting point

- `CLAUDE.md` exists → you will **complete** it, never rewrite it. Note which template sections it lacks.
- Only `AGENTS.md` exists → ask which file holds the project instructions and work on that one.
- `## Agent skills` is already present → `/setup-matt-pocock-skills` ran first. That's fine: add geostack's
  sections above that block and leave it untouched.

### 2. Read the repo

Collect only what the model could not cheaply infer later:

- **Commands**: setup, tests (whole suite and a single file), lint/format, types, local run, API client
  generation. The commands CI runs (`.github/workflows/`, `.gitlab-ci.yml`, `tekton/`) are the truth;
  then `Makefile`/`justfile`, `pyproject.toml`, `package.json` scripts. Never invent a command:
  if you can't find one, leave the placeholder.
- **Stack**: which template sections apply. No frontend → drop `## Frontend` and `## Design`.
  No spatial data → drop `## Data & GIS`. No Kubernetes or GitOps → drop `## Deployment`.
- **Settled decisions**: existing ADRs (`docs/adr/`) that constrain everyday coding become one-line pointers.
  So does what the code has already settled: the SRID of geometry columns in models and migrations is
  the storage CRS. Only with no ADR and no geometry columns is the CRS left for `/grill-with-docs`.
- **Design**: where the design system lives is a fact: the tokens file, the components directory, the
  Storybook script and URL. Product character, density and layout patterns are decisions: take them
  from an ADR or existing docs, otherwise write `<decide in /grill-with-docs>`.
- **Deployment**: read what the repo shows: the registry and image names from CI push steps, the build
  system, ArgoCD Applications (app name, GitOps repo URL), Helm/Kustomize directories, node
  architecture from `nodeSelector`/`kubernetes.io/arch` or multi-arch builds, and the cluster's
  distribution, `ingressClassName`/`gatewayClassName` and `storageClassName` from manifests or
  infrastructure code (Terraform for EKS/GKE/AKS, k3s config, OpenShift `Route`s). The deployment layout is a
  decision: leave its placeholder. The cluster itself is a fact, asked in step 3 if the repo doesn't show it.
- **Language hints** for step 3: UI strings in components or i18n files, the language of README and
  docs, and the language of recent commit messages (`git log -20 --format=%s`).

### 3. Ask what the repo can't tell

Ask in one round, with the hints from step 2 as proposed answers:

- the conversation language;
- the UI copy language and tone (e.g. informal vs formal address), only if there is a UI;
- the locale for numbers, dates and units (e.g. `pl-PL`), only if there is a UI;
- the language of human-facing docs (README, `docs/`, ADRs) and of commit messages;
- "What this is", only if README doesn't answer it in a sentence or two;
- learning goals, optional: what the user wants to build or learn by hand in this project. `mentor` and
  `/teach` take their mission from it. A skip is a valid answer: then drop `## Learning goals`;
- the cluster, only if `## Deployment` applies and the repo didn't show it: distribution and node
  architectures, or who runs it. "Managed by the ops team, details unknown" is a full answer: write it
  as is, and reviewers then turn cluster-dependent risks into questions for that team instead of
  assuming a cluster.

The `## Language` section is what `building-ui`, `frontend-stack` and the QRSPI steps read, so
don't skip it, even when every answer is English.

### 4. Write `CLAUDE.md`

- New file: fill the template, drop the sections that don't apply and the template comment.
  Keep `## Workflow` verbatim: it is how Matt's `/implement` learns when to call geostack's agents.
- Existing file: add only the missing sections and missing command lines. When the file and the repo
  disagree (e.g. a test command CI no longer runs), ask instead of choosing.
- Keep it short: every line is loaded on every turn. Drop example values the project doesn't use.

### 5. Write `.claude/settings.json`

The shared project file holds what must hold for everyone and in cloud sessions, enforced by the
harness rather than read by the model. Start from the template and merge it into an existing file
(`claude plugin install --scope project` may have created one): add missing entries, keep the rest, ask
on conflicts. Never touch `.claude/settings.local.json`.

- **Deny** what can't be undone: reading secrets (a read lands in the transcript), force push, `reset --hard`,
  `git clean`. Add the other gitignored secret files the repo has (`.envrc`, `*.pem`, `secrets.toml`).
  If the repo commits a `.env.example`, replace `Read(./.env.*)` with the ignored env files by name, so
  Claude can still read the example.
- **Ask** before what leaves the machine: `git push`, opening and merging PRs.
- **Hooks**, built from the commands found in step 2, with `"$CLAUDE_PROJECT_DIR"` paths:
  - `PostToolUse` on `Edit|Write`: the formatter for the edited file only (`ruff format <file>`,
    `prettier --write <file>`), exiting 0 for other file types. Only if the project has a formatter.
  - `Stop`: the fastest check that matters (lint or typecheck, not the full suite: it runs at the end
    of every turn), output to stderr, `exit 2` on failure. Run it once first: if it fails today, don't
    add the hook (it would send every turn back to pre-existing failures) and list it for the user instead.
- **Plugins**: keep `geostack@dampe` and its marketplace, so teammates and cloud sessions get geostack.
- Leave out what a project file can't or shouldn't set: `defaultMode: "auto"` and `autoMode` are ignored
  there, and personal choices (`statusLine`, `model`, sandbox paths for one machine) belong in user
  settings or `.claude/settings.local.json`.
- Keep the enforced set small: a rule with exceptions belongs in `CLAUDE.md`, not in a hook or deny rule.

Add `CLAUDE.local.md` and `.claude/settings.local.json` to `.gitignore` if they are missing.

Show the user the resulting files, or the added parts for existing ones, followed by a list of the
placeholders left in `CLAUDE.md`: `<decide in /grill-with-docs>` ones for the first grill, and facts you
couldn't find for the user to fill in. Don't commit.

### 6. Hand off

Tell the user what comes next:

1. Review `CLAUDE.md` and `.claude/settings.json` and commit them. Deny and ask rules apply at once;
   the marketplace and plugins wait until each teammate trusts the folder.
2. If `## Agent skills` is missing, run `/setup-matt-pocock-skills`: issue tracker, triage labels,
   `CONTEXT.md` and ADR layout.
3. Don't create `CONTEXT.md` or `docs/adr/` by hand: the first `/grill-with-docs` creates them, and
   that is also where the `<decide in /grill-with-docs>` placeholders get settled.

Running this skill again later is safe: it only fills what is missing.

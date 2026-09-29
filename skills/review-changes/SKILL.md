---
name: review-changes
description: Use when a change is finished and should be reviewed before commit, merge or PR - the user says "review", "zrób review", "sprawdź zmiany", or an implementation task just completed. Routes the diff to the right specialist reviewers in parallel and consolidates their findings.
argument-hint: "[base-branch]"
---

# Review changes

## 1. Scope

```bash
git status --short
git diff --stat ${ARGUMENTS:-main}...HEAD
git diff --stat            # unstaged
git diff --cached --stat   # staged
```

If there is nothing to review, say so and stop.

## 2. Route by changed files

| Reviewer | Dispatch when the diff touches |
|---|---|
| `devkit:code-reviewer` | always |
| `devkit:security-reviewer` | auth, permissions, views/endpoints, serializers, file upload/parsing, subprocess, templates, settings, secrets, CORS/CSRF, dependency manifests, CI workflows, frontend auth/token handling, rendering of user-generated HTML |
| `devkit:postgres-reviewer` | models, migrations, `*.sql`, ORM-heavy code (querysets, `annotate`, raw SQL), spatial queries |
| `devkit:platform-reviewer` | Dockerfile, compose, k8s/Helm/Kustomize/ArgoCD, CI pipelines, deploy scripts |
| `devkit:frontend-reviewer` | `*.tsx`/`*.ts`/`*.jsx`, frontend build config (`vite.config.*`, `tsconfig*`, `package.json`), generated API client, map components |

Dispatch all selected reviewers **in one message** (parallel). Give each one:
- the base ref and the list of files relevant to its lens
- the intent of the change in 1–3 sentences (from the conversation, commits or the task brief)
- known constraints (e.g. "table `observations` has ~40M rows", "runs on arm64 Pi")

Change is tiny (≤20 lines, one file, no security/DB/infra surface)? Review it yourself
with the review-standards skill instead of dispatching.

## 3. Consolidate

1. Merge duplicates. When reviewers disagree on severity, keep the higher one and note why.
2. For every critical/high finding, open the cited location and confirm it yourself.
   Drop any you cannot confirm, and say that you dropped them.
3. Present:
   - the overall verdict (`ship` / `ship after fixes` / `needs rework`)
   - findings by severity, each tagged with its source reviewer
   - what was covered (which reviewers ran, on which files)
4. If reviewers flagged a missing ADR, offer to write it with the adr skill.
5. Ask whether to fix. Don't start fixing automatically.

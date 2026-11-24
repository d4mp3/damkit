---
name: review-changes
description: Use after /code-review, or when the user asks for a risk, security, database, infrastructure or frontend review of a diff - "sprawdź ryzyko", "security review", "oceń migrację". Routes the diff to damstack's specialist reviewers in parallel and reports a separate Risk axis next to /code-review's Standards and Spec.
argument-hint: "[fixed-point]"
---

# Review changes: the Risk axis

`/code-review` already covers **Standards** (documented conventions + code smells) and **Spec**
(does the diff do what the ticket asked). This skill adds a third, separate axis, **Risk**: what
breaks in production — wrong behavior, regressions, security holes, locking migrations, failed
deploys, broken UI states. Don't repeat Standards or Spec findings, and don't merge the axes.

## 1. Scope

Use the same fixed point as the `/code-review` that ran before this, else the argument, else
the default branch.

```bash
git rev-parse ${ARGUMENTS:-main}
git diff --stat ${ARGUMENTS:-main}...HEAD
git diff --stat            # unstaged
git diff --cached --stat   # staged
```

If there is nothing to review, say so and stop.

## 2. Intent

Reviewers need the intent in 1–3 sentences. Take it, in this order, from: the ticket or spec
referenced in the commits or the conversation (fetch it as `docs/agents/issue-tracker.md`
describes), the commit messages, the conversation. `/implement` runs in a fresh context, so
the ticket is usually the only reliable source.

## 3. Route by changed files

| Reviewer | Dispatch when the diff touches |
|---|---|
| `damstack:code-reviewer` | always (correctness, regressions, test gaps, doc drift) |
| `damstack:security-reviewer` | auth, permissions, views/endpoints, serializers, file upload/parsing, subprocess, templates, settings, secrets, CORS/CSRF, dependency manifests, CI workflows, frontend auth/token handling, rendering of user-generated HTML |
| `damstack:postgres-reviewer` | models, migrations, `*.sql`, ORM-heavy code (querysets, `annotate`, raw SQL), spatial queries |
| `damstack:platform-reviewer` | Dockerfile, compose, k8s/Helm/Kustomize/ArgoCD, CI pipelines, deploy scripts |
| `damstack:frontend-reviewer` | `*.tsx`/`*.ts`/`*.jsx`, frontend build config (`vite.config.*`, `tsconfig*`, `package.json`), generated API client, map components |

Dispatch all selected reviewers **in one message** (parallel). Give each one:
- the fixed point and the list of files relevant to its lens
- the intent from step 2, and the ticket's acceptance criteria when there is one
- known constraints (e.g. "table `observations` has ~40M rows", "runs on arm64 Pi")
- the path to `CONTEXT.md` if it exists, so finding titles use the project's terms

Change is tiny (≤20 lines, one file, no security/DB/infra surface)? Review it yourself
with the review-standards skill instead of dispatching.

## 4. Consolidate

1. Merge duplicates across reviewers. When they disagree on severity, keep the higher one and note why.
2. For every critical/high finding, open the cited location and confirm it yourself.
   Drop any you cannot confirm, and say that you dropped them.
3. Present it under a `## Risk` heading, after `## Standards` and `## Spec` if `/code-review` ran:
   - the verdict (`ship` / `ship after fixes` / `needs rework`)
   - findings by severity, each tagged with its source reviewer
   - what was covered (which reviewers ran, on which files)
4. If reviewers flagged a missing ADR or a glossary term the diff changed, offer to record it
   with the domain-modeling skill.
5. Ask whether to fix. Don't start fixing automatically.

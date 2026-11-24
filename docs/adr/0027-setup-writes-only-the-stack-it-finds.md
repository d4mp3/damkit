# ADR-0027: setup-damkit asks for the stack and writes only the sections it needs

- Status: Accepted (refines [ADR-0019](0019-setup-damkit-writes-project-claude-md.md) and [ADR-0024](0024-setup-writes-project-settings.md))
- Date: 2026-11-16

## Context

damkit covers a whole stack (Django or FastAPI, React, PostGIS, maps, containers, Kubernetes, GitOps),
but most projects use only part of it. `setup-damkit` dropped `## Frontend`, `## Data & GIS` and
`## Deployment` only when the repo showed they didn't apply. In a fresh repo nothing showed that, so
the project's `CLAUDE.md` got every section, with placeholders for layers it would never have. The
template's commands were real uv and pnpm lines rather than placeholders, and the review-changes rule
always named Docker, k8s and frontend. Every line of `CLAUDE.md` is loaded on every turn, so that
noise cost context and pointed the model at a stack the project doesn't use.

## Decision

- Step 2 classifies each layer (backend, database, spatial data, frontend and map, design system,
  QGIS plugin, images, Kubernetes or GitOps, CI) as shown, ruled out or unclear, from code, manifests
  and dependencies.
- When any layer is unclear, step 3 asks about the stack first, on its own: every layer in a fresh
  repo, only the unclear ones otherwise. A layer is in the project, planned with its technology still
  undecided (`<decide in /grill-with-docs>`), or not in the project, in which case its sections, lines
  and questions are left out.
- The template marks its conditional sections and lines with `when:` comments. Its commands are
  placeholders with examples, and the review-changes rule names only the project's risk areas.
- The final summary names the layers left out, so a rerun can add one when it arrives.

## Alternatives considered

- **A template per stack**: the combinations multiply, and the shared parts (`## Workflow`,
  `## Language`) would be copied between them (ADR-0010).
- **Write every section and let the user delete**: the noise this ADR removes, and the user can't
  easily tell which placeholders matter.
- **Infer the stack from the README or the project name only**: plans in prose aren't facts, and a
  wrong guess writes sections nobody fills in.

## Consequences

- A fresh project's setup has one extra question round before the language questions.
- Skills that read a section the project doesn't have (`## Data & GIS`, `## Deployment`) already ask
  instead of assuming, so a missing section is safe.
- Adding a section to the template now also means giving it a `when:` comment.

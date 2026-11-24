# ADR-0028: The plugin is renamed from geostack to damkit

- Status: Accepted (supersedes [ADR-0021](0021-rename-to-geostack.md))
- Date: 2026-11-24

## Context

ADR-0021 named the plugin after spatial data and maps. Most of what it carries is not spatial: the
Matt Pocock companion workflow, role-based agents, Risk-axis reviewers, Django/React/Kubernetes
knowledge and the project setup. The `geo` prefix promises a GIS tool and undersells the rest.

A first version of this decision renamed the plugin to damstack. It was published the same day and
replaced before any project used it: "stack" promised a framework rather than a kit of agents and skills.

## Decision

- The plugin is called **damkit**: `/damkit:…` skills, `damkit:…` agents, `PLUGIN_PREFIX` in the
  read-only guard, and the `setup-damkit` skill. The marketplace stays `dampe`.
- The GitHub repository becomes `d4mp3/damkit`.
- ADRs 0001–0027 use the name damkit too, so a reader doesn't have to map old names to the current
  plugin. Only ADR-0021 and this ADR keep the earlier names (devkit, geostack, damstack), because
  they record the renames.

## Alternatives considered

- **Keep geostack**: ties the name to one part of the stack.
- **damstack**: briefly used; see Context.
- **Keep the old names in ADRs 0001–0027**: faithful to when they were written, but every reader
  has to know three names for one plugin.

## Consequences

- Projects with the plugin installed must switch `geostack@dampe` (or `damstack@dampe`) to
  `damkit@dampe` and the marketplace repo to `d4mp3/damkit` in `.claude/settings.json`, and
  `/geostack:…` to `/damkit:…` in the `## Workflow` section of `CLAUDE.md` (running
  `/damkit:setup-damkit` again does not rewrite existing sections).
- Until the GitHub repository is renamed, `claude plugin marketplace add d4mp3/damkit` fails;
  after the rename GitHub redirects the old name, so existing marketplace entries keep updating.

# ADR-0028: The plugin is renamed from geostack to damstack

- Status: Accepted (supersedes [ADR-0021](0021-rename-to-geostack.md))
- Date: 2026-11-24

## Context

ADR-0021 named the plugin after spatial data and maps. Most of what it carries is not spatial: the
Matt Pocock companion workflow, role-based agents, Risk-axis reviewers, Django/React/Kubernetes
knowledge and the project setup. The `geo` prefix promises a GIS tool and undersells the rest.

## Decision

- The plugin is called **damstack**: `/damstack:…` skills, `damstack:…` agents, `PLUGIN_PREFIX` in the
  read-only guard, and the `setup-damstack` skill. The marketplace stays `dampe`.
- The GitHub repository becomes `d4mp3/damstack`.
- ADRs 0001–0027 keep the names they were written under (devkit, geostack).

## Alternatives considered

- **Keep geostack**: ties the name to one part of the stack.

## Consequences

- Projects with the plugin installed must switch `geostack@dampe` to `damstack@dampe` and the
  marketplace repo `d4mp3/geostack` to `d4mp3/damstack` in `.claude/settings.json`, and `/geostack:…`
  to `/damstack:…` in the `## Workflow` section of `CLAUDE.md` (running `/damstack:setup-damstack`
  again does not rewrite existing sections).
- Until the GitHub repository is renamed, `claude plugin marketplace add d4mp3/damstack` fails;
  after the rename GitHub redirects the old name, so existing marketplace entries keep updating.

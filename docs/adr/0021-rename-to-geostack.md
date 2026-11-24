# ADR-0021: The plugin is renamed from devkit to geostack

- Status: Superseded by [ADR-0028](0028-rename-to-damkit.md)
- Date: 2026-11-16

## Context

"devkit" says nothing about who the plugin is for, and the repository is going public. After ADR-0020
the plugin no longer assumes a domain or a country; what sets it apart is spatial data and maps on a
Python/React/PostGIS/Kubernetes stack. The name is also a prefix typed every day (`/devkit:review-changes`),
so it should stay short.

## Decision

- The plugin is called **geostack**: `/geostack:…` skills, `geostack:…` agents, `PLUGIN_PREFIX` in the
  read-only guard, and the `setup-geostack` skill. The marketplace stays `dampe`.
- The GitHub repository becomes `d4mp3/geostack`.
- ADRs 0001–0020 keep the name devkit: they record decisions made under it.

## Alternatives considered

- **Keep devkit**: generic, and unfindable among many plugins with the same idea.
- **A domain name such as canopy or grove**: ties the plugin to forestry, which ADR-0020 made an example only.
- **gisops**: suggests a deployment tool rather than a whole-stack companion.

## Consequences

- Projects with the plugin installed must switch `devkit@dampe` to `geostack@dampe` in
  `.claude/settings.json` and `/devkit:…` to `/geostack:…` in the `## Workflow` section of `CLAUDE.md`
  (running `/geostack:setup-geostack` again does not rewrite existing sections).
- The name is close to the unrelated gstack skill pack; the `geo` prefix keeps them apart.

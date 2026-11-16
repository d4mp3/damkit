# ADR-0020: devkit serves any GIS project; domain, region and CRS come from the project

- Status: Accepted (extends [ADR-0019](0019-setup-devkit-writes-project-claude-md.md) from languages to domain and region)
- Date: 2026-11-16

## Context

devkit grew out of my projects: a forestry platform, a geodata validator, a k3s homelab, all with data
in Poland. ADR-0019 stopped skills from assuming Polish UI copy, but my context still leaked into
behavior in other places:
- the starter `tokens.css`, which is copied into projects, named its accent palette `--forest-*`;
- `mentor` listed my projects as the mission for every user;
- `postgres-postgis`, `web-maps` and the project template treated EPSG:2180 and Polish map services
  as the default, which is wrong for a GIS specialist anywhere else.

## Decision

- devkit is for any GIS specialist on this stack. Skills don't assume a domain, a country or a CRS.
- The storage CRS comes from `## Data & GIS` in the project's `CLAUDE.md` or its ADR. `setup-devkit`
  reads it from the SRID of existing geometry columns; otherwise it stays a question for `/grill-with-docs`.
- EPSG:2180, Geoportal, BDL and forestry stay as **examples**, named next to other national grids
  (27700, 25832/25833, UTM) where a choice is described.
- The starter tokens use a neutral `--brand-*` name. `mentor` takes the mission from `## What this is`
  and `## Learning goals`.

## Alternatives considered

- **Strip all forestry and Polish examples**: one consistent running example reads better than
  several invented ones, and it is clearly an illustration once nothing depends on it.
- **A per-country reference file in `postgres-postgis`**: knowledge the model already has (ADR-0014).

## Consequences

- Examples in README, `docs/` and hook tests (`forest-web`) stay as they are.
- ADR-0001 and ADR-0007 still name my projects; they record why devkit was built.
- A project without `## Data & GIS` gets asked about its CRS instead of silently getting 2180.

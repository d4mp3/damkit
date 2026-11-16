# ADR-0022: QGIS plugins are in scope, as one knowledge skill

- Status: Accepted
- Date: 2026-11-16

## Context

geostack covered the web side of GIS work (Django/FastAPI, PostGIS, web maps, validators, Kubernetes),
but GIS specialists also write QGIS plugins and PyQGIS scripts, often as the desktop client of the
same services. The model knows PyQGIS, yet it is costly in a few places: touching the GUI or project
layers from a background thread crashes QGIS without a traceback, `unload()` leaks surface only after a
reload, and the QGIS 4 (Qt6) migration rules changed after the model's training (`supportsQt6` was
dropped in favour of `qgisMaximumVersion`).

## Decision

- Add a `qgis-plugins` knowledge skill, triggered by description (no `paths`: `metadata.txt` and
  `.py` files don't justify loading the whole body on every match).
- It holds only what passes ADR-0014: threading rules, a Processing-first structure, using QGIS's
  network, auth and transform machinery, headless testing, publishing constraints, and a bridge to
  `geospatial-validation`'s error contract.
- The QGIS 4 migration lives in `references/qgis4-migration.md`, dated and pointing to the official
  guide, because it is the part most likely to change.

## Alternatives considered

- **A `qgis-expert` agent**: ruled out by ADR-0002. It would lose the conversation context and adds no
  isolation, permissions or parallelism.
- **A section in `geospatial-validation`**: plugins aren't always validators, and the section would load
  for every validator task.
- **A plugin scaffold in `assets/`**: Plugin Builder and `qgis-plugin-ci` already generate one
  (ADR-0010). The decisions fit in prose.

## Consequences

- Plugin work gets the same treatment as web work: ADRs and `CONTEXT.md` in the plugin's repo override
  the skill's defaults.
- The migration reference has to be re-checked as QGIS 4 matures. Its date says when it was last verified.

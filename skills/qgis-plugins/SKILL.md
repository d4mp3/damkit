---
name: qgis-plugins
description: Use when writing, testing, packaging or porting QGIS plugins or PyQGIS scripts - metadata.txt, Processing algorithms and providers, QgsTask and background work, dock widgets, map tools, plugin unload/reload, testing PyQGIS in CI, publishing to plugins.qgis.org, QGIS 3 to QGIS 4 (Qt6) migration, a crash or freeze inside QGIS.
---

# QGIS plugins

The project's ADRs and `CONTEXT.md` win over this file. The structure below is a default to propose
while grilling, not a fact.

## Threads: the rule that crashes QGIS

A mistake here doesn't raise a traceback: QGIS segfaults or freezes, often only on the user's machine.

- GUI, `iface`, the map canvas and layers from `QgsProject` belong to the **main thread**. Never touch
  them from `QgsTask.run()`, a Processing algorithm or a `QThread`.
- Long work goes into a `QgsTask` added to `QgsApplication.taskManager()`. Keep a reference to the task
  (`self._task = task`): a task that only a local variable holds gets garbage-collected while running.
- In `run()`: no GUI and no `iface.messageBar()`. Report with `setProgress()`, check `isCanceled()`
  in loops, log with `QgsMessageLog`, and return `bool`. Results go to the UI in `finished()`, which runs
  on the main thread.
- A layer needed in a task: create a `QgsVectorLayerFeatureSource(layer)` on the main thread and iterate
  it in the task, or open a new layer from `layer.source()` inside the task. Never pass the project's
  layer object across.
- Processing algorithms run in a background thread. One that must touch the GUI or the project declares
  the no-threading flag in `flags()` instead of hoping.

## Structure

- Put the work in a **Processing algorithm** with its own provider, registered in `initProcessing()`.
  The plugin's dialog or button calls it (`processing.execAlgorithmDialog` / `processing.run`). Then it
  runs headless in tests, from `qgis_process` in CI or scripts, in the model designer and as a batch,
  for free.
- Keep domain logic that doesn't need PyQGIS (rules, parsing, calculations) in modules without `qgis`
  imports: those are tested with plain pytest, no QGIS needed.
- `unload()` removes everything `initGui()` added: actions, menu entries, toolbar icons, dock widgets,
  the Processing provider, map tools, and signal connections to `iface`, `QgsProject` or layers.
  A leftover connection calls into a deleted object after a reload and crashes QGIS. Test with
  Plugin Reloader: a duplicated menu entry means `unload()` leaks.
- Icons and UI files by path relative to `__file__`, not a compiled `resources.py`: PyQt6 has no
  `pyrcc`, so Plugin Builder's resource file is a QGIS 4 blocker.

## Inside QGIS, use QGIS's machinery

- Network: `QgsNetworkAccessManager` / `QgsBlockingNetworkRequest`, not `requests`. They honor the
  proxy, SSL and auth settings the user configured in QGIS, which corporate and government networks need.
- Credentials: an `authcfg` id from `QgsAuthManager`, never a password in `QSettings` or the project file.
- CRS transforms: `QgsCoordinateTransform(src, dst, QgsProject.instance().transformContext())`, not pyproj.
  The context carries the datum transformations the user chose.
- Settings: `QgsSettings` under the plugin's own prefix. Strings shown to users: `self.tr()` with
  `.format()` placeholders, because `pylupdate` can't extract f-strings.

## Dependencies

- PyQGIS is not on PyPI. A local venv needs `--system-site-packages` on top of the QGIS Python, or
  imports fail with `No module named 'qgis'`.
- `metadata.txt` can't install Python packages (`plugin_dependencies` names other QGIS plugins only).
  Prefer the standard library plus what every QGIS install ships (GDAL/OGR, numpy). For a pure-Python
  extra, vendor it inside the plugin. Never run `pip` from the plugin: OSGeo4W, the macOS bundle and
  Flatpak each break differently.

## Testing

- Headless QGIS: the `qgis/qgis` image (it includes xvfb) or `QT_QPA_PLATFORM=offscreen`.
  `pytest-qgis` provides `qgis_app`, `qgis_iface` and `qgis_processing` fixtures. Without the last one
  (or `Processing.initialize()`), `processing.run` fails in tests.
- Test the algorithm through `processing.run("provider:algorithm", params)` on tiny layers built in
  the test (memory layers or a temporary GeoPackage), not committed data.
- A plugin supporting QGIS 3 and 4 runs CI on both: one job per image tag.

## QGIS 4 (Qt6)

Read [references/qgis4-migration.md](references/qgis4-migration.md) before porting a plugin or setting
`qgisMaximumVersion`. In new code use `qgis.PyQt` imports and scoped enums from the start.

## Packaging and publishing

- The zip's top folder is the plugin's module name. Exclude `.git`, `__pycache__`, tests and dev files.
- plugins.qgis.org expects a GPL-compatible license, and `repository` and `tracker` in `metadata.txt`.
  A plugin imports PyQGIS (GPL), so check the license before the first upload, not after.
- `qgis-plugin-ci` builds the zip from a git tag, compiles translations and uploads to the repository.
  Propose it as the release step. Record the choice in an ADR if the project takes it.

## Bridge to the project's services

When the plugin is a client of the project's validator or API, reuse its contracts:
- Load validation findings (the error FeatureCollection from `geospatial-validation`) as a layer with
  a QML style shipped in the plugin, and zoom to a finding by `feature_key`.
- Generate the client from the same OpenAPI schema as the web frontend, or at least test the plugin
  against it, so the plugin and the web app don't drift.

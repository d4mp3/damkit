# QGIS 3 → QGIS 4 (Qt6) migration

Checked against the official guide on 2026-11-16. This changes fast: before relying on a detail, check
<https://plugins.qgis.org/docs/migrate-qgis4> and the QGIS wiki page "Plugin migration to be
compatible with Qt5 and Qt6" (via `docs-researcher` when available).

## metadata.txt

- `supportsQt6` is gone: QGIS core no longer recognises it. Delete the line.
- QGIS 4 compatibility comes only from the version range:
  - QGIS 3 and 4: keep `qgisMinimumVersion=3.xx` and add `qgisMaximumVersion=4.99`.
  - QGIS 4 only: `qgisMinimumVersion=4.0`.
  - Without `qgisMaximumVersion`, the range ends with the major version of `qgisMinimumVersion`, so a
    QGIS 3 plugin is not loaded by QGIS 4.
- Set the range only after the plugin has run on a QGIS 4 build.

## Code

- Import only from `qgis.PyQt.*`, never `PyQt5`/`PyQt6`. One codebase then runs on both.
- Scoped enums everywhere, for both Qt and QGIS:
  `Qt.ItemDataRole.UserRole`, `Qt.GlobalColor.blue`, `QMessageBox.StandardButton.Ok`,
  `Qgis.MessageLevel.Success`, `QgsWkbTypes.GeometryType.PolygonGeometry`,
  `QgsMapLayer.LayerType.VectorLayer`. PyQt6 doesn't coerce raw ints either: `sort(0, 1)` becomes
  `sort(0, Qt.SortOrder.DescendingOrder)`, including in test mocks. Scoped forms work on recent QGIS 3
  releases too; check them against the plugin's `qgisMinimumVersion`.
- `exec_()` → `exec()`.
- `QRegExp` → `QRegularExpression` (`setFilterRegularExpression()`, `regex.match(s).hasMatch()`).
- `QAction` moved from QtWidgets to QtGui: let the converter script rewrite the import.
- No `pyrcc` in PyQt6: replace a compiled `resources.py` with icon paths relative to `__file__`.
- Qt6 has no webp image plugin: `QPixmap` on a webp file returns a null pixmap without an error.

## Tools

- `scripts/pyqt5_to_pyqt6/pyqt5_to_pyqt6.py` in the QGIS repo rewrites most of the above. Expect
  manual fixes afterwards.
- The checker image runs the same script without changing files:

  ```bash
  docker run --rm --pull always --user "$(id -u):$(id -g)" \
    -v "$(pwd):/workspace/" --workdir /workspace/ \
    ghcr.io/qgis/pyqgis4-checker:main-ubuntu \
    pyqt5_to_pyqt6.py --dry_run --logfile /workspace/pyqt6_checker.log .
  ```

  `--dry_run` exits 0 even with findings, so a CI job must fail on the log content
  (a `file.py:line:col` entry), not on the exit code.
- plugins.qgis.org runs the checker on upload. Results are in the version's "Qt6 Check" tab. The guide
  calls it informational, but plugin authors report uploads blocked by unscoped enums: fix them first.

## CI on the QGIS 4 image

- The image is Debian Trixie based: PEP 668 makes `pip install` fail without
  `--break-system-packages` (or a venv with `--system-site-packages`). Pass the flag only in the QGIS 4
  job, because the older pip in QGIS 3 images rejects it.
- Don't upgrade `pip`/`wheel` in that image: Debian's `wheel` can't be uninstalled by pip.

---
name: geospatial-validation
description: Use when building or changing tools that validate geospatial data - GeoPackage/Shapefile/GeoJSON/FlatGeobuf/GeoParquet inputs, geometry validity, CRS checks, topology rules, YAML-defined validation rules, immutability/change detection between dataset versions, reporting errors per layer and feature, or serving validation results through an API or on a map.
---

# Geospatial data validation

## Principles

1. **The validator never mutates input.** Open read-only (pyogrio/fiona read mode,
   `gdal.OpenEx(..., gdal.OF_READONLY)`). Tests assert that the input file checksum is
   unchanged after a run.
2. **Every error is locatable.** A finding without layer + feature key + location is useless for
   the user who has to fix it in QGIS.
3. **Rules are data.** Rules are defined in YAML, validated against a schema, and have stable
   IDs, so reports stay comparable across versions.

## Error record contract

Use one shape in the CLI JSON output, the web service API and the map layer:

```json
{
  "rule_id": "geom.valid",
  "severity": "error",
  "layer": "wydzielenia",
  "feature_key": "12-34-5-67-a",
  "fid": 1832,
  "message": "Self-intersection",
  "location": {"type": "Point", "coordinates": [512034.2, 301877.9]},
  "crs": "EPSG:2180"
}
```

- `feature_key` = a business key from the attributes (stable). `fid` is only a hint: it changes
  between exports and formats.
- `location` = the error point when known (`shapely.is_valid_reason` returns coordinates);
  else the feature's representative point (`shapely.point_on_surface`, never the centroid,
  which can fall outside the polygon).
- Output a FeatureCollection of errors as well, so the web service can draw them on the map directly
  (rendering patterns: the web-maps skill).
- CLI exit codes: `0` valid, `1` validation errors found, `2` usage/config/IO error. CI depends on this.

## Rule categories (check in this order and short-circuit)

1. **Container/schema:** file opens, the expected layers exist, fields and types match, encoding is correct.
2. **CRS:** present and equal to the expected EPSG. Don't guess a missing `.prj`. Report it.
3. **Geometry:** not null or empty, expected type (Polygon vs MultiPolygon), dimensions (Z/M),
   `is_valid`, and a minimum area/length for slivers.
4. **Topology** (same layer): no overlaps or gaps. Use `shapely.STRtree` for candidate pairs.
   Never use O(n²) loops.
5. **Cross-layer:** containment in a parent layer, referential integrity of keys.
6. **Attributes:** domains/dictionaries, required fields, regex, ranges.

## Immutability / change detection

For "these features must not change between dataset versions":

- Match features by `feature_key`, never by fid or row order.
- Geometry fingerprint: `shapely.normalize(g)` → `shapely.set_precision(g, grid)` →
  WKB → sha256. The grid (e.g. 0.01 m in EPSG:2180) absorbs float noise from re-exports.
  Without it every re-export looks like a change.
- Attribute fingerprint: canonical JSON of the selected immutable fields (sorted keys,
  normalized types: `"1"` vs `1`, dates to ISO).
- Report `added` / `removed` / `geometry_changed` / `attributes_changed` per key, in the same error contract.
- Store the baseline as a manifest (key → hashes) next to the data or in the DB. The CLI can then check without the old file.

## YAML rules

- `yaml.safe_load` only. Parse into Pydantic models, which give you errors with the field path.
- Export a JSON Schema from the models. Editors (yaml-language-server) then autocomplete
  rule files via `# yaml-language-server: $schema=...`.
- Report config errors with file:line. `ruamel.yaml` keeps line numbers.

## Libraries

- Reading: **pyogrio** (fast, Arrow) > fiona. Use geopandas for convenience on moderate sizes.
- Geometry: **shapely 2.x** vectorized functions (`shapely.is_valid(arr)`), not per-feature loops.
- CRS: pyproj with `always_xy=True`.
- `ogrinfo -json -so file.gpkg` for a quick inspection while debugging.
- Large files: iterate in batches (`pyogrio.read_arrow` / `skip_features`+`max_features`) and
  keep memory bounded. The web service runs this in a worker, not in the request handler.

## Format gotchas

- Shapefile: 10-char field names, no real NULLs in DBF, a 2 GB limit, and a separate `.cpg` for encoding.
- GeoJSON (RFC 7946): WGS84 only, and polygons follow the right-hand rule. A "crs" member is non-standard.
- GeoPackage: multiple layers plus non-spatial tables. Layer names are case-sensitive in some tools.

## Tests

Generate tiny fixtures in code (a bowtie polygon, overlapping squares, a missing CRS, a wrong type)
rather than committing large files. Keep one golden-report test per rule.

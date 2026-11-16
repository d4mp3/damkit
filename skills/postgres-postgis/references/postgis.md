# PostGIS reference

## geometry vs geography

- `geometry` in a projected CRS: fast, precise for a regional extent, and the full function set.
  The default choice for data within one country or region (the project's storage CRS, e.g. EPSG:2180).
- `geography`: correct distances on the sphere for global data, but slower and fewer functions.
  Good for "points within X meters" over worldwide data.
- Casting on the fly (`geom::geography`) in WHERE kills the index unless there is an expression index.

## Spatial join pattern

```sql
SELECT a.id, b.id
FROM parcels a
JOIN forest_units b ON ST_Intersects(a.geom, b.geom)   -- uses GiST on both sides
WHERE a.geom && ST_MakeEnvelope(:xmin, :ymin, :xmax, :ymax, 2180);  -- the column's SRID
```

- `ST_Intersects` / `ST_Contains` / `ST_Within` / `ST_DWithin` use the index automatically.
  `ST_Relate` with a custom pattern does not do a bbox pre-filter in every version, so add `&&`.
- `ST_Intersection` (computes geometry) is expensive. Filter with `ST_Intersects` first.
- Area/length in a metric CRS: `ST_Area(geom)` on a metric CRS such as 2180 gives m². On 4326 it gives meaningless "square degrees".

## Indexes

- `CREATE INDEX CONCURRENTLY idx ON t USING gist (geom);`
- SP-GiST can beat GiST for points. Measure before switching.
- Physical ordering helps range scans: `CLUSTER t USING idx` (locks!) or load data sorted by
  `ST_GeoHash(ST_Transform(geom, 4326))`.

## Validity and precision

- `ST_IsValidReason(geom)` returns the reason and location, e.g. `Self-intersection[x y]`.
- `ST_MakeValid(geom, 'method=structure')` (GEOS 3.10+) keeps polygons as polygons more often.
- Snapping/precision: `ST_ReducePrecision` (GEOS 3.9+) for sliver cleanup. `ST_SnapToGrid` is the older way.
- Enforce types: `CHECK (ST_IsValid(geom))` is expensive on writes. Consider validating in the pipeline instead.

## Axis order

EPSG:4326 is officially lat/lon. Most GIS software and PostGIS use lon/lat (x/y). GDAL 3+ honors
authority order unless `OAMS_TRADITIONAL_GIS_ORDER` / `always_xy=True` (pyproj) is set.
Swapped coordinates are the most common "data in the ocean" bug.

## Vector tiles

`ST_AsMVT` + `ST_AsMVTGeom(ST_Transform(geom, 3857), ST_TileEnvelope(z, x, y))`. Serve with
a thin endpoint or pg_tileserv/Martin. Simplify per zoom level and cache aggressively.

## GeoDjango mapping

- `PolygonField(srid=2180)` (the project's storage SRID) keeps the column SRID explicit.
- `filter(geom__intersects=g)`, `filter(geom__dwithin=(pt, D(m=100)))` (metric SRID or geography only).
- `Transform` in annotations runs in the DB. Prefer it to transforming in Python.
- `GEOSGeometry` operations run in Python. Don't loop over 100k rows doing them. Push them to SQL.

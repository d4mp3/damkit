---
name: web-maps
description: Use when building or debugging interactive web maps in a React/TypeScript frontend - MapLibre GL JS, OpenLayers or Leaflet, vector tiles (MVT) from PostGIS, large GeoJSON layers, data in a national grid or other non-Mercator CRS (e.g. EPSG:2180, EPSG:27700) on a web map, national WMS/WMTS services (e.g. Polish Geoportal, BDL), map performance, syncing map state with URL and React state, showing validation errors on a map.
---

# Web maps

## Pick the library by requirements

| Need | Choice |
|---|---|
| Fast vector tiles, smooth zoom, data-driven styling, 3D terrain | **MapLibre GL JS** (react-map-gl/maplibre wrapper) |
| **Native non-Mercator projections** (national grids such as EPSG:2180 or 27700), WMS/WMTS published in them, heavy GIS tooling (editing, measuring) | **OpenLayers** |
| Simple markers and popups on raster tiles | Leaflet (react-leaflet) |

MapLibre renders **only Web Mercator (EPSG:3857)**. Data stored in the project's projected CRS
(`## Data & GIS` in `CLAUDE.md`) must be served reprojected (PostGIS `ST_Transform(geom, 3857)` in
`ST_AsMVT` or 4326 GeoJSON). National WMTS services published only in their own grid (e.g. the
Polish Geoportal in EPSG:2180) need OpenLayers + `proj4` registration. The example registers 2180;
take the definition for your CRS from epsg.io:

```ts
import proj4 from "proj4";
import { register } from "ol/proj/proj4";
proj4.defs("EPSG:2180",
  "+proj=tmerc +lat_0=0 +lon_0=19 +k=0.9993 +x_0=500000 +y_0=-5300000 +ellps=GRS80 +units=m +no_defs");
register(proj4);
```

Coordinates in the storage CRS, 4326 and 3857 share one TypeScript type (`[number, number]`). Where more
than one CRS lives in the client, brand them so a missing transform fails at compile time:
e.g. `type Xy2180 = [number, number] & { readonly __crs: "EPSG:2180" }`.

## Data volume decides the transport

| Features in view | Transport |
|---|---|
| < ~5k simple features | GeoJSON from the API (bbox-filtered, simplified) |
| 5k – millions | **Vector tiles (MVT)** from PostGIS (`ST_AsMVT`) via Martin / pg_tileserv / a FastAPI endpoint, cached behind a CDN or nginx |
| Static large dataset | PMTiles file on object storage (no tile server) |

Always filter by the current bbox and zoom. Never ship a whole forest-district layer as one GeoJSON.

## Map instance and React

- The map is an **external system**. Create it once in an effect (or use the wrapper), keep it in a ref,
  and destroy it on unmount. Don't recreate it on every render.
- Update sources and layers imperatively (`map.getSource(id).setData(...)`, `setPaintProperty`)
  rather than remounting layers from props on each render.
- Map view state (center, zoom, active layers, filters) lives in the URL so views are shareable.
  Debounce URL writes on `moveend`.
- Fetch data for the view with TanStack Query keyed by `[layer, bbox rounded, zoom]` and an AbortSignal,
  so panning cancels stale requests.

## Performance

- Styling by data expressions (`["match", ["get", "species"], ...]`) on the GPU. Don't loop features in JS.
- Simplify per zoom on the server (`ST_SimplifyPreserveTopology` / `ST_AsMVTGeom` extent).
- Clustering for dense points (built into MapLibre sources: `cluster: true`).
- Heavy client-side geometry (turf) on large sets goes to a Web Worker.

## Showing validation errors (a validation web service)

Use the error contract from the geospatial-validation skill. The service returns errors as a
FeatureCollection with the `location` point per error. Render it as its own source:
- a circle layer colored by `severity`, with clustering at low zoom
- click → popup with `rule_id`, `layer`, `feature_key`, `message`
- the error list and the map share the selection state (click in the list → `flyTo` + highlight)
- the original layer's feature is highlighted via `feature-state`, which needs `promoteId: "feature_key"`

## Attribution and terms

Show the attribution for every base layer (OSM, national geoportals such as Geoportal/GUGiK or BDL). Check the usage limits of public
WMS/WMTS services before putting them behind a busy public site. Cache or proxy if allowed.

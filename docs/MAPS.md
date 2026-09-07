# Map data — Libya Locations v1.2

`v1.2.0` adds optional geospatial companion datasets for Libyan municipalities without changing the stable `v1.1` location record contract.

## Files

| File | Purpose |
| --- | --- |
| `data/municipality-points.json` | All 141 municipalities with nullable latitude/longitude and coordinate provenance |
| `data/municipality-points.csv` | Spreadsheet/database-friendly form of the point dataset |
| `data/municipality-points.geojson` | GeoJSON `Point` features for municipalities with confidently sourced coordinates |
| `data/municipality-boundaries.geojson` | GeoJSON municipality boundary features where a reliable OpenStreetMap relation is matched |
| `data/map-coverage.json` | Exact coverage counts, source counts, and unmatched municipality slugs |
| `data/map-match-candidates.json` | Review-only candidates for currently unmatched municipalities; these are not published as accepted coordinates |

## Coordinate semantics

A published point is a **map reference point**, not automatically the legal centroid or the municipality office.

`point_type` explains what it represents:

- `boundary_representative_point`: a point guaranteed to lie inside a matched administrative polygon;
- `operational_hub`: an operational municipality hub point from the IOM/OCHA ArcGIS source;
- `named_place`: an exact-name GeoNames place/admin record used as a fallback.

If a municipality cannot be matched confidently, `latitude`, `longitude`, and source fields remain `null`. The project intentionally prefers missing data over a guessed location.

## Sources

### OpenStreetMap / Geofabrik

Current OpenStreetMap administrative relations are read from the Libya extract published by Geofabrik. Boundary-derived data must retain the required OpenStreetMap attribution and ODbL notice.

Recommended attribution:

```text
© OpenStreetMap contributors
```

Source page:

```text
https://download.geofabrik.de/africa/libya.html
```

License information:

```text
https://www.openstreetmap.org/copyright
```

### IOM / OCHA operational municipality hubs

The ArcGIS service is an operational dataset based on the 2015 Baladiya election list and revised in 2016. It is used only when an exact municipality name can be matched and should not be interpreted as an official statement of current administrative boundaries.

### GeoNames

GeoNames is used only as an exact-name fallback for point locations. A GeoNames match represents a named-place/admin reference point, not a municipality polygon.

## Stable URLs

For production, pin the release version rather than reading from `master`:

```text
https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.2.0/data/municipality-points.json
https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.2.0/data/municipality-points.geojson
https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.2.0/data/municipality-boundaries.geojson
https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.2.0/data/map-coverage.json
```

## Leaflet

A zero-build browser example is available at [`examples/leaflet-map.html`](../examples/leaflet-map.html).

The same GeoJSON works with MapLibre, Mapbox, Google Maps data layers, Flutter mapping libraries, native iOS/Android GIS libraries, Python GeoPandas, QGIS, and any client that supports standard GeoJSON.

## Production guidance

1. Pin a release such as `v1.2.0`.
2. Cache or bundle the GeoJSON instead of downloading it on every screen load.
3. Use `slug` or `id` to join map data to `data/municipalities.json`.
4. Read `data/map-coverage.json` before assuming every municipality has a published point or polygon.
5. Preserve source attribution when displaying or redistributing OSM-derived map data.
6. Review the changelog before moving to a newer map-data release.

## Boundary limitations

Municipality boundaries in this repository are published only where a matching administrative relation can be verified from the selected source. A missing polygon does **not** mean the municipality does not exist; it means the repository does not currently have a sufficiently reliable boundary geometry for it.

Boundary data can evolve independently of the Ministry's municipality directory, so both source date and coverage must be considered when using it for operational or legal decisions.

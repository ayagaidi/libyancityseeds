# Map data — Libya Locations v1.2

`v1.2.0` adds optional geospatial companion datasets for Libyan municipalities without changing the stable `v1.1` base location record contract.

## v1.2.0 coverage snapshot

- **141** municipality rows are present in the point dataset.
- **103 / 141 (73.05%)** have a confidently sourced map reference point.
- **38** deliberately retain `null` latitude/longitude because no sufficiently confident match is published.
- **10** municipality polygon features are currently published in the boundary GeoJSON.

Coverage is machine-readable in [`data/map-coverage.json`](../data/map-coverage.json).

## Files

| File | Purpose |
| --- | --- |
| `data/municipality-points.json` | All 141 municipalities with nullable latitude/longitude and coordinate provenance |
| `data/municipality-points.csv` | Spreadsheet/database-friendly form of the point dataset |
| `data/municipality-points.geojson` | GeoJSON `Point` features for municipalities with confidently sourced coordinates |
| `data/municipality-boundaries.geojson` | GeoJSON municipality boundary features where a reliable OpenStreetMap relation is matched |
| `data/map-coverage.json` | Exact coverage counts, source counts, and unmatched municipality slugs |
| `data/map-match-candidates.json` | Review-only candidates for currently unmatched municipalities; these are not accepted coordinates |

## Coordinate semantics

A published point is a **map reference point**, not automatically the legal centroid, municipality office, or exact administrative center.

`point_type` explains what a point represents:

- `boundary_representative_point`: a point guaranteed to lie inside a matched OSM administrative polygon;
- `administrative_label_point`: an exact-name OSM `admin_level=4` label/admin point;
- `osm_named_place`: an exact-name OSM place feature such as a city, town, village, hamlet, locality, or municipality feature;
- `operational_hub`: an operational municipality hub point from the IOM/OCHA ArcGIS source;
- `named_place`: an exact-name GeoNames place/admin record used as a fallback.

If a municipality cannot be matched confidently, `latitude`, `longitude`, `coordinate_source`, `coordinate_source_id`, and `point_type` remain `null`. The project intentionally prefers missing data over a guessed location.

## Matching strategy

The map-data build favors deterministic, traceable matching:

1. exact municipality-name matches against the available IOM/OCHA operational hub service;
2. exact-name GeoNames fallback for Libyan place/admin records;
3. current OpenStreetMap Libya extract from Geofabrik;
4. matched `admin_level=4` polygons where available;
5. exact `admin_level=4` administrative label points;
6. exact-name OSM place features from the local extract.

Fuzzy candidate generation is kept for human review only in `data/map-match-candidates.json`; fuzzy candidates are **not** automatically promoted to published coordinates.

## Sources

### OpenStreetMap / Geofabrik

The build reads the Libya OpenStreetMap extract published by Geofabrik and extracts administrative and named-place features locally. This avoids systematic bulk queries against the public Nominatim service and keeps matching reproducible against one source snapshot.

OSM-derived coordinates and boundary data require OpenStreetMap attribution and the applicable ODbL terms.

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

The ArcGIS service is an operational dataset based on the 2015 Baladiya election list and revised in 2016. The service currently exposes only the records returned by its live endpoint; `v1.2.0` does not infer unavailable records from historical metadata.

It is used only when an exact municipality name can be matched and should not be interpreted as an official statement of current administrative boundaries.

### GeoNames

GeoNames is used as an exact-name fallback for point locations. A GeoNames match represents a named-place/admin reference point, not a municipality polygon.

GeoNames data is distributed under CC BY 4.0; see the upstream project for full terms.

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

The same GeoJSON works with MapLibre, Mapbox, Google Maps data layers, Flutter mapping libraries, native iOS/Android GIS libraries, Python GeoPandas, QGIS, and other clients that support standard GeoJSON.

## Production guidance

1. Pin a release such as `v1.2.0`.
2. Cache or bundle the GeoJSON instead of downloading it on every screen load.
3. Use `slug` or `id` to join map data to `data/municipalities.json`.
4. Read `data/map-coverage.json` before assuming every municipality has a published point or polygon.
5. Preserve source attribution when displaying or redistributing OSM-derived map data.
6. Do not treat a reference point as a legal centroid or municipal office location unless your application separately verifies that meaning.
7. Review the changelog before moving to a newer map-data release.

## Boundary limitations

Municipality boundaries in this repository are published only where a matching administrative polygon can be verified from the selected source. OpenStreetMap may also contain administrative objects exported as label points or incomplete linework; these are not published as municipality polygons here.

A missing polygon does **not** mean the municipality does not exist. It means the repository does not currently have a sufficiently reliable polygon geometry to publish for that municipality.

Boundary data can evolve independently of the Ministry's municipality directory, so source date and coverage must be considered when using it for operational, legal, cadastral, or policy decisions.

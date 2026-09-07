# Data sources and provenance

## Municipalities

The Arabic municipality names in `data/municipalities.json` and `data/municipalities.csv` were compiled from the public municipality directory of the **Libyan Ministry of Local Government**.

Source: https://www.lgm.gov.ly/municipalities

Last checked for this dataset release: **2026-09-07**.

The Ministry directory currently exposes the municipality names as local-government units. This repository assigns its own sequential dataset IDs and stable slugs; those IDs are **not government municipality codes**.

### English names

`name_en` values are developer-friendly transliterations/English display names maintained by this project. Libya place names can have multiple valid Latin spellings, so these values are not presented as official government English spellings.

A correction to an English display name should normally preserve the existing `slug` unless there is a strong compatibility reason to change it.

## Cities

The city list originates from the original `CitySeeder.php` that existed in this repository before the open-data rebuild. The original list contained 50 Arabic city/place names.

The rebuild preserves that legacy coverage, normalizes it into JSON/CSV, and adds English display names and stable slugs.

Unlike the municipality dataset, this city list is **not claimed to be a complete official registry of every city, town, village, or locality in Libya**. Contributions that improve coverage or source verification are welcome.

## Geospatial municipality data — v1.2

`v1.2.0` adds optional map-point and partial boundary datasets as companions to the Ministry-backed municipality directory. These geospatial records do not change municipality identity, IDs, slugs, or the base location contract.

### OpenStreetMap / Geofabrik

The automated map build downloads a Libya OpenStreetMap extract from **Geofabrik** and processes it locally. It uses exact-name matches against administrative and named-place features; fuzzy candidates are generated only for review and are not automatically published as accepted coordinates.

Source: https://download.geofabrik.de/africa/libya.html

OpenStreetMap copyright/license information: https://www.openstreetmap.org/copyright

OSM-derived coordinates and geometry require the applicable OpenStreetMap attribution and ODbL terms. Recommended attribution when displaying OSM-derived map data:

```text
© OpenStreetMap contributors
```

### GeoNames

GeoNames is used as an exact-name fallback for Libyan place/admin reference points when a municipality can be matched confidently.

Source: https://download.geonames.org/export/dump/LY.zip

GeoNames data is distributed under CC BY 4.0. A GeoNames coordinate represents a named-place/admin reference point, not a legal municipality centroid or polygon.

### IOM / OCHA operational municipality hubs

An ArcGIS municipality-hub service is used only for the records currently returned by its live endpoint and only when an exact municipality-name match is available.

Source service: https://services3.arcgis.com/iuNbZYJOrAYBrPyC/ArcGIS/rest/services/Hubs_WFL1/FeatureServer/0

The service is an operational dataset based on an older Baladiya election list and should not be interpreted as an official statement of current administrative boundaries.

### Map-data semantics

Published coordinates are **reference points**. Depending on `point_type`, they can represent a point inside a matched administrative polygon, an administrative label, an exact OSM named place, an operational hub, or a GeoNames place/admin feature.

If no sufficiently confident source match is available, the municipality remains in `data/municipality-points.json` with `null` coordinate/provenance fields. The repository intentionally prefers missing coordinates over guessed ones.

Boundary GeoJSON is partial. Missing geometry does not imply that a municipality does not exist, and the published polygons must not be treated as cadastral or legal boundary authority.

See [`docs/MAPS.md`](docs/MAPS.md) and [`data/map-coverage.json`](data/map-coverage.json) for exact coverage and implementation details.

## Scope rules

- A municipality belongs in the municipality dataset when supported by a reliable local-government source.
- A city/town/locality should not automatically be treated as a municipality.
- Municipal subdivisions (`محلات`) remain a separate concern and are not silently mixed into municipality records.
- Coordinates are published only as sourced, traceable companion data with explicit semantics and provenance.
- Postal codes, electoral codes, and population figures remain out of scope until a reliable and maintainable source is selected.

## Corrections

When opening a correction PR, include:

1. the affected slug;
2. the current value;
3. the proposed value;
4. a reliable source URL or document reference;
5. whether the change affects only display text or also identity/administrative status;
6. for geospatial changes, the coordinate/geometry source and the intended `point_type`.

## Rights and attribution

The repository's original scripts, examples, and documentation are licensed under MIT. Public source facts and place names may be subject to terms applicable to their original sources; this project does not claim additional exclusive rights over those underlying facts.

OpenStreetMap-derived data remains subject to the Open Database License (ODbL) and required attribution. GeoNames-derived data remains subject to its CC BY terms. Source-specific terms must be preserved when redistributing or displaying derived map data.

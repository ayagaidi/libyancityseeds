# Changelog

All notable changes to the Libya Locations dataset are documented here.

## [1.2.0] - 2026-09-07

### Added

- optional municipality map-point dataset with nullable `latitude` and `longitude`
- coordinate provenance fields: `coordinate_source`, `coordinate_source_id`, and `point_type`
- JSON, CSV, and GeoJSON outputs for municipality reference points
- partial municipality boundary GeoJSON from matched OpenStreetMap administrative polygons
- `data/map-coverage.json` with exact point/boundary coverage and unmatched slugs
- review-only `data/map-match-candidates.json` for unresolved municipalities
- JSON Schema for municipality map-point records
- zero-build Leaflet/GeoJSON map example
- map integration and attribution guide in `docs/MAPS.md`
- automated GIS build using public source data and a local Libya OpenStreetMap extract
- validation for coordinate ranges, provenance, GeoJSON consistency, coverage counts, boundary counts, schemas, and versioned map endpoints

### Coverage

- 141 municipality rows in the map-point dataset
- 103 municipalities with published reference points (**73.05%**)
- 38 municipalities intentionally left with null coordinates rather than guessed locations
- 10 matched municipality polygon features in the boundary GeoJSON

### Sources

Published map references are traceable to OpenStreetMap/Geofabrik, GeoNames, or the available IOM/OCHA operational municipality hub service. OpenStreetMap-derived data retains the applicable attribution and ODbL requirements.

### Compatibility

The base location record shape remains unchanged from `v1.1.0`: `id`, `slug`, `name_ar`, `name_en`, and `type`.

Map data is provided as a **companion dataset**, so existing integrations using `municipalities.json` or `cities.json` remain compatible. Applications opt into the new geospatial fields by reading `municipality-points.json` or the GeoJSON files.

## [1.1.0] - 2026-09-07

### Added

- language-agnostic integration guide with stable versioned raw JSON/CSV URLs
- `data/endpoints.json` for programmatic dataset discovery
- JSON Schema for the universal location record contract
- copy-paste examples for JavaScript/TypeScript, Python, PHP, Go, Java, C#/.NET, Dart/Flutter, and Swift
- production guidance for pinned releases, caching, offline bundling, and database imports
- automated validation of integration metadata, schema compatibility, and Python example syntax

### Changed

- repositioned JSON and CSV as the primary framework-neutral interface
- documented Laravel tooling as optional rather than required
- pinned public examples to `v1.1.0` for deterministic production integration

### Compatibility

The location record shape is unchanged from `v1.0.0`: `id`, `slug`, `name_ar`, `name_en`, and `type`. Existing integrations remain compatible.

## [1.0.0] - 2026-09-07

### Added

- 141-entry Libya municipality dataset in JSON and CSV
- Arabic and English display names
- stable developer-friendly slugs
- 50-entry city dataset migrated from the original repository seeder
- Laravel municipality and city seeders using `upsert`
- Laravel migration and API examples
- JavaScript fetch example
- dataset manifest with counts and source metadata
- data provenance and scope documentation
- Arabic and English READMEs
- automated JSON/CSV integrity validation with GitHub Actions

### Changed

- modernized the original root `CitySeeder.php` to read the canonical JSON dataset instead of performing one insert per city

### Compatibility

The original repository contained only a single-column city seeder using a `name` field. Version 1.0 introduces the recommended schema: `slug`, `name_ar`, and `name_en`.

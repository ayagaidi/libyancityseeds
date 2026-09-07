# Changelog

All notable changes to the Libya Locations dataset are documented here.

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

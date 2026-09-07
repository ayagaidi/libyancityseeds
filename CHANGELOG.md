# Changelog

All notable changes to the Libya Locations dataset are documented here.

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

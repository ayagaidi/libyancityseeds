# Libya Locations 🇱🇾

A **language-agnostic open dataset** of Libyan municipalities and cities with Arabic/English names, stable slugs, JSON, CSV, Laravel seeders, and copy-paste integration examples for common languages.

[![Validate data](https://github.com/ayagaidi/libyancityseeds/actions/workflows/validate-data.yml/badge.svg)](https://github.com/ayagaidi/libyancityseeds/actions/workflows/validate-data.yml)

[العربية](README_AR.md) · [Integration guide](docs/INTEGRATION.md) · [Data sources](DATA_SOURCES.md) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md)

> **No SDK. No API key. No framework required.** If your language can make an HTTP request and parse JSON, it can use Libya Locations.

## 30-second integration

Use a stable, versioned JSON URL:

```text
https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json
```

```js
const locations = await fetch(
  'https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json'
).then(response => response.json());
```

The same data contract works in **JavaScript/TypeScript, Python, PHP, Go, Java, C#/.NET, Dart/Flutter, Swift, Ruby, mobile apps, backend services, frontend apps, scripts, and databases**.

See the full **[integration guide](docs/INTEGRATION.md)** and **[copy-paste language examples](examples/README.md)**.

## What's included

| Dataset | Records | Formats |
| --- | ---: | --- |
| Municipalities | 141 | JSON + CSV + Laravel Seeder |
| Cities | 50 | JSON + CSV + Laravel Seeder |

Each record has one universal contract:

```json
{
  "id": 94,
  "slug": "tripoli-center",
  "name_ar": "طرابلس المركز",
  "name_en": "Tripoli Center",
  "type": "municipality"
}
```

A machine-readable JSON Schema is provided in [`schemas/location.schema.json`](schemas/location.schema.json).

## Data files

- [`data/municipalities.json`](data/municipalities.json)
- [`data/municipalities.csv`](data/municipalities.csv)
- [`data/cities.json`](data/cities.json)
- [`data/cities.csv`](data/cities.csv)
- [`data/endpoints.json`](data/endpoints.json) — programmatic discovery of stable dataset URLs
- [`data/manifest.json`](data/manifest.json)

## Stable releases vs latest data

For production, pin a release such as `v1.1.0`:

```text
https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/cities.json
```

For development or previews, use `master`:

```text
https://raw.githubusercontent.com/ayagaidi/libyancityseeds/master/data/cities.json
```

Version pinning keeps production integrations deterministic while still allowing the dataset to evolve.

## Data source & naming

The Arabic municipality list is compiled from the **Libyan Ministry of Local Government** municipality directory and was checked on **2026-09-07**:

https://www.lgm.gov.ly/municipalities

The English names are **developer-friendly transliterations** intended for application UIs and identifiers; they should not be interpreted as a claim of official English spellings. The city list is the original public dataset from this repository, cleaned and expanded with English names/slugs.

See [`DATA_SOURCES.md`](DATA_SOURCES.md) for provenance, scope, and update rules.

## Laravel

Laravel is supported, but it is optional. Copy the dataset and seeders into your Laravel project, then run:

```bash
php artisan db:seed --class=LibyaMunicipalitySeeder
php artisan db:seed --class=LibyaCitySeeder
```

Expected table columns:

```php
$table->id();
$table->string('slug')->unique();
$table->string('name_ar');
$table->string('name_en');
$table->timestamps();
```

The seeders use `upsert`, so rerunning them is safe for the same slugs.

See:

- [`database/seeders/LibyaMunicipalitySeeder.php`](database/seeders/LibyaMunicipalitySeeder.php)
- [`database/seeders/LibyaCitySeeder.php`](database/seeders/LibyaCitySeeder.php)
- [`examples/laravel-api.php`](examples/laravel-api.php)

## Integration examples

Ready-to-copy examples are available for:

- JavaScript / TypeScript
- Python
- PHP
- Go
- Java
- C# / .NET
- Dart / Flutter
- Swift

Start at [`examples/README.md`](examples/README.md).

## Data quality

Every pull request validates that:

- JSON is valid UTF-8 data;
- IDs and slugs are unique;
- required fields are present;
- record types are correct;
- CSV and JSON contain the same records;
- the manifest counts match the actual datasets;
- integration endpoint metadata matches the release version;
- the JSON Schema matches the dataset contract;
- the Python example remains syntactically valid.

Run locally:

```bash
python3 scripts/validate_data.py
```

## Contributing

Spelling and transliteration improvements are welcome, especially when backed by a reliable source. Please do not silently rename a slug that applications may already depend on.

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before submitting a change.

## Project principles

1. **Language-agnostic by default** — JSON/CSV are the primary interface; framework-specific helpers are optional.
2. **Arabic is first-class** — not an afterthought.
3. **Cities and municipalities stay separate** — they are not interchangeable administrative concepts.
4. **Stable slugs matter** — application integrations should not break because display spelling changed.
5. **Sources are documented** — corrections should be reviewable.
6. **No private data** — this repository only contains public location names and developer tooling.

## Maintainer

**Aya Aljaidi** — Laravel / Full-Stack Developer, Tripoli, Libya  
GitHub: [@ayagaidi](https://github.com/ayagaidi)

## License

Original code in this repository is available under the [MIT License](LICENSE). Source facts and names retain any rights or terms applicable to their original public sources; see [`DATA_SOURCES.md`](DATA_SOURCES.md).

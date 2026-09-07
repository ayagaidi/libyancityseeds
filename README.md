# Libya Locations 🇱🇾

A developer-friendly open dataset of **Libyan municipalities and cities** with Arabic/English names, stable slugs, JSON, CSV, Laravel seeders, and API usage examples.

[![Validate data](https://github.com/ayagaidi/libyancityseeds/actions/workflows/validate-data.yml/badge.svg)](https://github.com/ayagaidi/libyancityseeds/actions/workflows/validate-data.yml)

[العربية](README_AR.md) · [Data sources](DATA_SOURCES.md) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md)

> Built for Libyan developers who keep rebuilding the same city/municipality dropdowns in Laravel, mobile apps, APIs, forms, e-commerce, delivery, banking, and government systems.

## What's included

| Dataset | Records | Formats |
| --- | ---: | --- |
| Municipalities | 141 | JSON + CSV + Laravel Seeder |
| Cities | 50 | JSON + CSV + Laravel Seeder |

Each record has a stable numeric `id`, URL-safe `slug`, Arabic `name_ar`, English `name_en`, and `type`.

```json
{
  "id": 94,
  "slug": "tripoli-center",
  "name_ar": "طرابلس المركز",
  "name_en": "Tripoli Center",
  "type": "municipality"
}
```

## Data files

- [`data/municipalities.json`](data/municipalities.json)
- [`data/municipalities.csv`](data/municipalities.csv)
- [`data/cities.json`](data/cities.json)
- [`data/cities.csv`](data/cities.csv)
- [`data/manifest.json`](data/manifest.json)

## Data source & naming

The Arabic municipality list is compiled from the **Libyan Ministry of Local Government** municipality directory and was checked on **2026-09-07**:

https://www.lgm.gov.ly/municipalities

The English names are **developer-friendly transliterations** intended for application UIs and identifiers; they should not be interpreted as a claim of official English spellings. The city list is the original public dataset from this repository, cleaned and expanded with English names/slugs.

See [`DATA_SOURCES.md`](DATA_SOURCES.md) for provenance, scope, and update rules.

## Laravel

Copy the dataset and seeders into your Laravel project, then run:

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

## API example

A simple Laravel endpoint can expose localized data:

```http
GET /api/libya/municipalities?lang=ar
GET /api/libya/municipalities?lang=en
GET /api/libya/cities?lang=ar
```

Example response:

```json
[
  {"id": 1, "slug": "abu-salim", "name": "أبوسليم"},
  {"id": 2, "slug": "ubari", "name": "أوباري"}
]
```

## JavaScript / frontend

```js
const municipalities = await fetch(
  'https://raw.githubusercontent.com/ayagaidi/libyancityseeds/master/data/municipalities.json'
).then(response => response.json());
```

## Data quality

Every pull request validates that:

- JSON is valid UTF-8 data;
- IDs and slugs are unique;
- required fields are present;
- record types are correct;
- CSV and JSON contain the same records;
- the manifest counts match the actual datasets.

Run locally:

```bash
python3 scripts/validate_data.py
```

## Contributing

Spelling and transliteration improvements are welcome, especially when backed by a reliable source. Please do not silently rename a slug that applications may already depend on.

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before submitting a change.

## Project principles

1. **Arabic is first-class** — not an afterthought.
2. **Cities and municipalities stay separate** — they are not interchangeable administrative concepts.
3. **Stable slugs matter** — application integrations should not break because display spelling changed.
4. **Sources are documented** — corrections should be reviewable.
5. **No private data** — this repository only contains public location names and developer tooling.

## Maintainer

**Aya Aljaidi** — Laravel / Full-Stack Developer, Tripoli, Libya  
GitHub: [@ayagaidi](https://github.com/ayagaidi)

## License

Original code in this repository is available under the [MIT License](LICENSE). Source facts and names retain any rights or terms applicable to their original public sources; see [`DATA_SOURCES.md`](DATA_SOURCES.md).

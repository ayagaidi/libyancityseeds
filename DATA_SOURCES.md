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

## Scope rules

- A municipality belongs in the municipality dataset when supported by a reliable local-government source.
- A city/town/locality should not automatically be treated as a municipality.
- Municipal subdivisions (`محلات`) are intentionally out of scope for v1.0 and may become a separate dataset later.
- Coordinates, postal codes, electoral codes, and population figures are out of scope until a reliable and maintainable source is selected.

## Corrections

When opening a correction PR, include:

1. the affected slug;
2. the current value;
3. the proposed value;
4. a reliable source URL or document reference;
5. whether the change affects only display text or also identity/administrative status.

## Rights and attribution

The repository's original scripts, examples, and documentation are licensed under MIT. Public source facts and place names may be subject to terms applicable to their original sources; this project does not claim additional exclusive rights over those underlying facts.

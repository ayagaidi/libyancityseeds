# Contributing

Contributions are welcome, especially corrections that improve Libya location coverage, Arabic spelling, transliteration quality, or developer usability.

## Before changing data

Please identify whether your change affects a **municipality** or a **city/locality**. The two datasets intentionally stay separate.

For municipality changes, include a reliable local-government source when possible. The current baseline source is documented in `DATA_SOURCES.md`.

## Stable slugs

Treat `slug` values as public API identifiers.

- A display-name correction does not automatically require a slug change.
- Avoid changing existing slugs unless identity was wrong or there is a strong compatibility reason.
- If a slug must change, explain the migration impact in the pull request.

## Required checks

After editing JSON, update the matching CSV and manifest count when necessary.

Run:

```bash
python3 scripts/validate_data.py
```

The same validator runs in GitHub Actions for pull requests.

## Pull request checklist

- [ ] I changed the correct dataset (`cities` or `municipalities`).
- [ ] Arabic and English values are UTF-8 and non-empty.
- [ ] IDs and slugs remain unique.
- [ ] JSON and CSV contain the same records.
- [ ] I included a source for administrative corrections.
- [ ] I did not add personal, customer, or private data.
- [ ] `python3 scripts/validate_data.py` passes.

## New fields

Please open an issue before adding fields such as coordinates, postal codes, population, regions, districts, or electoral codes. Those fields need a reliable source and update strategy before becoming part of the stable schema.

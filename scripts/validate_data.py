#!/usr/bin/env python3

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FIELDS = ["id", "slug", "name_ar", "name_en", "type"]
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_csv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_dataset(name: str, expected_type: str, expected_count: int) -> None:
    json_path = ROOT / "data" / f"{name}.json"
    csv_path = ROOT / "data" / f"{name}.csv"

    rows = load_json(json_path)
    csv_rows = load_csv(csv_path)

    assert isinstance(rows, list), f"{json_path} must contain a JSON array"
    assert len(rows) == expected_count, (
        f"{name}: expected {expected_count} JSON rows, found {len(rows)}"
    )
    assert len(csv_rows) == expected_count, (
        f"{name}: expected {expected_count} CSV rows, found {len(csv_rows)}"
    )

    ids = set()
    slugs = set()

    for index, row in enumerate(rows, start=1):
        missing = [field for field in REQUIRED_FIELDS if field not in row]
        assert not missing, f"{name} row {index} missing fields: {missing}"
        assert row["type"] == expected_type, (
            f"{name} row {index}: expected type={expected_type!r}"
        )
        assert isinstance(row["id"], int) and row["id"] > 0, (
            f"{name} row {index}: id must be a positive integer"
        )
        assert row["id"] not in ids, f"{name}: duplicate id {row['id']}"
        assert row["slug"] not in slugs, f"{name}: duplicate slug {row['slug']}"
        assert SLUG_RE.fullmatch(row["slug"]), (
            f"{name}: invalid slug {row['slug']!r}"
        )
        assert row["name_ar"].strip(), f"{name}: empty Arabic name for {row['slug']}"
        assert row["name_en"].strip(), f"{name}: empty English name for {row['slug']}"

        ids.add(row["id"])
        slugs.add(row["slug"])

    assert ids == set(range(1, expected_count + 1)), (
        f"{name}: IDs must be contiguous from 1 to {expected_count}"
    )

    normalized_json = [
        {field: str(row[field]) for field in REQUIRED_FIELDS}
        for row in rows
    ]
    normalized_csv = [
        {field: row[field] for field in REQUIRED_FIELDS}
        for row in csv_rows
    ]

    assert normalized_json == normalized_csv, (
        f"{name}: CSV content does not match JSON content"
    )

    print(f"✓ {name}: {expected_count} records validated")


def validate_integration_metadata(manifest: dict) -> None:
    endpoints = load_json(ROOT / "data" / "endpoints.json")
    schema = load_json(ROOT / "schemas" / "location.schema.json")

    version = endpoints.get("version")
    assert version == "1.1.0", f"endpoints version must be 1.1.0, found {version!r}"

    stable_base = endpoints.get("stable_base_url", "")
    assert f"/v{version}" in stable_base, "stable_base_url must pin the release version"

    for name in ("municipalities", "cities"):
        endpoint = endpoints["datasets"][name]
        expected_count = manifest["datasets"][name]["records"]
        assert endpoint["records"] == expected_count, (
            f"endpoints count for {name} does not match manifest"
        )
        assert f"/v{version}/data/{name}.json" in endpoint["json"], (
            f"{name} JSON endpoint must pin v{version}"
        )
        assert f"/v{version}/data/{name}.csv" in endpoint["csv"], (
            f"{name} CSV endpoint must pin v{version}"
        )

    assert schema["required"] == REQUIRED_FIELDS, (
        "JSON Schema required fields do not match the dataset contract"
    )
    assert schema["properties"]["type"]["enum"] == ["city", "municipality"], (
        "JSON Schema location types are out of sync"
    )

    python_example = (ROOT / "examples" / "python.py").read_text(encoding="utf-8")
    compile(python_example, "examples/python.py", "exec")

    print("✓ integration endpoints validated")
    print("✓ JSON Schema validated")
    print("✓ Python integration example syntax validated")


def main() -> None:
    manifest = load_json(ROOT / "data" / "manifest.json")

    validate_dataset(
        "municipalities",
        "municipality",
        manifest["datasets"]["municipalities"]["records"],
    )
    validate_dataset(
        "cities",
        "city",
        manifest["datasets"]["cities"]["records"],
    )

    assert manifest["fields"] == REQUIRED_FIELDS, "manifest fields do not match schema"

    print("✓ manifest validated")
    validate_integration_metadata(manifest)
    print("All Libya location datasets and integration metadata are valid.")


if __name__ == "__main__":
    main()

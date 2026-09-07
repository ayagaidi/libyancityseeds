#!/usr/bin/env python3

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FIELDS = ["id", "slug", "name_ar", "name_en", "type"]
MAP_POINT_FIELDS = [
    "id",
    "slug",
    "name_ar",
    "name_en",
    "type",
    "latitude",
    "longitude",
    "coordinate_source",
    "coordinate_source_id",
    "point_type",
]
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


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


def validate_map_data(manifest: dict, endpoints: dict) -> None:
    municipalities = load_json(ROOT / "data" / "municipalities.json")
    points = load_json(ROOT / "data" / "municipality-points.json")
    csv_points = load_csv(ROOT / "data" / "municipality-points.csv")
    points_geojson = load_json(ROOT / "data" / "municipality-points.geojson")
    boundaries_geojson = load_json(ROOT / "data" / "municipality-boundaries.geojson")
    coverage = load_json(ROOT / "data" / "map-coverage.json")
    map_schema = load_json(ROOT / "schemas" / "municipality-map-point.schema.json")

    expected_total = manifest["map_datasets"]["municipality_points"]["records"]
    expected_mapped = manifest["map_datasets"]["municipality_points"]["mapped_records"]
    expected_boundaries = manifest["map_datasets"]["municipality_boundaries"]["features"]

    assert manifest["map_point_fields"] == MAP_POINT_FIELDS, (
        "manifest map-point fields do not match the v1.2 contract"
    )
    assert len(points) == expected_total == len(municipalities), (
        "municipality map-point record count must match municipality count"
    )
    assert len(csv_points) == expected_total, "map-point CSV count does not match JSON"

    mapped = 0
    municipality_by_id = {row["id"]: row for row in municipalities}
    mapped_by_id = {}

    for row in points:
        assert list(row.keys()) == MAP_POINT_FIELDS, (
            f"map point {row.get('id')} fields are out of contract order/content"
        )
        base = municipality_by_id.get(row["id"])
        assert base, f"map point references unknown municipality id {row['id']}"
        for field in REQUIRED_FIELDS:
            assert row[field] == base[field], (
                f"map point {row['id']} does not match canonical municipality field {field}"
            )

        lat = row["latitude"]
        lon = row["longitude"]
        assert (lat is None) == (lon is None), (
            f"map point {row['slug']} must publish latitude and longitude together"
        )

        if lat is None:
            assert row["coordinate_source"] is None
            assert row["coordinate_source_id"] is None
            assert row["point_type"] is None
            continue

        assert isinstance(lat, (int, float)) and 19 <= lat <= 34, (
            f"map point {row['slug']} latitude is outside Libya validation bounds"
        )
        assert isinstance(lon, (int, float)) and 9 <= lon <= 26, (
            f"map point {row['slug']} longitude is outside Libya validation bounds"
        )
        assert row["coordinate_source"], f"map point {row['slug']} missing source"
        assert row["coordinate_source_id"], f"map point {row['slug']} missing source id"
        assert row["point_type"], f"map point {row['slug']} missing point type"
        mapped += 1
        mapped_by_id[row["id"]] = row

    assert mapped == expected_mapped, (
        f"manifest says {expected_mapped} mapped municipalities but data has {mapped}"
    )

    for json_row, csv_row in zip(points, csv_points):
        for field in REQUIRED_FIELDS:
            assert str(json_row[field]) == csv_row[field]
        if json_row["latitude"] is None:
            assert csv_row["latitude"] == "" and csv_row["longitude"] == ""
            assert csv_row["coordinate_source"] == ""
            assert csv_row["coordinate_source_id"] == ""
            assert csv_row["point_type"] == ""
        else:
            assert float(csv_row["latitude"]) == float(json_row["latitude"])
            assert float(csv_row["longitude"]) == float(json_row["longitude"])
            assert csv_row["coordinate_source"] == json_row["coordinate_source"]
            assert csv_row["coordinate_source_id"] == str(json_row["coordinate_source_id"])
            assert csv_row["point_type"] == json_row["point_type"]

    assert points_geojson.get("type") == "FeatureCollection"
    assert len(points_geojson.get("features", [])) == expected_mapped
    geojson_ids = set()
    for feature in points_geojson["features"]:
        props = feature["properties"]
        geometry = feature["geometry"]
        row = mapped_by_id[props["id"]]
        assert props["id"] not in geojson_ids, f"duplicate GeoJSON point id {props['id']}"
        geojson_ids.add(props["id"])
        assert geometry["type"] == "Point"
        assert geometry["coordinates"] == [row["longitude"], row["latitude"]]
        assert props["slug"] == row["slug"]
        assert props["coordinate_source"] == row["coordinate_source"]
        assert props["point_type"] == row["point_type"]

    assert boundaries_geojson.get("type") == "FeatureCollection"
    assert len(boundaries_geojson.get("features", [])) == expected_boundaries
    boundary_ids = [feature["properties"]["id"] for feature in boundaries_geojson["features"]]
    assert len(boundary_ids) == len(set(boundary_ids)), "duplicate municipality boundary ids"

    assert coverage["total_municipalities"] == expected_total
    assert coverage["mapped_municipalities"] == expected_mapped
    assert coverage["matched_osm_boundaries"] == expected_boundaries
    assert len(coverage["unmatched_slugs"]) == expected_total - expected_mapped
    assert sum(coverage["source_counts"].values()) == expected_total
    assert coverage["source_counts"].get("unmatched", 0) == expected_total - expected_mapped

    map_endpoint = endpoints["maps"]["municipality_points"]
    boundary_endpoint = endpoints["maps"]["municipality_boundaries"]
    assert map_endpoint["records"] == expected_total
    assert map_endpoint["mapped_records"] == expected_mapped
    assert map_endpoint["coverage_percent"] == coverage["coverage_percent"]
    assert boundary_endpoint["features"] == expected_boundaries

    assert map_schema["required"] == MAP_POINT_FIELDS
    allowed_point_types = set(map_schema["properties"]["point_type"]["enum"])
    for row in points:
        assert row["point_type"] in allowed_point_types

    leaflet_example = (ROOT / "examples" / "leaflet-map.html").read_text(encoding="utf-8")
    assert "municipality-points.geojson" in leaflet_example, (
        "Leaflet example must load the municipality point GeoJSON"
    )

    print(f"✓ map points: {mapped}/{expected_total} mapped ({coverage['coverage_percent']}%)")
    print(f"✓ municipality boundaries: {expected_boundaries} GeoJSON features validated")
    print("✓ map provenance, schema, endpoints, and Leaflet example validated")


def validate_integration_metadata(manifest: dict) -> None:
    endpoints = load_json(ROOT / "data" / "endpoints.json")
    schema = load_json(ROOT / "schemas" / "location.schema.json")

    version = endpoints.get("version")
    assert VERSION_RE.fullmatch(version or ""), f"invalid semantic version {version!r}"
    assert manifest.get("version") == version, (
        "manifest and endpoints must publish the same release version"
    )

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

    assert f"/v{version}/schemas/location.schema.json" in endpoints["schema"]
    assert f"/v{version}/schemas/municipality-map-point.schema.json" in endpoints["map_point_schema"]

    assert schema["required"] == REQUIRED_FIELDS, (
        "JSON Schema required fields do not match the dataset contract"
    )
    assert schema["properties"]["type"]["enum"] == ["city", "municipality"], (
        "JSON Schema location types are out of sync"
    )

    python_example = (ROOT / "examples" / "python.py").read_text(encoding="utf-8")
    compile(python_example, "examples/python.py", "exec")

    validate_map_data(manifest, endpoints)

    print(f"✓ integration endpoints validated for v{version}")
    print("✓ JSON Schemas validated")
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
    print("All Libya location datasets, map data, and integration metadata are valid.")


if __name__ == "__main__":
    main()

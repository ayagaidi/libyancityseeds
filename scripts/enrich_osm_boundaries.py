#!/usr/bin/env python3

import csv
import json
import os
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

from shapely.geometry import mapping, shape

ROOT = Path(__file__).resolve().parents[1]
OSM_PATH = Path(os.environ.get("OSM_BOUNDARIES_GEOJSON", "/tmp/libya-admin-boundaries.geojson"))
POINTS_JSON_PATH = ROOT / "data" / "municipality-points.json"
POINTS_CSV_PATH = ROOT / "data" / "municipality-points.csv"
POINTS_GEOJSON_PATH = ROOT / "data" / "municipality-points.geojson"
BOUNDARIES_GEOJSON_PATH = ROOT / "data" / "municipality-boundaries.geojson"
COVERAGE_PATH = ROOT / "data" / "map-coverage.json"

ARABIC_TRANSLATION = str.maketrans({
    "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا",
    "ى": "ي", "ة": "ه", "ؤ": "و", "ئ": "ي",
})


def normalize_ar(value: str) -> str:
    value = (value or "").strip().translate(ARABIC_TRANSLATION)
    value = "".join(ch for ch in unicodedata.normalize("NFKD", value) if not unicodedata.combining(ch))
    return re.sub(r"[^\u0600-\u06ff0-9]+", "", value)


def normalize_en(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def feature_names(props):
    keys = [
        "name", "name:ar", "name:en", "official_name", "official_name:ar", "official_name:en",
        "alt_name", "alt_name:ar", "alt_name:en", "short_name", "short_name:ar", "short_name:en",
    ]
    values = []
    for key in keys:
        value = props.get(key)
        if not value:
            continue
        values.extend(part.strip() for part in str(value).split(";") if part.strip())
    return values


def relation_id(feature, props):
    for key in ("@id", "id", "osm_id", "relation_id"):
        value = props.get(key)
        if value:
            return str(value)
    if feature.get("id") is not None:
        return str(feature["id"])
    return ""


def build_index(features):
    index = defaultdict(list)
    for feature in features:
        geometry = feature.get("geometry")
        if not geometry or geometry.get("type") not in {"Polygon", "MultiPolygon"}:
            continue
        props = feature.get("properties") or {}
        if props.get("boundary") != "administrative":
            continue

        try:
            admin_level = int(props.get("admin_level") or 0)
        except ValueError:
            admin_level = 0

        # Libya municipalities are local administrative units. Exclude country/very broad levels.
        if admin_level and admin_level < 5:
            continue

        geom = shape(geometry)
        if geom.is_empty or not geom.is_valid:
            geom = geom.buffer(0)
        if geom.is_empty:
            continue

        item = {
            "feature": feature,
            "geometry": geom,
            "admin_level": admin_level,
            "source_id": relation_id(feature, props),
        }

        for name in feature_names(props):
            ar = normalize_ar(name)
            en = normalize_en(name)
            if ar:
                index[("ar", ar)].append(item)
            if en:
                index[("en", en)].append(item)

    return index


def choose_boundary(candidates):
    if not candidates:
        return None

    # Prefer the most local admin level; if tied, prefer the smaller geometry.
    unique = {}
    for candidate in candidates:
        key = candidate["source_id"] or candidate["geometry"].wkb_hex
        unique[key] = candidate
    ranked = sorted(
        unique.values(),
        key=lambda item: (item["admin_level"], -item["geometry"].area),
        reverse=True,
    )
    return ranked[0]


def find_boundary(point, index):
    keys = [
        ("ar", normalize_ar(point["name_ar"])),
        ("en", normalize_en(point["name_en"])),
        ("en", normalize_en(point["slug"])),
    ]
    for key in keys:
        match = choose_boundary(index.get(key, []))
        if match:
            return match
    return None


def update_points_geojson(points):
    features = []
    for point in points:
        if point["latitude"] is None or point["longitude"] is None:
            continue
        features.append({
            "type": "Feature",
            "id": point["id"],
            "properties": {
                "id": point["id"],
                "slug": point["slug"],
                "name_ar": point["name_ar"],
                "name_en": point["name_en"],
                "type": "municipality",
                "coordinate_source": point["coordinate_source"],
                "coordinate_source_id": point["coordinate_source_id"],
                "point_type": point["point_type"],
            },
            "geometry": {
                "type": "Point",
                "coordinates": [point["longitude"], point["latitude"]],
            },
        })
    POINTS_GEOJSON_PATH.write_text(
        json.dumps({"type": "FeatureCollection", "name": "libya-municipality-points", "features": features}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return len(features)


def write_csv(points):
    fields = [
        "id", "slug", "name_ar", "name_en", "type", "latitude", "longitude",
        "coordinate_source", "coordinate_source_id", "point_type",
    ]
    with POINTS_CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(points)


def main():
    if not OSM_PATH.exists():
        raise SystemExit(f"OSM boundary GeoJSON not found: {OSM_PATH}")

    points = json.loads(POINTS_JSON_PATH.read_text(encoding="utf-8"))
    osm = json.loads(OSM_PATH.read_text(encoding="utf-8"))
    index = build_index(osm.get("features", []))

    boundary_features = []
    matched_boundaries = 0
    filled_from_osm = 0

    for point in points:
        match = find_boundary(point, index)
        if not match:
            continue

        geom = match["geometry"]
        representative = geom.representative_point()
        matched_boundaries += 1

        # Administrative-boundary representative points are preferred over locality fallbacks.
        if point["coordinate_source"] != "iom-ocha-hubs-2016":
            if point["latitude"] is None:
                filled_from_osm += 1
            point["latitude"] = round(representative.y, 6)
            point["longitude"] = round(representative.x, 6)
            point["coordinate_source"] = "openstreetmap-geofabrik"
            point["coordinate_source_id"] = match["source_id"]
            point["point_type"] = "boundary_representative_point"

        boundary_features.append({
            "type": "Feature",
            "id": point["id"],
            "properties": {
                "id": point["id"],
                "slug": point["slug"],
                "name_ar": point["name_ar"],
                "name_en": point["name_en"],
                "type": "municipality",
                "source": "openstreetmap-geofabrik",
                "source_id": match["source_id"],
                "admin_level": match["admin_level"],
            },
            "geometry": mapping(geom),
        })

    POINTS_JSON_PATH.write_text(json.dumps(points, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(points)
    mapped = update_points_geojson(points)

    BOUNDARIES_GEOJSON_PATH.write_text(
        json.dumps({
            "type": "FeatureCollection",
            "name": "libya-municipality-boundaries",
            "attribution": "© OpenStreetMap contributors; extract by Geofabrik",
            "features": boundary_features,
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    coverage = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
    counts = defaultdict(int)
    for point in points:
        counts[point["coordinate_source"] or "unmatched"] += 1

    coverage.update({
        "mapped_municipalities": mapped,
        "coverage_percent": round(mapped / len(points) * 100, 2),
        "source_counts": dict(counts),
        "matched_osm_boundaries": matched_boundaries,
        "filled_from_osm_boundaries": filled_from_osm,
        "unmatched_slugs": [point["slug"] for point in points if point["latitude"] is None],
    })
    coverage.setdefault("sources", {})["openstreetmap-geofabrik"] = {
        "url": "https://download.geofabrik.de/africa/libya.html",
        "license": "OpenStreetMap ODbL 1.0",
        "note": "Current OpenStreetMap administrative boundary relations from the Geofabrik Libya extract. Representative points are generated inside matched boundary polygons; boundary coverage depends on OSM mapping completeness."
    }
    COVERAGE_PATH.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"OSM boundaries matched: {matched_boundaries}")
    print(f"Previously unmatched municipalities filled from OSM: {filled_from_osm}")
    print(f"Final mapped municipality points: {mapped}/{len(points)} ({coverage['coverage_percent']}%)")
    if coverage["unmatched_slugs"]:
        print("Still unmatched:", ", ".join(coverage["unmatched_slugs"]))


if __name__ == "__main__":
    main()

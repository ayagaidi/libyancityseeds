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
OSM_ADMIN_PATH = Path(os.environ.get("OSM_BOUNDARIES_GEOJSON", "/tmp/libya-admin-boundaries.geojson"))
OSM_PLACES_PATH = Path(os.environ.get("OSM_PLACES_GEOJSON", "/tmp/libya-places.geojson"))
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
        "loc_name", "old_name",
    ]
    values = []
    for key in keys:
        value = props.get(key)
        if not value:
            continue
        values.extend(part.strip() for part in str(value).split(";") if part.strip())
    return values


def source_id(feature, props):
    for key in ("@id", "id", "osm_id", "relation_id"):
        value = props.get(key)
        if value:
            return str(value)
    if feature.get("id") is not None:
        return str(feature["id"])
    return ""


def admin_level(props):
    try:
        return int(props.get("admin_level") or 0)
    except (TypeError, ValueError):
        return 0


def add_names(index, item, props):
    for name in feature_names(props):
        ar = normalize_ar(name)
        en = normalize_en(name)
        if ar:
            index[("ar", ar)].append(item)
        if en:
            index[("en", en)].append(item)


def build_boundary_index(features):
    index = defaultdict(list)
    for feature in features:
        geometry = feature.get("geometry")
        if not geometry or geometry.get("type") not in {"Polygon", "MultiPolygon"}:
            continue
        props = feature.get("properties") or {}
        if props.get("boundary") != "administrative" or admin_level(props) != 4:
            continue

        geom = shape(geometry)
        if geom.is_empty or not geom.is_valid:
            geom = geom.buffer(0)
        if geom.is_empty:
            continue

        item = {
            "geometry": geom,
            "admin_level": 4,
            "source_id": source_id(feature, props),
        }
        add_names(index, item, props)
    return index


def build_admin_point_index(features):
    index = defaultdict(list)
    for feature in features:
        geometry = feature.get("geometry")
        if not geometry or geometry.get("type") != "Point":
            continue
        props = feature.get("properties") or {}
        if admin_level(props) != 4:
            continue

        coordinates = geometry.get("coordinates") or []
        if len(coordinates) < 2:
            continue
        lon, lat = float(coordinates[0]), float(coordinates[1])
        if not (9 <= lon <= 26 and 19 <= lat <= 34):
            continue

        item = {
            "latitude": lat,
            "longitude": lon,
            "source_id": source_id(feature, props),
        }
        add_names(index, item, props)
    return index


def build_named_place_index(features):
    index = defaultdict(list)
    accepted_place_types = {
        "city", "town", "village", "hamlet", "municipality", "suburb", "quarter", "locality"
    }

    for feature in features:
        geometry = feature.get("geometry")
        if not geometry:
            continue
        props = feature.get("properties") or {}
        place_type = str(props.get("place") or "").lower()
        if place_type not in accepted_place_types:
            continue

        geom = shape(geometry)
        if geom.is_empty:
            continue
        if not geom.is_valid:
            geom = geom.buffer(0)
        if geom.is_empty:
            continue

        point = geom if geom.geom_type == "Point" else geom.representative_point()
        lon, lat = float(point.x), float(point.y)
        if not (9 <= lon <= 26 and 19 <= lat <= 34):
            continue

        item = {
            "latitude": lat,
            "longitude": lon,
            "source_id": source_id(feature, props),
            "place_type": place_type,
        }
        add_names(index, item, props)
    return index


def lookup_keys(point):
    return [
        ("ar", normalize_ar(point["name_ar"])),
        ("en", normalize_en(point["name_en"])),
        ("en", normalize_en(point["slug"])),
    ]


def choose_boundary(candidates):
    if not candidates:
        return None
    unique = {}
    for candidate in candidates:
        key = candidate["source_id"] or candidate["geometry"].wkb_hex
        unique[key] = candidate
    return min(unique.values(), key=lambda item: item["geometry"].area)


def choose_unique_point(candidates):
    if not candidates:
        return None
    unique = {}
    for candidate in candidates:
        key = (
            candidate["source_id"],
            round(candidate["latitude"], 7),
            round(candidate["longitude"], 7),
        )
        unique[key] = candidate
    return next(iter(unique.values())) if len(unique) == 1 else None


def find_match(point, index, chooser):
    for key in lookup_keys(point):
        match = chooser(index.get(key, []))
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
    if not OSM_ADMIN_PATH.exists():
        raise SystemExit(f"OSM admin GeoJSON not found: {OSM_ADMIN_PATH}")
    if not OSM_PLACES_PATH.exists():
        raise SystemExit(f"OSM places GeoJSON not found: {OSM_PLACES_PATH}")

    points = json.loads(POINTS_JSON_PATH.read_text(encoding="utf-8"))
    admin_features = json.loads(OSM_ADMIN_PATH.read_text(encoding="utf-8")).get("features", [])
    place_features = json.loads(OSM_PLACES_PATH.read_text(encoding="utf-8")).get("features", [])

    boundary_index = build_boundary_index(admin_features)
    admin_point_index = build_admin_point_index(admin_features)
    named_place_index = build_named_place_index(place_features)

    boundary_features = []
    matched_boundaries = 0
    filled_from_boundaries = 0
    matched_admin_points = 0
    filled_from_admin_points = 0
    matched_named_places = 0
    filled_from_named_places = 0

    for point in points:
        boundary = find_match(point, boundary_index, choose_boundary)
        admin_point = find_match(point, admin_point_index, choose_unique_point)
        named_place = find_match(point, named_place_index, choose_unique_point)

        if boundary:
            geom = boundary["geometry"]
            representative = geom.representative_point()
            matched_boundaries += 1

            if point["coordinate_source"] != "iom-ocha-hubs-2016":
                if point["latitude"] is None:
                    filled_from_boundaries += 1
                point["latitude"] = round(representative.y, 6)
                point["longitude"] = round(representative.x, 6)
                point["coordinate_source"] = "openstreetmap-geofabrik"
                point["coordinate_source_id"] = boundary["source_id"]
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
                    "source_id": boundary["source_id"],
                    "admin_level": 4,
                },
                "geometry": mapping(geom),
            })
        elif admin_point:
            matched_admin_points += 1
            if point["coordinate_source"] != "iom-ocha-hubs-2016":
                if point["latitude"] is None:
                    filled_from_admin_points += 1
                point["latitude"] = round(admin_point["latitude"], 6)
                point["longitude"] = round(admin_point["longitude"], 6)
                point["coordinate_source"] = "openstreetmap-geofabrik"
                point["coordinate_source_id"] = admin_point["source_id"]
                point["point_type"] = "administrative_label_point"
        elif named_place:
            matched_named_places += 1
            # Exact-name OSM places are a safer fallback than unrelated fuzzy matches,
            # but they do not replace the older IOM/OCHA operational hub reference.
            if point["coordinate_source"] != "iom-ocha-hubs-2016":
                if point["latitude"] is None:
                    filled_from_named_places += 1
                point["latitude"] = round(named_place["latitude"], 6)
                point["longitude"] = round(named_place["longitude"], 6)
                point["coordinate_source"] = "openstreetmap-geofabrik"
                point["coordinate_source_id"] = named_place["source_id"]
                point["point_type"] = "osm_named_place"

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
        "filled_from_osm_boundaries": filled_from_boundaries,
        "matched_osm_admin_points": matched_admin_points,
        "filled_from_osm_admin_points": filled_from_admin_points,
        "matched_osm_named_places": matched_named_places,
        "filled_from_osm_named_places": filled_from_named_places,
        "unmatched_slugs": [point["slug"] for point in points if point["latitude"] is None],
    })
    coverage.setdefault("sources", {})["openstreetmap-geofabrik"] = {
        "url": "https://download.geofabrik.de/africa/libya.html",
        "license": "OpenStreetMap ODbL 1.0",
        "note": "OpenStreetMap Libya admin_level=4 polygons/admin points and exact-name place features from the Geofabrik extract. Boundary representative points are preferred, then exact administrative label points, then exact named-place points."
    }
    COVERAGE_PATH.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"OSM boundaries matched: {matched_boundaries}; newly filled: {filled_from_boundaries}")
    print(f"OSM admin points matched: {matched_admin_points}; newly filled: {filled_from_admin_points}")
    print(f"OSM named places matched: {matched_named_places}; newly filled: {filled_from_named_places}")
    print(f"Final mapped municipality points: {mapped}/{len(points)} ({coverage['coverage_percent']}%)")
    if coverage["unmatched_slugs"]:
        print("Still unmatched:", ", ".join(coverage["unmatched_slugs"]))


if __name__ == "__main__":
    main()

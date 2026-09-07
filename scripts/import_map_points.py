#!/usr/bin/env python3

import csv
import io
import json
import re
import unicodedata
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MUNICIPALITIES_PATH = ROOT / "data" / "municipalities.json"
POINTS_JSON_PATH = ROOT / "data" / "municipality-points.json"
POINTS_CSV_PATH = ROOT / "data" / "municipality-points.csv"
POINTS_GEOJSON_PATH = ROOT / "data" / "municipality-points.geojson"
COVERAGE_PATH = ROOT / "data" / "map-coverage.json"

ARCGIS_QUERY_URL = (
    "https://services3.arcgis.com/iuNbZYJOrAYBrPyC/ArcGIS/rest/services/"
    "Hubs_WFL1/FeatureServer/0/query"
)
GEONAMES_URL = "https://download.geonames.org/export/dump/LY.zip"
USER_AGENT = "libyancityseeds-map-import/1.2 (+https://github.com/ayagaidi/libyancityseeds)"

ARABIC_TRANSLATION = str.maketrans({
    "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا",
    "ى": "ي", "ة": "ه", "ؤ": "و", "ئ": "ي",
})


def fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def fetch_json(url: str):
    payload = json.loads(fetch_bytes(url).decode("utf-8"))
    if "error" in payload:
        raise RuntimeError(f"Remote source error: {payload['error']}")
    return payload


def normalize_ar(value: str) -> str:
    value = (value or "").strip().translate(ARABIC_TRANSLATION)
    value = "".join(ch for ch in unicodedata.normalize("NFKD", value) if not unicodedata.combining(ch))
    return re.sub(r"[^\u0600-\u06ff0-9]+", "", value)


def normalize_en(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def load_municipalities():
    return json.loads(MUNICIPALITIES_PATH.read_text(encoding="utf-8"))


def arcgis_url(params):
    return f"{ARCGIS_QUERY_URL}?{urllib.parse.urlencode(params)}"


def fetch_arcgis_features():
    ids_payload = fetch_json(arcgis_url({
        "where": "1=1",
        "returnIdsOnly": "true",
        "f": "json",
    }))
    object_ids = sorted(ids_payload.get("objectIds") or [])
    print(f"ArcGIS source object IDs: {len(object_ids)}")

    features = []
    batch_size = 100
    for offset in range(0, len(object_ids), batch_size):
        batch = object_ids[offset:offset + batch_size]
        payload = fetch_json(arcgis_url({
            "objectIds": ",".join(str(object_id) for object_id in batch),
            "outFields": "*",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "json",
        }))
        for feature in payload.get("features", []):
            geometry = feature.get("geometry") or {}
            if "x" not in geometry or "y" not in geometry:
                continue
            features.append({
                "properties": feature.get("attributes") or {},
                "geometry": {
                    "coordinates": [float(geometry["x"]), float(geometry["y"])],
                },
            })

    print(f"ArcGIS source features with geometry: {len(features)}")
    return features


def build_arcgis_index(features):
    index = {}
    fields = [
        "featureName_en", "featureName_ar", "featureRefName",
        "featureAltName1_en", "featureAltName2_en",
        "featureAltName1_ar", "featureAltName2_ar",
    ]

    for feature in features:
        geometry = feature.get("geometry") or {}
        coords = geometry.get("coordinates") or []
        if len(coords) < 2:
            continue

        props = feature.get("properties") or {}
        record = {
            "longitude": float(coords[0]),
            "latitude": float(coords[1]),
            "source": "iom-ocha-hubs-2016",
            "source_id": props.get("pcode") or str(props.get("OBJECTID", "")),
            "point_type": "operational_hub",
        }

        keys = set()
        for field in fields:
            value = props.get(field)
            if not value:
                continue
            keys.add(("ar", normalize_ar(value)))
            keys.add(("en", normalize_en(value)))

        for key in keys:
            if key[1]:
                index.setdefault(key, []).append(record)

    return index


def fetch_geonames_rows():
    archive = zipfile.ZipFile(io.BytesIO(fetch_bytes(GEONAMES_URL)))
    with archive.open("LY.txt") as handle:
        text = io.TextIOWrapper(handle, encoding="utf-8")
        for line in text:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 19:
                continue
            yield {
                "geonameid": parts[0],
                "name": parts[1],
                "asciiname": parts[2],
                "alternatenames": [name for name in parts[3].split(",") if name],
                "latitude": float(parts[4]),
                "longitude": float(parts[5]),
                "feature_class": parts[6],
                "feature_code": parts[7],
                "country_code": parts[8],
                "population": int(parts[14] or 0),
            }


def build_geonames_index(rows):
    index = {}
    for row in rows:
        if row["country_code"] != "LY" or row["feature_class"] not in {"P", "A"}:
            continue

        names = [row["name"], row["asciiname"], *row["alternatenames"]]
        record = {
            "longitude": row["longitude"],
            "latitude": row["latitude"],
            "source": "geonames",
            "source_id": row["geonameid"],
            "point_type": "named_place",
            "feature_class": row["feature_class"],
            "feature_code": row["feature_code"],
            "population": row["population"],
        }

        keys = set()
        for name in names:
            keys.add(("ar", normalize_ar(name)))
            keys.add(("en", normalize_en(name)))
        for key in keys:
            if key[1]:
                index.setdefault(key, []).append(record)

    return index


def choose_unique(candidates):
    unique = {}
    for candidate in candidates:
        key = (candidate["latitude"], candidate["longitude"], candidate["source_id"])
        unique[key] = candidate
    candidates = list(unique.values())
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    ranked = sorted(
        candidates,
        key=lambda item: (
            1 if item.get("feature_class") == "A" else 0,
            item.get("population", 0),
        ),
        reverse=True,
    )
    return ranked[0]


def find_match(municipality, arcgis_index, geonames_index):
    keys = [
        ("ar", normalize_ar(municipality["name_ar"])),
        ("en", normalize_en(municipality["name_en"])),
        ("en", normalize_en(municipality["slug"])),
    ]

    for key in keys:
        match = choose_unique(arcgis_index.get(key, []))
        if match:
            return match

    for key in keys:
        match = choose_unique(geonames_index.get(key, []))
        if match:
            return match

    return None


def build_outputs(municipalities, arcgis_index, geonames_index):
    points = []
    features = []
    source_counts = {"iom-ocha-hubs-2016": 0, "geonames": 0, "unmatched": 0}

    for municipality in municipalities:
        match = find_match(municipality, arcgis_index, geonames_index)
        point = {
            "id": municipality["id"],
            "slug": municipality["slug"],
            "name_ar": municipality["name_ar"],
            "name_en": municipality["name_en"],
            "type": "municipality",
            "latitude": None,
            "longitude": None,
            "coordinate_source": None,
            "coordinate_source_id": None,
            "point_type": None,
        }

        if match:
            point.update({
                "latitude": round(match["latitude"], 6),
                "longitude": round(match["longitude"], 6),
                "coordinate_source": match["source"],
                "coordinate_source_id": match["source_id"],
                "point_type": match["point_type"],
            })
            source_counts[match["source"]] += 1
            features.append({
                "type": "Feature",
                "id": municipality["id"],
                "properties": {
                    "id": municipality["id"],
                    "slug": municipality["slug"],
                    "name_ar": municipality["name_ar"],
                    "name_en": municipality["name_en"],
                    "type": "municipality",
                    "coordinate_source": match["source"],
                    "coordinate_source_id": match["source_id"],
                    "point_type": match["point_type"],
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [round(match["longitude"], 6), round(match["latitude"], 6)],
                },
            })
        else:
            source_counts["unmatched"] += 1

        points.append(point)

    return points, features, source_counts


def write_outputs(points, features, source_counts, arcgis_count):
    POINTS_JSON_PATH.write_text(json.dumps(points, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    fields = [
        "id", "slug", "name_ar", "name_en", "type", "latitude", "longitude",
        "coordinate_source", "coordinate_source_id", "point_type",
    ]
    with POINTS_CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(points)

    geojson = {
        "type": "FeatureCollection",
        "name": "libya-municipality-points",
        "features": features,
    }
    POINTS_GEOJSON_PATH.write_text(json.dumps(geojson, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    matched = len(features)
    total = len(points)
    coverage = {
        "version_target": "1.2.0",
        "generated_at": "2026-09-07",
        "total_municipalities": total,
        "mapped_municipalities": matched,
        "coverage_percent": round((matched / total) * 100, 2) if total else 0,
        "source_counts": source_counts,
        "sources": {
            "iom-ocha-hubs-2016": {
                "records_available_from_source": arcgis_count,
                "url": "https://services3.arcgis.com/iuNbZYJOrAYBrPyC/ArcGIS/rest/services/Hubs_WFL1/FeatureServer/0",
                "note": "Operational municipality hub points based on the 2015 Baladiya election list and revised in 2016; not an official endorsement of current administrative divisions."
            },
            "geonames": {
                "url": "https://download.geonames.org/export/dump/LY.zip",
                "license": "CC BY 4.0",
                "note": "Fallback exact-name matches to Libya named/admin places; represents a named-place reference point rather than a legal municipality centroid."
            }
        },
        "unmatched_slugs": [row["slug"] for row in points if row["latitude"] is None],
    }
    COVERAGE_PATH.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Generated {matched}/{total} mapped municipality points ({coverage['coverage_percent']}%).")
    print(json.dumps(source_counts, indent=2))
    if coverage["unmatched_slugs"]:
        print("Unmatched:", ", ".join(coverage["unmatched_slugs"]))


def main():
    municipalities = load_municipalities()
    arcgis_features = fetch_arcgis_features()
    arcgis_index = build_arcgis_index(arcgis_features)
    geonames_index = build_geonames_index(fetch_geonames_rows())
    points, features, counts = build_outputs(municipalities, arcgis_index, geonames_index)
    write_outputs(points, features, counts, len(arcgis_features))


if __name__ == "__main__":
    main()

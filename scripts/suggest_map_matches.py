#!/usr/bin/env python3

import io
import json
import re
import unicodedata
import urllib.request
import zipfile
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POINTS_PATH = ROOT / "data" / "municipality-points.json"
OUTPUT_PATH = ROOT / "data" / "map-match-candidates.json"
GEONAMES_URL = "https://download.geonames.org/export/dump/LY.zip"
USER_AGENT = "libyancityseeds-map-candidates/1.2 (+https://github.com/ayagaidi/libyancityseeds)"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def download_rows():
    request = urllib.request.Request(GEONAMES_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))

    rows = []
    with archive.open("LY.txt") as handle:
        for line in io.TextIOWrapper(handle, encoding="utf-8"):
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 19 or parts[8] != "LY" or parts[6] not in {"P", "A"}:
                continue
            names = [parts[1], parts[2], *[x for x in parts[3].split(",") if x]]
            normalized = sorted({normalize(name) for name in names if normalize(name)})
            rows.append({
                "geonameid": parts[0],
                "name": parts[1],
                "asciiname": parts[2],
                "latitude": float(parts[4]),
                "longitude": float(parts[5]),
                "feature_class": parts[6],
                "feature_code": parts[7],
                "population": int(parts[14] or 0),
                "normalized_names": normalized,
            })
    return rows


def top_candidates(target: str, rows, limit=5):
    target_norm = normalize(target)
    candidates = []
    for row in rows:
        score = max((SequenceMatcher(None, target_norm, name).ratio() for name in row["normalized_names"]), default=0)
        if score < 0.55:
            continue
        candidates.append({
            "score": round(score, 4),
            "geonameid": row["geonameid"],
            "name": row["name"],
            "asciiname": row["asciiname"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "feature_class": row["feature_class"],
            "feature_code": row["feature_code"],
            "population": row["population"],
        })
    candidates.sort(key=lambda item: (item["score"], item["population"]), reverse=True)
    return candidates[:limit]


def main():
    points = json.loads(POINTS_PATH.read_text(encoding="utf-8"))
    rows = download_rows()
    report = []
    for point in points:
        if point["latitude"] is not None:
            continue
        report.append({
            "slug": point["slug"],
            "name_ar": point["name_ar"],
            "name_en": point["name_en"],
            "candidates": top_candidates(point["name_en"], rows),
        })

    OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote candidates for {len(report)} unmatched municipalities.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Export normalized wardriving observations to GeoJSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

PROPERTY_FIELDS = [
    "timestamp",
    "source",
    "ssid",
    "bssid",
    "channel",
    "frequency",
    "rssi",
    "security",
]


def valid_coords(lat, lon) -> bool:
    try:
        if pd.isna(lat) or pd.isna(lon):
            return False
        lat_f = float(lat)
        lon_f = float(lon)
    except (TypeError, ValueError):
        return False
    if lat_f == 0.0 and lon_f == 0.0:
        return False
    return -90.0 <= lat_f <= 90.0 and -180.0 <= lon_f <= 180.0


def to_feature(row: pd.Series) -> dict:
    props = {}
    for field in PROPERTY_FIELDS:
        value = row.get(field)
        if pd.isna(value):
            props[field] = None
        elif field in {"channel", "frequency", "rssi"}:
            try:
                props[field] = int(value) if field != "rssi" else float(value)
            except (TypeError, ValueError):
                props[field] = value
        else:
            props[field] = value if not isinstance(value, str) else value
    return {
        "type": "Feature",
        "properties": props,
        "geometry": {
            "type": "Point",
            "coordinates": [float(row["longitude"]), float(row["latitude"])],
        },
    }


def export_geojson(input_path: Path, output_path: Path) -> int:
    if not input_path.is_file():
        print(f"[!] File not found: {input_path}", file=sys.stderr)
        return 1

    try:
        df = pd.read_csv(input_path)
    except Exception as exc:  # noqa: BLE001
        print(f"[!] Failed to read CSV: {exc}", file=sys.stderr)
        return 1

    features = []
    skipped = 0
    for _, row in df.iterrows():
        if not valid_coords(row.get("latitude"), row.get("longitude")):
            skipped += 1
            continue
        features.append(to_feature(row))

    collection = {"type": "FeatureCollection", "features": features}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(collection, indent=2), encoding="utf-8")

    print(f"[+] Input observations: {len(df)}")
    print(f"[+] Features exported: {len(features)}")
    print(f"[+] Skipped without GPS: {skipped}")
    print(f"[+] Saved: {output_path}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export wardriving CSV rows with GPS to a GeoJSON FeatureCollection."
    )
    parser.add_argument("input", type=Path, help="Input CSV path")
    parser.add_argument("output", type=Path, help="Output GeoJSON path")
    args = parser.parse_args()
    sys.exit(export_geojson(args.input, args.output))


if __name__ == "__main__":
    main()

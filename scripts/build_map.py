#!/usr/bin/env python3
"""Build a local Folium HTML map from wardriving observations."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

try:
    import folium
    from folium.plugins import MarkerCluster
except ImportError:  # pragma: no cover
    folium = None
    MarkerCluster = None


def valid_gps_mask(df: pd.DataFrame) -> pd.Series:
    lat = pd.to_numeric(df.get("latitude"), errors="coerce")
    lon = pd.to_numeric(df.get("longitude"), errors="coerce")
    missing = lat.isna() | lon.isna() | ((lat == 0.0) & (lon == 0.0))
    in_range = lat.between(-90, 90) & lon.between(-180, 180)
    return (~missing) & in_range


def build_map(input_path: Path, output_path: Path) -> int:
    if folium is None:
        print("[!] folium is not installed. Run: pip install -r requirements.txt", file=sys.stderr)
        return 1

    if not input_path.is_file():
        print(f"[!] File not found: {input_path}", file=sys.stderr)
        return 1

    try:
        df = pd.read_csv(input_path)
    except Exception as exc:  # noqa: BLE001
        print(f"[!] Failed to read CSV: {exc}", file=sys.stderr)
        return 1

    mask = valid_gps_mask(df)
    geo = df.loc[mask].copy()
    if geo.empty:
        print("[!] No valid GPS observations found; cannot build map.", file=sys.stderr)
        return 1

    geo["latitude"] = pd.to_numeric(geo["latitude"], errors="coerce")
    geo["longitude"] = pd.to_numeric(geo["longitude"], errors="coerce")
    center_lat = float(geo["latitude"].mean())
    center_lon = float(geo["longitude"].mean())

    # tile.openstreetmap.org blocks heavy/local file usage (403); use the workshop tile server.
    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=14, tiles=None)
    folium.TileLayer(
        tiles="https://wardriving-ctf.rf-village-mx.com/map-tiles/{z}/{x}/{y}.png",
        attr="Wardriving CTF - RF Village MX",
        name="CTF",
    ).add_to(fmap)
    cluster = MarkerCluster().add_to(fmap)

    for _, row in geo.iterrows():
        popup = (
            f"<b>SSID:</b> {row.get('ssid', '')}<br>"
            f"<b>BSSID:</b> {row.get('bssid', '')}<br>"
            f"<b>Channel:</b> {row.get('channel', '')}<br>"
            f"<b>RSSI:</b> {row.get('rssi', '')}<br>"
            f"<b>Security:</b> {row.get('security', '')}<br>"
            f"<b>Source:</b> {row.get('source', '')}"
        )
        folium.Marker(
            location=[float(row["latitude"]), float(row["longitude"])],
            popup=folium.Popup(popup, max_width=280),
            tooltip=str(row.get("ssid", "")),
        ).add_to(cluster)

    folium.LayerControl().add_to(fmap)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fmap.save(str(output_path))
    print(f"[+] Markers: {len(geo)}")
    print(f"[+] Saved: {output_path}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a local Folium HTML map from wardriving CSV observations."
    )
    parser.add_argument("input", type=Path, help="Input CSV path")
    parser.add_argument("output", type=Path, help="Output HTML path")
    args = parser.parse_args()
    sys.exit(build_map(args.input, args.output))


if __name__ == "__main__":
    main()

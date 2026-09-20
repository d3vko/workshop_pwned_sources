#!/usr/bin/env python3
"""Analyze a normalized wardriving dataset and print investigation summaries."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

HIDDEN_VALUES = {"<hidden>", "hidden"}


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.is_file():
        print(f"[!] File not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        return pd.read_csv(path)
    except Exception as exc:  # noqa: BLE001
        print(f"[!] Failed to read CSV: {exc}", file=sys.stderr)
        sys.exit(1)


def valid_gps_mask(df: pd.DataFrame) -> pd.Series:
    lat = pd.to_numeric(df.get("latitude"), errors="coerce")
    lon = pd.to_numeric(df.get("longitude"), errors="coerce")
    missing = lat.isna() | lon.isna() | ((lat == 0.0) & (lon == 0.0))
    in_range = lat.between(-90, 90) & lon.between(-180, 180)
    return (~missing) & in_range


def analyze(df: pd.DataFrame, top: int = 10) -> dict:
    ssid = df["ssid"].astype(str).str.strip()
    bssid = df["bssid"].astype(str).str.upper()
    security = df["security"].astype(str).str.upper()
    channel = pd.to_numeric(df["channel"], errors="coerce")
    rssi = pd.to_numeric(df["rssi"], errors="coerce")
    gps_ok = valid_gps_mask(df)

    hidden = ssid.str.lower().isin(HIDDEN_VALUES) | (ssid == "<hidden>")
    sec_counts = security.value_counts().to_dict()
    channel_counts = channel.dropna().astype(int).value_counts().head(top)

    strongest_idx = rssi.idxmax() if rssi.notna().any() else None
    weakest_idx = rssi.idxmin() if rssi.notna().any() else None

    bssid_counts = bssid.value_counts().head(top)
    ssid_to_bssids = (
        df.assign(ssid=ssid, bssid=bssid)
        .groupby("ssid")["bssid"]
        .nunique()
        .sort_values(ascending=False)
    )
    multi_ssid = ssid_to_bssids[ssid_to_bssids > 1]

    work = df.copy()
    work["_bssid"] = bssid
    work["_lat"] = pd.to_numeric(work.get("latitude"), errors="coerce")
    work["_lon"] = pd.to_numeric(work.get("longitude"), errors="coerce")
    work = work[gps_ok]
    work["_coord"] = list(zip(work["_lat"].round(5), work["_lon"].round(5)))
    coords_per_bssid = work.groupby("_bssid")["_coord"].nunique().sort_values(ascending=False)

    result = {
        "observations": int(len(df)),
        "unique_bssids": int(bssid.nunique()),
        "unique_ssids": int(ssid.nunique()),
        "hidden_ssids": int(ssid[hidden].nunique()) if hidden.any() else 0,
        "gps_observations": int(gps_ok.sum()),
        "security": {k: int(v) for k, v in sec_counts.items()},
        "top_channels": {str(int(k)): int(v) for k, v in channel_counts.items()},
        "strongest": None,
        "weakest_rssi": float(rssi.min()) if rssi.notna().any() else None,
        "most_observed_bssids": {k: int(v) for k, v in bssid_counts.items()},
        "ssids_multiple_bssids": {k: int(v) for k, v in multi_ssid.head(top).items()},
        "bssid_most_locations": None,
        "unique_coords_per_bssid_top": {k: int(v) for k, v in coords_per_bssid.head(top).items()},
    }

    if strongest_idx is not None:
        row = df.loc[strongest_idx]
        result["strongest"] = {
            "ssid": str(row.get("ssid")),
            "bssid": str(row.get("bssid")).upper(),
            "rssi": float(rssi.loc[strongest_idx]),
            "channel": int(channel.loc[strongest_idx]) if pd.notna(channel.loc[strongest_idx]) else None,
        }

    if len(coords_per_bssid):
        top_b = coords_per_bssid.index[0]
        result["bssid_most_locations"] = {
            "bssid": top_b,
            "distinct_locations": int(coords_per_bssid.iloc[0]),
        }

    return result


def print_report(result: dict, top: int) -> None:
    print("Wireless Dataset Summary")
    print("========================")
    print()
    print(f"Observations: {result['observations']}")
    print(f"Unique BSSIDs: {result['unique_bssids']}")
    print(f"Unique SSIDs: {result['unique_ssids']}")
    print(f"Hidden SSIDs: {result['hidden_ssids']}")
    print(f"GPS observations: {result['gps_observations']}")
    print()
    print("Security:")
    for label in ["WPA2", "WPA3", "OPEN", "WPA", "WEP", "UNKNOWN"]:
        if label in result["security"]:
            print(f"{label}: {result['security'][label]}")
    for label, count in result["security"].items():
        if label not in {"WPA2", "WPA3", "OPEN", "WPA", "WEP", "UNKNOWN"}:
            print(f"{label}: {count}")
    print()
    print("Top Channels:")
    for ch, count in result["top_channels"].items():
        print(f"  {ch}: {count}")
    print()
    print("Strongest Observation:")
    if result["strongest"]:
        s = result["strongest"]
        print(f"SSID: {s['ssid']}")
        print(f"BSSID: {s['bssid']}")
        print(f"RSSI: {s['rssi']}")
        print(f"Channel: {s['channel']}")
    else:
        print("(none)")
    if result["weakest_rssi"] is not None:
        print(f"Weakest RSSI: {result['weakest_rssi']}")
    print()
    print("Most Observed BSSIDs:")
    for bssid, count in list(result["most_observed_bssids"].items())[:top]:
        print(f"  {bssid}: {count}")
    print()
    print("SSIDs with Multiple BSSIDs:")
    if result["ssids_multiple_bssids"]:
        for ssid, count in result["ssids_multiple_bssids"].items():
            print(f"  {ssid}: {count} BSSIDs")
    else:
        print("  (none)")
    print()
    print("BSSID with Most Distinct Locations:")
    if result["bssid_most_locations"]:
        m = result["bssid_most_locations"]
        print(f"  {m['bssid']}: {m['distinct_locations']} locations")
    else:
        print("  (none)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize a normalized wardriving CSV for investigation questions."
    )
    parser.add_argument("input", type=Path, help="Normalized or challenge CSV path")
    parser.add_argument("--top", type=int, default=10, help="Top-N lists size (default: 10)")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = parser.parse_args()

    df = load_dataset(args.input)
    result = analyze(df, top=args.top)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_report(result, top=args.top)


if __name__ == "__main__":
    main()

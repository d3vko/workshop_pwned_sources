#!/usr/bin/env python3
"""Validate a normalized wardriving dataset against the common schema."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

REQUIRED = [
    "timestamp",
    "source",
    "ssid",
    "bssid",
    "channel",
    "frequency",
    "rssi",
    "security",
    "latitude",
    "longitude",
]

KNOWN_SECURITY = {"OPEN", "WEP", "WPA", "WPA2", "WPA3", "UNKNOWN"}
BSSID_RE = re.compile(r"^([0-9A-F]{2}:){5}[0-9A-F]{2}$")


def is_missing_coord(lat, lon) -> bool:
    if pd.isna(lat) or pd.isna(lon):
        return True
    try:
        return float(lat) == 0.0 and float(lon) == 0.0
    except (TypeError, ValueError):
        return True


def validate(path: Path) -> int:
    if not path.is_file():
        print(f"[!] File not found: {path}", file=sys.stderr)
        return 1

    try:
        df = pd.read_csv(path)
    except Exception as exc:  # noqa: BLE001
        print(f"[!] Failed to read CSV: {exc}", file=sys.stderr)
        return 1

    print("Dataset validation")
    print("------------------")
    print(f"Rows: {len(df)}")

    missing = [c for c in REQUIRED if c not in df.columns]
    schema_ok = not missing
    print(f"Schema: {'OK' if schema_ok else 'FAIL'}")
    if missing:
        print(f"  Missing columns: {missing}")
        print()
        print("RESULT: INVALID")
        return 1

    issues: list[str] = []

    # BSSID format
    bssid_bad = ~df["bssid"].astype(str).str.upper().str.match(BSSID_RE.pattern)
    bssid_ok = not bool(bssid_bad.any())
    print(f"BSSID format: {'OK' if bssid_ok else 'FAIL'}")
    if not bssid_ok:
        issues.append(f"Invalid BSSID rows: {int(bssid_bad.sum())}")

    # Numeric fields
    channel_ok = pd.to_numeric(df["channel"], errors="coerce").notna().all()
    freq_ok = pd.to_numeric(df["frequency"], errors="coerce").notna().all()
    rssi_num = pd.to_numeric(df["rssi"], errors="coerce")
    rssi_ok = rssi_num.notna().all()
    print(f"Channel numeric: {'OK' if channel_ok else 'FAIL'}")
    print(f"Frequency numeric: {'OK' if freq_ok else 'FAIL'}")
    print(f"RSSI: {'OK' if rssi_ok else 'FAIL'}")
    if not channel_ok:
        issues.append("Non-numeric channel values")
    if not freq_ok:
        issues.append("Non-numeric frequency values")
    if not rssi_ok:
        issues.append("Non-numeric RSSI values")

    # Coordinates
    valid_gps = 0
    missing_gps = 0
    bad_gps = 0
    for _, row in df.iterrows():
        lat, lon = row["latitude"], row["longitude"]
        if is_missing_coord(lat, lon):
            missing_gps += 1
            continue
        try:
            lat_f, lon_f = float(lat), float(lon)
        except (TypeError, ValueError):
            bad_gps += 1
            continue
        if -90.0 <= lat_f <= 90.0 and -180.0 <= lon_f <= 180.0:
            valid_gps += 1
        else:
            bad_gps += 1
    print(f"Coordinates: {valid_gps} valid / {missing_gps} missing" + (f" / {bad_gps} invalid" if bad_gps else ""))

    # Timestamps
    ts = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    ts_ok = ts.notna().all()
    print(f"Timestamp: {'OK' if ts_ok else 'FAIL'}")
    if not ts_ok:
        issues.append(f"Unparseable timestamps: {int(ts.isna().sum())}")

    # Security labels
    sec = df["security"].astype(str).str.upper()
    sec_ok = sec.isin(KNOWN_SECURITY).all()
    print(f"Security labels: {'OK' if sec_ok else 'FAIL'}")
    if not sec_ok:
        bad = sorted(set(sec[~sec.isin(KNOWN_SECURITY)].tolist()))
        issues.append(f"Unknown security labels: {bad}")

    print()
    hard_fail = (not schema_ok) or (not bssid_ok) or (not channel_ok) or (not freq_ok) or (not rssi_ok) or (not ts_ok) or (not sec_ok) or bad_gps > 0
    if hard_fail:
        for issue in issues:
            print(f"[!] {issue}")
        if bad_gps:
            print(f"[!] Invalid coordinate rows: {bad_gps}")
        print("RESULT: INVALID")
        return 1

    print("RESULT: VALID")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a normalized wardriving CSV against the common schema."
    )
    parser.add_argument("input", type=Path, help="Normalized CSV path")
    args = parser.parse_args()
    sys.exit(validate(args.input))


if __name__ == "__main__":
    main()

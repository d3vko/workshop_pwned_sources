#!/usr/bin/env python3
"""Inspect an unknown wardriving CSV before normalization."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

BSSID_CANDIDATES = {"bssid", "mac", "device_mac", "ap_mac", "bssid_mac"}
SSID_CANDIDATES = {"ssid", "device_name", "essid", "name"}


def find_column(columns: list[str], candidates: set[str]) -> str | None:
    lower_map = {c.lower(): c for c in columns}
    for cand in candidates:
        if cand in lower_map:
            return lower_map[cand]
    return None


def inspect(path: Path) -> None:
    if not path.is_file():
        print(f"[!] File not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        df = pd.read_csv(path)
    except Exception as exc:  # noqa: BLE001
        print(f"[!] Failed to read CSV: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"File: {path.name}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print()
    print("Columns:")
    for col in df.columns:
        print(f"- {col}")

    print()
    print("Dtypes:")
    for col, dtype in df.dtypes.items():
        print(f"- {col}: {dtype}")

    print()
    print("Null counts:")
    nulls = df.isna().sum()
    for col, count in nulls.items():
        print(f"- {col}: {int(count)}")

    ssid_col = find_column(list(df.columns), SSID_CANDIDATES)
    bssid_col = find_column(list(df.columns), BSSID_CANDIDATES)
    if ssid_col:
        unique_ssids = df[ssid_col].dropna().astype(str).str.strip().nunique()
        print()
        print(f"Unique SSIDs ({ssid_col}): {unique_ssids}")
    if bssid_col:
        unique_bssids = df[bssid_col].dropna().astype(str).str.strip().str.upper().nunique()
        print()
        print(f"Unique BSSIDs ({bssid_col}): {unique_bssids}")

    print()
    print("Preview:")
    print(df.head(5).to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect a wardriving CSV: columns, dtypes, nulls, and preview."
    )
    parser.add_argument("input", type=Path, help="Path to a CSV file")
    args = parser.parse_args()
    inspect(args.input)


if __name__ == "__main__":
    main()

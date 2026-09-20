#!/usr/bin/env python3
"""Normalize heterogeneous wardriving CSVs into one common schema."""

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

CHANNEL_FREQ_24 = {
    1: 2412,
    2: 2417,
    3: 2422,
    4: 2427,
    5: 2432,
    6: 2437,
    7: 2442,
    8: 2447,
    9: 2452,
    10: 2457,
    11: 2462,
    12: 2467,
    13: 2472,
    14: 2484,
}

CHANNEL_FREQ_5 = {
    36: 5180,
    40: 5200,
    44: 5220,
    48: 5240,
    149: 5745,
    153: 5765,
    157: 5785,
    161: 5805,
}

SECURITY_MAP = {
    "open": "OPEN",
    "none": "OPEN",
    "opn": "OPEN",
    "wep": "WEP",
    "wpa": "WPA",
    "wpa1": "WPA",
    "wpa2": "WPA2",
    "wpa/wpa2": "WPA2",
    "wpa2/wpa3": "WPA2",
    "wpa3": "WPA3",
    "unknown": "UNKNOWN",
    "": "UNKNOWN",
}

SIGNATURES = {
    "marauder": {"MAC", "SSID", "AuthMode", "FirstSeen", "Channel", "RSSI", "Latitude", "Longitude"},
    "minino": {"timestamp", "bssid", "ssid", "channel", "rssi", "security", "lat", "lon"},
    "kismet": {
        "first_time",
        "device_mac",
        "device_name",
        "channel",
        "frequency",
        "signal_dbm",
        "crypt",
        "lat",
        "lon",
    },
    "generic": set(REQUIRED),
}

BSSID_RE = re.compile(r"^([0-9A-F]{2}:){5}[0-9A-F]{2}$")


def channel_to_frequency(channel) -> float | None:
    if channel is None or (isinstance(channel, float) and pd.isna(channel)):
        return None
    try:
        ch = int(channel)
    except (TypeError, ValueError):
        return None
    if ch in CHANNEL_FREQ_24:
        return float(CHANNEL_FREQ_24[ch])
    if ch in CHANNEL_FREQ_5:
        return float(CHANNEL_FREQ_5[ch])
    return None


def normalize_security(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "UNKNOWN"
    key = str(value).strip().lower()
    if key in SECURITY_MAP:
        return SECURITY_MAP[key]
    upper = str(value).strip().upper()
    if upper in {"OPEN", "WEP", "WPA", "WPA2", "WPA3", "UNKNOWN"}:
        return upper
    return "UNKNOWN"


def clean_ssid(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "<hidden>"
    text = str(value).strip()
    if text == "" or text.lower() in {"hidden", "<hidden>", "null", "none"}:
        return "<hidden>"
    return text


def clean_bssid(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip().upper().replace("-", ":")
    return text


def clean_coordinates(lat, lon) -> tuple[float | None, float | None]:
    try:
        if lat is None or lon is None or pd.isna(lat) or pd.isna(lon):
            return None, None
        lat_f = float(lat)
        lon_f = float(lon)
    except (TypeError, ValueError):
        return None, None
    if lat_f == 0.0 and lon_f == 0.0:
        return None, None
    if not (-90.0 <= lat_f <= 90.0 and -180.0 <= lon_f <= 180.0):
        return None, None
    return lat_f, lon_f


def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def validate_columns(df: pd.DataFrame, required: list[str]) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def detect_source(columns: list[str]) -> str:
    cols = set(columns)
    matches = [name for name, sig in SIGNATURES.items() if sig.issubset(cols)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        # Prefer exact generic when all required present and no sensor-specific extras
        if "generic" in matches and cols == SIGNATURES["generic"]:
            return "generic"
        raise ValueError(f"Ambiguous format; matches: {matches}")
    raise ValueError(f"Unknown CSV format. Columns: {sorted(cols)}")


def finalize(df: pd.DataFrame, source: str) -> pd.DataFrame:
    out = df.copy()
    out["source"] = source
    out["ssid"] = out["ssid"].map(clean_ssid)
    out["bssid"] = out["bssid"].map(clean_bssid)
    out["security"] = out["security"].map(normalize_security)
    out["channel"] = to_numeric(out["channel"])
    out["rssi"] = to_numeric(out["rssi"])

    if "frequency" not in out.columns:
        out["frequency"] = None
    out["frequency"] = to_numeric(out["frequency"])
    missing_freq = out["frequency"].isna()
    out.loc[missing_freq, "frequency"] = out.loc[missing_freq, "channel"].map(channel_to_frequency)

    coords = out.apply(
        lambda r: clean_coordinates(r.get("latitude"), r.get("longitude")),
        axis=1,
        result_type="expand",
    )
    out["latitude"] = coords[0]
    out["longitude"] = coords[1]

    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True, errors="coerce")
    out["timestamp"] = out["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    validate_columns(out, REQUIRED)
    return out[REQUIRED]


def normalize_marauder(df: pd.DataFrame) -> pd.DataFrame:
    mapped = pd.DataFrame(
        {
            "timestamp": df["FirstSeen"],
            "ssid": df["SSID"],
            "bssid": df["MAC"],
            "channel": df["Channel"],
            "frequency": None,
            "rssi": df["RSSI"],
            "security": df["AuthMode"],
            "latitude": df["Latitude"],
            "longitude": df["Longitude"],
        }
    )
    return finalize(mapped, "marauder")


def normalize_minino(df: pd.DataFrame) -> pd.DataFrame:
    mapped = pd.DataFrame(
        {
            "timestamp": df["timestamp"],
            "ssid": df["ssid"],
            "bssid": df["bssid"],
            "channel": df["channel"],
            "frequency": None,
            "rssi": df["rssi"],
            "security": df["security"],
            "latitude": df["lat"],
            "longitude": df["lon"],
        }
    )
    return finalize(mapped, "minino")


def normalize_kismet(df: pd.DataFrame) -> pd.DataFrame:
    mapped = pd.DataFrame(
        {
            "timestamp": df["first_time"],
            "ssid": df["device_name"],
            "bssid": df["device_mac"],
            "channel": df["channel"],
            "frequency": df["frequency"],
            "rssi": df["signal_dbm"],
            "security": df["crypt"],
            "latitude": df["lat"],
            "longitude": df["lon"],
        }
    )
    return finalize(mapped, "kismet")


def normalize_generic(df: pd.DataFrame) -> pd.DataFrame:
    mapped = df.copy()
    # Keep provided source if present, else label generic
    source = "generic"
    if "source" in mapped.columns and mapped["source"].notna().any():
        # Still tag as generic adapter; preserve first non-null source string if uniform
        vals = mapped["source"].dropna().astype(str).unique()
        if len(vals) == 1:
            source = vals[0]
    return finalize(mapped, source)


NORMALIZERS = {
    "marauder": normalize_marauder,
    "minino": normalize_minino,
    "kismet": normalize_kismet,
    "generic": normalize_generic,
}


def normalize_file(path: Path, source: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if source == "auto":
        source = detect_source(list(df.columns))
    if source not in NORMALIZERS:
        raise ValueError(f"Unsupported source: {source}")
    return NORMALIZERS[source](df)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize one or more wardriving CSVs into the common schema."
    )
    parser.add_argument(
        "--source",
        required=True,
        choices=["auto", "marauder", "minino", "kismet", "generic"],
        help="Input format, or auto to detect from columns",
    )
    parser.add_argument(
        "--input",
        nargs="+",
        type=Path,
        required=True,
        help="One or more input CSV paths",
    )
    parser.add_argument("--output", type=Path, required=True, help="Output CSV path")
    args = parser.parse_args()

    frames: list[pd.DataFrame] = []
    total_in = 0
    try:
        for path in args.input:
            if not path.is_file():
                print(f"[!] File not found: {path}", file=sys.stderr)
                sys.exit(1)
            raw = pd.read_csv(path)
            total_in += len(raw)
            frames.append(normalize_file(path, args.source))
    except Exception as exc:  # noqa: BLE001
        print(f"[!] Normalization failed: {exc}", file=sys.stderr)
        sys.exit(1)

    out = pd.concat(frames, ignore_index=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, index=False)

    missing_gps = out["latitude"].isna().sum()
    print(f"[+] Input rows: {total_in}")
    print(f"[+] Output rows: {len(out)}")
    print(f"[+] Unique BSSIDs: {out['bssid'].nunique()}")
    print(f"[+] Missing GPS: {missing_gps}")
    print(f"[+] Saved: {args.output}")


if __name__ == "__main__":
    main()

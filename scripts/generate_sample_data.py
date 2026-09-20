#!/usr/bin/env python3
"""Generate synthetic wardriving sample and challenge datasets."""

from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Synthetic GPS clusters (not real locations)
ZONES = {
    "alpha": (1.2345678, -9.8765432),
    "beta": (1.2456789, -9.8654321),
    "gamma": (1.2234567, -9.8876543),
    "delta": (1.2567890, -9.8543210),
}

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

LAB_SSIDS = [
    "LAB-ALPHA",
    "LAB-BETA",
    "LAB-GAMMA",
    "LAB-DELTA",
    "LAB-ECHO",
    "LAB-FOXTROT",
    "LAB-GUEST",
    "LAB-IOT",
    "LAB-LABORATORY",
    "LAB-MESH-A",
    "LAB-MESH-B",
    "LAB-OFFICE",
    "LAB-SENSOR",
    "LAB-TRAINING",
    "LAB-WIFI-01",
    "LAB-WIFI-02",
    "LAB-ZONE-NORTH",
    "LAB-ZONE-SOUTH",
    "LAB-CORRIDOR",
    "LAB-BASEMENT",
    "<hidden>",
]


def mac_from_parts(prefix: int, n: int) -> str:
    """Build a locally administered synthetic MAC (02:xx:xx:xx:xx:xx)."""
    return f"02:{prefix:02X}:{(n >> 24) & 0xFF:02X}:{(n >> 16) & 0xFF:02X}:{(n >> 8) & 0xFF:02X}:{n & 0xFF:02X}"


def jitter(coord: float, scale: float = 0.0008) -> float:
    return round(coord + random.uniform(-scale, scale), 7)


def maybe_missing_gps(lat: float, lon: float, miss_rate: float = 0.08) -> tuple[str, str]:
    if random.random() < miss_rate:
        choice = random.choice(["empty", "zero"])
        if choice == "empty":
            return "", ""
        return "0.0", "0.0"
    return f"{jitter(lat):.7f}", f"{jitter(lon):.7f}"


def pick_security(rng_weights: bool = True) -> str:
    options = ["WPA2", "WPA3", "OPEN", "UNKNOWN", "WPA", "WEP"]
    if rng_weights:
        return random.choices(options, weights=[45, 20, 15, 12, 5, 3], k=1)[0]
    return random.choice(options)


def iso_ts(base: datetime, offset_seconds: int) -> str:
    return (base + timedelta(seconds=offset_seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_marauder(base: datetime) -> list[dict]:
    rows: list[dict] = []
    bssids = [mac_from_parts(1, i) for i in range(1, 9)]
    for i in range(24):
        bssid = bssids[i % len(bssids)]
        ssid = LAB_SSIDS[i % 10]
        if i % 7 == 0:
            ssid = "<hidden>"
        zone = ZONES["alpha" if i % 2 == 0 else "beta"]
        lat, lon = maybe_missing_gps(*zone, miss_rate=0.1)
        channel = random.choice([1, 6, 11, 36])
        rows.append(
            {
                "MAC": bssid,
                "SSID": ssid,
                "AuthMode": pick_security(),
                "FirstSeen": iso_ts(base, i * 3),
                "Channel": channel,
                "RSSI": random.randint(-85, -35),
                "Latitude": lat,
                "Longitude": lon,
            }
        )
    return rows


def generate_minino(base: datetime) -> list[dict]:
    rows: list[dict] = []
    bssids = [mac_from_parts(2, i) for i in range(1, 9)]
    for i in range(24):
        bssid = bssids[i % len(bssids)]
        ssid = LAB_SSIDS[(i + 3) % 12]
        if i % 8 == 0:
            ssid = "<hidden>"
        zone = ZONES["beta" if i % 2 == 0 else "gamma"]
        lat, lon = maybe_missing_gps(*zone)
        channel = random.choice([1, 6, 11, 40])
        rows.append(
            {
                "timestamp": iso_ts(base, 60 + i * 4),
                "bssid": bssid.lower(),
                "ssid": f" {ssid} " if i % 5 == 0 else ssid,
                "channel": channel,
                "rssi": random.randint(-88, -32),
                "security": pick_security(),
                "lat": lat,
                "lon": lon,
            }
        )
    return rows


def generate_kismet(base: datetime) -> list[dict]:
    rows: list[dict] = []
    bssids = [mac_from_parts(3, i) for i in range(1, 9)]
    for i in range(24):
        bssid = bssids[i % len(bssids)]
        ssid = LAB_SSIDS[(i + 5) % 14]
        if i % 9 == 0:
            ssid = "<hidden>"
        zone = ZONES["gamma" if i % 2 == 0 else "delta"]
        lat, lon = maybe_missing_gps(*zone)
        channel = random.choice([1, 6, 11, 44, 149])
        freq = CHANNEL_FREQ_24.get(channel) or CHANNEL_FREQ_5.get(channel, "")
        rows.append(
            {
                "first_time": iso_ts(base, 120 + i * 5),
                "device_mac": bssid,
                "device_name": ssid,
                "channel": channel,
                "frequency": freq,
                "signal_dbm": random.randint(-90, -30),
                "crypt": pick_security(),
                "lat": lat,
                "lon": lon,
            }
        )
    return rows


def generate_generic(base: datetime) -> list[dict]:
    rows: list[dict] = []
    bssids = [mac_from_parts(4, i) for i in range(1, 9)]
    for i in range(24):
        bssid = bssids[i % len(bssids)]
        ssid = LAB_SSIDS[(i + 7) % 16]
        if i % 6 == 0:
            ssid = "<hidden>"
        zone = ZONES["delta" if i % 2 == 0 else "alpha"]
        lat, lon = maybe_missing_gps(*zone)
        channel = random.choice([1, 6, 11, 48, 153])
        freq = CHANNEL_FREQ_24.get(channel) or CHANNEL_FREQ_5.get(channel, 0)
        rows.append(
            {
                "timestamp": iso_ts(base, 180 + i * 2),
                "source": "generic",
                "ssid": ssid,
                "bssid": bssid,
                "channel": channel,
                "frequency": freq,
                "rssi": random.randint(-87, -34),
                "security": pick_security(),
                "latitude": lat,
                "longitude": lon,
            }
        )
    return rows


def generate_challenge(base: datetime, n_obs: int = 2000) -> list[dict]:
    """Build a larger synthetic investigation dataset."""
    n_bssids = 60
    ssids = LAB_SSIDS + [f"LAB-NET-{i:02d}" for i in range(1, 31)]
    # Map several SSIDs to multiple BSSIDs (same deployment hypothesis)
    multi_ssid_groups = {
        "LAB-MESH-A": list(range(1, 5)),
        "LAB-MESH-B": list(range(5, 9)),
        "LAB-OFFICE": list(range(9, 13)),
        "LAB-CORRIDOR": list(range(13, 16)),
    }

    bssid_meta: list[dict] = []
    for i in range(1, n_bssids + 1):
        bssid = mac_from_parts(10, i)
        assigned = None
        for ssid, idxs in multi_ssid_groups.items():
            if i in idxs:
                assigned = ssid
                break
        if assigned is None:
            if i % 11 == 0:
                assigned = "<hidden>"
            else:
                assigned = ssids[i % len(ssids)]
        zone_name = list(ZONES.keys())[i % len(ZONES)]
        channel = random.choices(
            [1, 6, 11, 36, 40, 44, 149, 153],
            weights=[25, 25, 25, 6, 5, 5, 5, 4],
            k=1,
        )[0]
        bssid_meta.append(
            {
                "bssid": bssid,
                "ssid": assigned,
                "zone": zone_name,
                "channel": channel,
                "security": pick_security(),
            }
        )

    # Some BSSIDs are "mobile" / multi-location heavy
    heavy = {m["bssid"] for m in random.sample(bssid_meta, 8)}

    rows: list[dict] = []
    for i in range(n_obs):
        meta = random.choice(bssid_meta)
        zone = ZONES[meta["zone"]]
        if meta["bssid"] in heavy:
            # wander across zones
            zone = random.choice(list(ZONES.values()))
            lat, lon = maybe_missing_gps(*zone, miss_rate=0.03)
        else:
            lat, lon = maybe_missing_gps(*zone, miss_rate=0.06)

        channel = meta["channel"]
        if random.random() < 0.15:
            channel = random.choice([1, 6, 11])
        freq = CHANNEL_FREQ_24.get(channel) or CHANNEL_FREQ_5.get(channel, 0)
        rows.append(
            {
                "timestamp": iso_ts(base, i * 7),
                "source": random.choice(["marauder", "minino", "kismet", "generic"]),
                "ssid": meta["ssid"],
                "bssid": meta["bssid"],
                "channel": channel,
                "frequency": freq,
                "rssi": random.randint(-90, -30),
                "security": meta["security"] if random.random() > 0.05 else pick_security(),
                "latitude": lat,
                "longitude": lon,
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate synthetic wardriving sample and challenge CSV datasets."
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    args = parser.parse_args()

    random.seed(args.seed)
    base = datetime(2026, 9, 20, 10, 0, 0, tzinfo=timezone.utc)

    paths = {
        ROOT / "data/raw/marauder/sample_marauder.csv": (
            ["MAC", "SSID", "AuthMode", "FirstSeen", "Channel", "RSSI", "Latitude", "Longitude"],
            generate_marauder(base),
        ),
        ROOT / "data/raw/minino/sample_minino.csv": (
            ["timestamp", "bssid", "ssid", "channel", "rssi", "security", "lat", "lon"],
            generate_minino(base),
        ),
        ROOT / "data/raw/kismet/sample_kismet.csv": (
            [
                "first_time",
                "device_mac",
                "device_name",
                "channel",
                "frequency",
                "signal_dbm",
                "crypt",
                "lat",
                "lon",
            ],
            generate_kismet(base),
        ),
        ROOT / "data/raw/generic/sample_generic.csv": (
            [
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
            ],
            generate_generic(base),
        ),
        ROOT / "data/challenge/challenge_wifi.csv": (
            [
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
            ],
            generate_challenge(base),
        ),
    }

    print("Generated:")
    for path, (fields, rows) in paths.items():
        write_csv(path, fields, rows)
        print(f"  {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

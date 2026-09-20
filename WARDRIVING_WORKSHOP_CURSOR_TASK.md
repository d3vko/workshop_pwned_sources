# Cursor Task — Wardriving Workshop Lab Material

## Project

**From Signals to Intelligence: Building Your Wardriving Arsenal**

Create a complete educational repository for a 3-hour wardriving workshop.

The repository must support this flow:

```text
Signals
  ↓
Capture
  ↓
Raw Data
  ↓
Normalization
  ↓
Analysis
  ↓
Geospatial Export
  ↓
Intelligence
```

The repository must work even when participants do not have specialized hardware.

All bundled sample datasets must be **synthetic**. Do not include real third-party SSIDs, real BSSIDs, credentials, handshakes, packet captures, or personal locations.

---

# 1. Workshop goals

Participants should be able to:

1. Inspect a raw Wi-Fi observation dataset.
2. Understand common wardriving fields.
3. Normalize different source formats into one schema.
4. Validate normalized data.
5. Perform basic analysis with Python and Pandas.
6. Export observations to GeoJSON.
7. Generate a local HTML map.
8. Answer investigation questions from a larger challenge dataset.

The exercises focus on passive metadata observation.

Do not implement:

- deauthentication;
- credential attacks;
- handshake cracking;
- packet injection;
- network intrusion;
- automated exploitation.

---

# 2. Target environment

Support:

- Linux
- macOS
- Windows
- Python 3.10+

Dependencies:

```txt
pandas>=2.0
folium>=0.16
```

Use the Python standard library when practical.

Code comments must be in English.

Scripts must be compact, readable, and easy to explain live.

---

# 3. Repository structure

```text
wardriving-workshop/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/
│   │   ├── marauder/
│   │   │   └── sample_marauder.csv
│   │   ├── minino/
│   │   │   └── sample_minino.csv
│   │   ├── kismet/
│   │   │   └── sample_kismet.csv
│   │   └── generic/
│   │       └── sample_generic.csv
│   ├── processed/
│   │   └── .gitkeep
│   └── challenge/
│       └── challenge_wifi.csv
├── scripts/
│   ├── generate_sample_data.py
│   ├── inspect_dataset.py
│   ├── normalize.py
│   ├── validate_dataset.py
│   ├── analyze.py
│   ├── export_geojson.py
│   └── build_map.py
├── maps/
│   └── .gitkeep
├── exercises/
│   ├── LAB01_FIRST_SIGNALS.md
│   ├── LAB02_NORMALIZE_EVERYTHING.md
│   ├── LAB03_SIGNALS_TO_INTELLIGENCE.md
│   └── FINAL_CHALLENGE.md
└── examples/
    ├── common_schema.json
    └── expected_analysis.txt
```

---

# 4. Common schema

Every normalized observation must contain exactly:

```text
timestamp
source
ssid
bssid
channel
frequency
rssi
security
latitude
longitude
```

Example:

```csv
timestamp,source,ssid,bssid,channel,frequency,rssi,security,latitude,longitude
2026-09-20T10:01:02Z,marauder,LAB-ALPHA,02:00:00:00:01:01,1,2412,-42,WPA2,14.60010,-90.52010
```

Rules:

- Normalize BSSID to uppercase.
- Trim SSID whitespace.
- Use `<hidden>` consistently for hidden SSIDs.
- Invalid coordinates become null.
- `0,0` coordinates are treated as missing.
- RSSI stays numeric and negative when supplied in dBm.
- Never invent GPS values for real input.
- Security labels normalize to:
  - OPEN
  - WEP
  - WPA
  - WPA2
  - WPA3
  - UNKNOWN

---

# 5. Frequency mapping

Implement a helper for common 2.4 GHz channels:

```text
1  -> 2412 MHz
2  -> 2417 MHz
3  -> 2422 MHz
4  -> 2427 MHz
5  -> 2432 MHz
6  -> 2437 MHz
7  -> 2442 MHz
8  -> 2447 MHz
9  -> 2452 MHz
10 -> 2457 MHz
11 -> 2462 MHz
12 -> 2467 MHz
13 -> 2472 MHz
14 -> 2484 MHz
```

For 5 GHz and 6 GHz, preserve a provided frequency when available and implement only a simple channel conversion where useful.

Do not overengineer this helper.

---

# 6. Synthetic input formats

Generate intentionally different CSV formats.

## Marauder-like

Path:

```text
data/raw/marauder/sample_marauder.csv
```

Columns:

```csv
MAC,SSID,AuthMode,FirstSeen,Channel,RSSI,Latitude,Longitude
02:00:00:00:01:01,LAB-ALPHA,WPA2,2026-09-20T10:01:02Z,1,-42,14.60010,-90.52010
02:00:00:00:01:02,LAB-BETA,WPA3,2026-09-20T10:01:04Z,6,-67,14.60020,-90.52020
```

Generate at least 20 observations.

Repeat some BSSIDs with different timestamps, RSSI values, and positions.

## Minino-like

Path:

```text
data/raw/minino/sample_minino.csv
```

Columns:

```csv
timestamp,bssid,ssid,channel,rssi,security,lat,lon
2026-09-20T10:02:01Z,02:00:00:00:02:01,LAB-GAMMA,11,-55,WPA2,14.60030,-90.52030
```

Generate at least 20 observations.

## Kismet-like export

For the initial workshop, do **not** parse a native `.kismet` database.

Use an exported CSV representation.

Path:

```text
data/raw/kismet/sample_kismet.csv
```

Columns:

```csv
first_time,device_mac,device_name,channel,frequency,signal_dbm,crypt,lat,lon
2026-09-20T10:03:01Z,02:00:00:00:03:01,LAB-DELTA,1,2412,-61,WPA2,14.60040,-90.52040
```

Generate at least 20 observations.

## Generic

Path:

```text
data/raw/generic/sample_generic.csv
```

Columns:

```csv
timestamp,source,ssid,bssid,channel,frequency,rssi,security,latitude,longitude
```

Generate at least 20 observations.

---

# 7. Challenge dataset

Create:

```text
data/challenge/challenge_wifi.csv
```

Requirements:

- 1,500–2,500 observations.
- 40–80 unique BSSIDs.
- 25–60 unique SSIDs.
- Multiple observations per BSSID.
- Security mix:
  - WPA2
  - WPA3
  - OPEN
  - UNKNOWN
- Several hidden SSIDs.
- Channels 1, 6, and 11 should be common.
- Include some 5 GHz channels.
- RSSI approximately from -30 to -90 dBm.
- GPS observations clustered around several fictional zones.
- Some APs observed from many locations.
- Some SSIDs mapped to multiple BSSIDs.
- Fixed random seed for deterministic output.

Use locally administered synthetic MAC addresses:

```text
02:xx:xx:xx:xx:xx
```

Never use real vendor OUIs.

---

# 8. `generate_sample_data.py`

Purpose:

Generate all raw samples and the challenge dataset.

CLI:

```bash
python scripts/generate_sample_data.py
```

Optional:

```bash
python scripts/generate_sample_data.py --seed 42
```

Expected output:

```text
Generated:
  data/raw/marauder/sample_marauder.csv
  data/raw/minino/sample_minino.csv
  data/raw/kismet/sample_kismet.csv
  data/raw/generic/sample_generic.csv
  data/challenge/challenge_wifi.csv
```

Requirements:

- deterministic;
- no API calls;
- no network access;
- UTF-8 output;
- readable helper functions.

---

# 9. `inspect_dataset.py`

Purpose:

Introduce an unknown CSV before normalization.

CLI:

```bash
python scripts/inspect_dataset.py data/raw/marauder/sample_marauder.csv
```

Output:

```text
File: sample_marauder.csv
Rows: 24
Columns: 8

Columns:
- MAC
- SSID
- AuthMode
- FirstSeen
- Channel
- RSSI
- Latitude
- Longitude

Preview:
...
```

Also show:

- pandas dtypes;
- null counts;
- unique SSID/BSSID counts when recognizable.

Do not modify the file.

---

# 10. `normalize.py`

Main script for LAB 02.

Examples:

```bash
python scripts/normalize.py --source marauder --input data/raw/marauder/sample_marauder.csv --output data/processed/marauder_normalized.csv
```

```bash
python scripts/normalize.py --source minino --input data/raw/minino/sample_minino.csv --output data/processed/minino_normalized.csv
```

```bash
python scripts/normalize.py --source kismet --input data/raw/kismet/sample_kismet.csv --output data/processed/kismet_normalized.csv
```

Support combining inputs:

```bash
python scripts/normalize.py   --source auto   --input     data/raw/marauder/sample_marauder.csv     data/raw/minino/sample_minino.csv     data/raw/kismet/sample_kismet.csv   --output data/processed/networks.csv
```

Auto-detection should rely on column signatures.

Fail clearly if a format is ambiguous.

Suggested functions:

```python
def normalize_marauder(df): ...
def normalize_minino(df): ...
def normalize_kismet(df): ...
def normalize_generic(df): ...
def channel_to_frequency(channel): ...
def normalize_security(value): ...
def clean_coordinates(lat, lon): ...
def validate_columns(df, required): ...
```

Output schema must be exactly:

```text
timestamp,source,ssid,bssid,channel,frequency,rssi,security,latitude,longitude
```

Summary example:

```text
Input rows: 24
Output rows: 24
Unique BSSIDs: 8
Missing GPS: 2
Saved: data/processed/marauder_normalized.csv
```

---

# 11. `validate_dataset.py`

CLI:

```bash
python scripts/validate_dataset.py data/processed/networks.csv
```

Validate:

- required columns;
- numeric channel;
- numeric frequency;
- numeric RSSI;
- BSSID structure;
- latitude from -90 to 90;
- longitude from -180 to 180;
- reject/treat `0,0` as missing;
- parseable timestamps;
- known security labels.

Output:

```text
Dataset validation
------------------
Rows: 64
Schema: OK
BSSID format: OK
RSSI: OK
Coordinates: 61 valid / 3 missing
Timestamp: OK

RESULT: VALID
```

Return a non-zero process status on schema validation failure.

---

# 12. `analyze.py`

CLI:

```bash
python scripts/analyze.py data/processed/networks.csv
```

Also:

```bash
python scripts/analyze.py data/challenge/challenge_wifi.csv
```

Print:

```text
Wireless Dataset Summary
========================

Observations:
Unique BSSIDs:
Unique SSIDs:
Hidden SSIDs:
GPS observations:

Security:
WPA2:
WPA3:
OPEN:
UNKNOWN:

Top Channels:
...

Strongest Observation:
SSID:
BSSID:
RSSI:
Channel:

Most Observed BSSIDs:
...

SSIDs with Multiple BSSIDs:
...
```

Calculate:

- total observations;
- unique BSSIDs;
- unique SSIDs;
- hidden SSIDs;
- security distribution;
- channel distribution;
- strongest RSSI;
- weakest RSSI;
- observations per BSSID;
- SSIDs associated with multiple BSSIDs;
- unique coordinate pairs per BSSID;
- BSSID observed from the most distinct coordinate pairs.

Optional flags:

```bash
--top 10
--json
```

---

# 13. `export_geojson.py`

CLI:

```bash
python scripts/export_geojson.py data/processed/networks.csv maps/networks.geojson
```

Feature example:

```json
{
  "type": "Feature",
  "properties": {
    "timestamp": "2026-09-20T10:01:02Z",
    "source": "marauder",
    "ssid": "LAB-ALPHA",
    "bssid": "02:00:00:00:01:01",
    "channel": 1,
    "frequency": 2412,
    "rssi": -42,
    "security": "WPA2"
  },
  "geometry": {
    "type": "Point",
    "coordinates": [-90.52010, 14.60010]
  }
}
```

Important:

```text
GeoJSON coordinates = [longitude, latitude]
```

Skip observations without valid GPS.

Output:

```text
Input observations: 64
Features exported: 61
Skipped without GPS: 3
Saved: maps/networks.geojson
```

---

# 14. `build_map.py`

Use Folium.

CLI:

```bash
python scripts/build_map.py data/processed/networks.csv maps/networks.html
```

Requirements:

- calculate center from valid GPS rows;
- one marker per observation in the basic version;
- popup:
  - SSID
  - BSSID
  - channel
  - RSSI
  - security
  - source
- use `MarkerCluster` when practical;
- no API keys;
- fail cleanly when no valid GPS exists.

Output:

```text
maps/networks.html
```

---

# 15. LAB 01 material

Create:

```text
exercises/LAB01_FIRST_SIGNALS.md
```

Content:

```markdown
# LAB 01 — First Signals

## Goal

Observe a controlled wireless environment and understand what a wardriving sensor records.

## Time

30 minutes.

## Input

One of:

- ESP32 Marauder
- Minino
- Kismet
- compatible Wi-Fi adapter
- supplied synthetic dataset

## Tasks

1. Inspect the sensor output.
2. Locate:
   - SSID
   - BSSID
   - channel
   - RSSI
   - security
   - timestamp
   - GPS
3. Identify at least three unique BSSIDs.
4. Find the strongest observation.
5. Save the resulting dataset under `data/raw/`.

## No hardware?

Use one of the supplied files under `data/raw/`.

Then run:

`python scripts/inspect_dataset.py <file>`

## Questions

- What identifies an AP?
- Can one SSID map to several BSSIDs?
- Does RSSI equal distance?
- Which metadata can be observed without joining a network?
```

Add a brief responsible-use note.

---

# 16. LAB 02 material

Create:

```text
exercises/LAB02_NORMALIZE_EVERYTHING.md
```

Content:

```markdown
# LAB 02 — Normalize Everything

## Goal

Convert different sensor formats into one common schema.

## Time

30 minutes.

## Step 1 — Inspect

`python scripts/inspect_dataset.py data/raw/marauder/sample_marauder.csv`

Repeat for Minino and Kismet.

## Step 2 — Compare

Identify which source columns correspond to:

- SSID
- BSSID
- timestamp
- channel
- RSSI
- security
- latitude
- longitude

## Step 3 — Normalize

Run `normalize.py`.

## Step 4 — Validate

`python scripts/validate_dataset.py data/processed/networks.csv`

## Success criteria

The output contains:

timestamp, source, ssid, bssid, channel, frequency, rssi, security, latitude, longitude

## Discussion

Why is one common schema more useful than one analysis script per sensor?
```

---

# 17. LAB 03 material

Create:

```text
exercises/LAB03_SIGNALS_TO_INTELLIGENCE.md
```

Content:

```markdown
# LAB 03 — Signals to Intelligence

## Goal

Turn normalized observations into useful information.

## Time

25 minutes.

## Step 1

`python scripts/analyze.py data/processed/networks.csv`

## Step 2

Answer:

1. How many observations exist?
2. How many unique BSSIDs?
3. How many unique SSIDs?
4. What is the most common channel?
5. What security mechanism appears most often?
6. What was the strongest observation?
7. Which BSSID appears most often?
8. Which SSIDs map to multiple BSSIDs?

## Step 3 — GeoJSON

`python scripts/export_geojson.py data/processed/networks.csv maps/networks.geojson`

## Step 4 — Map

`python scripts/build_map.py data/processed/networks.csv maps/networks.html`

Open `maps/networks.html` locally.

## Discussion

What changed when geographic context was added?
```

---

# 18. Final challenge

Create:

```text
exercises/FINAL_CHALLENGE.md
```

Use:

```text
data/challenge/challenge_wifi.csv
```

Questions:

1. How many observations exist?
2. How many unique BSSIDs exist?
3. How many unique SSIDs exist?
4. Which five channels are most common?
5. What is the security distribution?
6. Which BSSID has the strongest RSSI observation?
7. Which BSSID was observed most frequently?
8. Which BSSID was observed from the most distinct locations?
9. Which SSIDs map to multiple BSSIDs?
10. Which area has the highest apparent observation density?
11. Can you identify possible groups of APs from the same deployment using only this dataset?
12. What additional evidence would you need before making stronger conclusions?

Questions 11 and 12 must explicitly be framed as hypotheses, not facts.

---

# 19. `examples/common_schema.json`

```json
{
  "timestamp": "2026-09-20T10:01:02Z",
  "source": "marauder",
  "ssid": "LAB-ALPHA",
  "bssid": "02:00:00:00:01:01",
  "channel": 1,
  "frequency": 2412,
  "rssi": -42,
  "security": "WPA2",
  "latitude": 14.6001,
  "longitude": -90.5201
}
```

---

# 20. README

Include setup instructions.

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Generate data:

```bash
python scripts/generate_sample_data.py
```

Full workflow:

```bash
python scripts/inspect_dataset.py data/raw/marauder/sample_marauder.csv

python scripts/normalize.py   --source auto   --input     data/raw/marauder/sample_marauder.csv     data/raw/minino/sample_minino.csv     data/raw/kismet/sample_kismet.csv   --output data/processed/networks.csv

python scripts/validate_dataset.py data/processed/networks.csv

python scripts/analyze.py data/processed/networks.csv

python scripts/export_geojson.py data/processed/networks.csv maps/networks.geojson

python scripts/build_map.py data/processed/networks.csv maps/networks.html
```

Explain:

```text
Raw Data
   ↓
Inspect
   ↓
Normalize
   ↓
Validate
   ↓
Analyze
   ↓
GeoJSON
   ↓
Map
```

---

# 21. Instructor copy/paste commands

## Generate samples

```bash
python scripts/generate_sample_data.py
```

## Single sensor

```bash
python scripts/inspect_dataset.py data/raw/marauder/sample_marauder.csv
python scripts/normalize.py --source marauder --input data/raw/marauder/sample_marauder.csv --output data/processed/marauder.csv
python scripts/validate_dataset.py data/processed/marauder.csv
python scripts/analyze.py data/processed/marauder.csv
```

## Combined dataset

```bash
python scripts/normalize.py --source auto --input data/raw/marauder/sample_marauder.csv data/raw/minino/sample_minino.csv data/raw/kismet/sample_kismet.csv --output data/processed/networks.csv
python scripts/validate_dataset.py data/processed/networks.csv
python scripts/analyze.py data/processed/networks.csv
python scripts/export_geojson.py data/processed/networks.csv maps/networks.geojson
python scripts/build_map.py data/processed/networks.csv maps/networks.html
```

## Challenge

```bash
python scripts/analyze.py data/challenge/challenge_wifi.csv
python scripts/build_map.py data/challenge/challenge_wifi.csv maps/challenge.html
```

---

# 22. Code quality

Every Python file must use:

```python
if __name__ == "__main__":
    main()
```

Also:

- use `argparse`;
- use `pathlib.Path`;
- prefer functions over long procedural code;
- use type hints where useful;
- avoid unnecessary classes;
- include useful `--help`;
- print clear user-facing errors;
- return non-zero status for invalid input.

---

# 23. Workshop-friendly output

Prefer:

```text
[+] Loaded 64 observations
[+] Unique BSSIDs: 14
[+] GPS observations: 61
[+] Saved data/processed/networks.csv
```

Avoid:

- huge DataFrame dumps;
- verbose debug logs;
- unnecessary UI dependencies.

---

# 24. Privacy and safety

The sample generator must not use:

- real personal SSIDs;
- real addresses;
- real third-party MAC addresses;
- credentials;
- captured handshakes;
- participant locations.

All processing must be local.

No automatic uploads.

---

# 25. Acceptance test

From a clean repository, this must work:

```bash
python -m pip install -r requirements.txt

python scripts/generate_sample_data.py

python scripts/inspect_dataset.py data/raw/marauder/sample_marauder.csv

python scripts/normalize.py   --source auto   --input     data/raw/marauder/sample_marauder.csv     data/raw/minino/sample_minino.csv     data/raw/kismet/sample_kismet.csv     data/raw/generic/sample_generic.csv   --output data/processed/networks.csv

python scripts/validate_dataset.py data/processed/networks.csv

python scripts/analyze.py data/processed/networks.csv

python scripts/export_geojson.py data/processed/networks.csv maps/networks.geojson

python scripts/build_map.py data/processed/networks.csv maps/networks.html

python scripts/analyze.py data/challenge/challenge_wifi.csv

python scripts/build_map.py data/challenge/challenge_wifi.csv maps/challenge.html
```

Expected files:

```text
data/processed/networks.csv
maps/networks.geojson
maps/networks.html
maps/challenge.html
```

Do not consider the task complete until all commands work without manual source edits.

---

# 26. Implementation order

Implement in this order:

```text
1. Repository skeleton
2. requirements.txt
3. generate_sample_data.py
4. inspect_dataset.py
5. normalize.py
6. validate_dataset.py
7. analyze.py
8. export_geojson.py
9. build_map.py
10. exercise Markdown files
11. README.md
12. Run the complete acceptance flow
13. Fix errors
14. Save a known-good analysis output
```

After each script, run it before proceeding.

---

# 27. Optional extensions

Only after the base workshop works:

- Jupyter notebook version of the analysis;
- Folium heatmap;
- RSSI visualization;
- pluggable sensor adapters;
- local FastAPI API;
- additional BLE or LTE exercises.

These are optional and must not block the core workshop.

---

# 28. Final principle

The repository should reinforce:

```text
THE TOOL IS JUST THE SENSOR.

SIGNALS
  ↓
OBSERVATIONS
  ↓
DATA
  ↓
CONTEXT
  ↓
PATTERNS
  ↓
INTELLIGENCE
```

The educational objective is not attacking Wi-Fi networks.

The objective is learning how wireless observations become structured information that can be inspected, normalized, analyzed, mapped, and used to form responsible research hypotheses.

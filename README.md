# Wardriving Workshop — De señales a inteligencia

Material de laboratorio (~3 horas) para el taller **From Signals to Intelligence: Building Your Wardriving Arsenal**.

El objetivo educativo **no** es atacar redes Wi-Fi. Es aprender cómo las observaciones inalámbricas pasivas se convierten en información estructurada que se puede inspeccionar, normalizar, analizar, mapear y usar para formar **hipótesis de investigación responsables**.

```text
Señales
  ↓
Captura
  ↓
Datos crudos
  ↓
Normalización
  ↓
Análisis
  ↓
Exportación geoespacial
  ↓
Inteligencia
```

Principio del taller:

```text
LA HERRAMIENTA SOLO ES EL SENSOR.

SEÑALES → OBSERVACIONES → DATOS → CONTEXTO → PATRONES → INTELIGENCIA
```

---

## Qué incluye este repositorio

| Ruta | Contenido |
|------|-----------|
| `data/raw/` | Muestras CSV sintéticas por formato de sensor (Marauder, Minino, Kismet export, genérico) |
| `data/processed/` | Salida normalizada (generada por scripts; no versionar resultados) |
| `data/challenge/` | Dataset grande de investigación sintética |
| `scripts/` | Pipeline completo: generar → inspeccionar → normalizar → validar → analizar → GeoJSON → mapa |
| `exercises/` | Labs 01–03 y reto final (preguntas y pasos) |
| `examples/` | Esquema común de ejemplo y salida de análisis de referencia |
| `maps/` | GeoJSON / HTML generados localmente |
| `requirements.txt` | Dependencias Python |
| `WARDRIVING_WORKSHOP_CURSOR_TASK.md` | Especificación original del material (referencia) |

Todos los datasets empaquetados son **sintéticos**. No hay SSIDs/BSSIDs reales de terceros, credenciales, handshakes, PCAP ni ubicaciones personales. Las coordenadas GPS usan valores ficticios (p. ej. `1.2345678, -9.8765432`).

---

## Requisitos

- Linux, macOS o Windows
- Python **3.10+**
- Dependencias: `pandas>=2.0`, `folium>=0.16` (más biblioteca estándar)

No hace falta hardware especializado: puedes completar todo el taller con los CSV incluidos.

---

## Instalación

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Generar (o regenerar) las muestras

```bash
python scripts/generate_sample_data.py
# opcional: semilla fija
python scripts/generate_sample_data.py --seed 42
```

Salida esperada:

```text
Generated:
  data/raw/marauder/sample_marauder.csv
  data/raw/minino/sample_minino.csv
  data/raw/kismet/sample_kismet.csv
  data/raw/generic/sample_generic.csv
  data/challenge/challenge_wifi.csv
```

---

## Flujo completo del laboratorio

```text
Datos crudos
   ↓
Inspeccionar
   ↓
Normalizar
   ↓
Validar
   ↓
Analizar
   ↓
GeoJSON
   ↓
Mapa
```

```bash
python scripts/inspect_dataset.py data/raw/marauder/sample_marauder.csv

python scripts/normalize.py \
  --source auto \
  --input \
    data/raw/marauder/sample_marauder.csv \
    data/raw/minino/sample_minino.csv \
    data/raw/kismet/sample_kismet.csv \
    data/raw/generic/sample_generic.csv \
  --output data/processed/networks.csv

python scripts/validate_dataset.py data/processed/networks.csv

python scripts/analyze.py data/processed/networks.csv

python scripts/export_geojson.py data/processed/networks.csv maps/networks.geojson

python scripts/build_map.py data/processed/networks.csv maps/networks.html
```

Reto:

```bash
python scripts/analyze.py data/challenge/challenge_wifi.csv
python scripts/build_map.py data/challenge/challenge_wifi.csv maps/challenge.html
```

---

## Esquema común (salida normalizada)

Cada observación normalizada tiene exactamente:

```text
timestamp, source, ssid, bssid, channel, frequency, rssi, security, latitude, longitude
```

Reglas aplicadas por `normalize.py`:

- BSSID en mayúsculas
- SSID recortado (trim); ocultos → `<hidden>`
- coordenadas inválidas o `0,0` → nulas (no se inventa GPS)
- RSSI numérico (dBm, típicamente negativo)
- seguridad → `OPEN` | `WEP` | `WPA` | `WPA2` | `WPA3` | `UNKNOWN`
- frecuencia derivada del canal 2.4 GHz cuando falta (mapa 1→2412 … 14→2484); 5 GHz se preserva o convierte de forma simple

Ejemplo: `examples/common_schema.json`.

---

## Scripts

| Script | Uso |
|--------|-----|
| `generate_sample_data.py` | Genera CSV sintéticos deterministas (`--seed`) |
| `inspect_dataset.py` | Columnas, dtypes, nulos, preview, conteos SSID/BSSID |
| `normalize.py` | Une formatos (`marauder` / `minino` / `kismet` / `generic` / `auto`) |
| `validate_dataset.py` | Valida esquema; sale ≠0 si falla |
| `analyze.py` | Resumen de investigación (`--top N`, `--json`) |
| `export_geojson.py` | FeatureCollection; coords `[lon, lat]`; omite filas sin GPS |
| `build_map.py` | Mapa HTML local con Folium + MarkerCluster |

Ayuda: `python scripts/<script>.py --help`.

---

## Datasets crudos (formatos distintos a propósito)

### Marauder-like — `data/raw/marauder/sample_marauder.csv`

```text
MAC,SSID,AuthMode,FirstSeen,Channel,RSSI,Latitude,Longitude
```

### Minino-like — `data/raw/minino/sample_minino.csv`

```text
timestamp,bssid,ssid,channel,rssi,security,lat,lon
```

### Kismet (export CSV) — `data/raw/kismet/sample_kismet.csv`

```text
first_time,device_mac,device_name,channel,frequency,signal_dbm,crypt,lat,lon
```

No se parsea la base nativa `.kismet` en este taller.

### Genérico — `data/raw/generic/sample_generic.csv`

Ya en esquema común (útil como control).

### Desafío — `data/challenge/challenge_wifi.csv`

~1500–2500 observaciones, decenas de BSSID/SSID, mezcla de seguridad, SSIDs ocultos, canales 1/6/11 frecuentes, algo de 5 GHz, clusters GPS ficticios. MACs localmente administradas `02:xx:xx:xx:xx:xx`.

---

## Ejercicios

| Fichero | Tema | Tiempo |
|---------|------|--------|
| [`exercises/LAB01_FIRST_SIGNALS.md`](exercises/LAB01_FIRST_SIGNALS.md) | Primeras señales e inspección | ~30 min |
| [`exercises/LAB02_NORMALIZE_EVERYTHING.md`](exercises/LAB02_NORMALIZE_EVERYTHING.md) | Normalización y validación | ~30 min |
| [`exercises/LAB03_SIGNALS_TO_INTELLIGENCE.md`](exercises/LAB03_SIGNALS_TO_INTELLIGENCE.md) | Análisis, GeoJSON y mapa | ~25 min |
| [`exercises/FINAL_CHALLENGE.md`](exercises/FINAL_CHALLENGE.md) | 12 preguntas sobre el challenge | resto |

### Comandos rápidos para instructores

Un sensor:

```bash
python scripts/inspect_dataset.py data/raw/marauder/sample_marauder.csv
python scripts/normalize.py --source marauder --input data/raw/marauder/sample_marauder.csv --output data/processed/marauder.csv
python scripts/validate_dataset.py data/processed/marauder.csv
python scripts/analyze.py data/processed/marauder.csv
```

Dataset combinado + mapa: ver sección «Flujo completo».

---

## Privacidad y seguridad

**Sí:** observación pasiva de metadatos, datasets sintéticos, procesamiento 100 % local.

**No en este material:** deautenticación, inyección, cracking de handshakes, phishing, intrusión, explotación automatizada, subidas automáticas a la nube.

Trabaja solo en entornos autorizados o con los datos del repositorio.

---

## Guía para asistentes de IA

Al ayudar en este repo:

1. Responde y documenta ejercicios en **español** (comentarios de código en inglés, según la especificación).
2. No sustituyas coordenadas sintéticas por GPS reales.
3. No añadas exploits, ataques activos ni captura/cracking de credenciales.
4. Prefiere ampliar análisis defensivo/educativo (normalización, validación, mapas, hipótesis).
5. Tras cambiar `.py`, documenta el cambio en un `CHANGE_YYYYMMDD_*.md` en la raíz del proyecto.
6. Orquestación de contenedores (si se añade): usar `podman-compose`, no Docker Compose CLI.

---

## Extensiones opcionales (después del núcleo)

Notebook Jupyter, heatmap Folium, visualización RSSI, adaptadores de sensor plug-in, API FastAPI local, ejercicios BLE/LTE. No deben bloquear el laboratorio base.

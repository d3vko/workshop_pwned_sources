# LAB 02 — Normalizarlo todo

## Objetivo

Convertir formatos distintos de sensores en un único esquema común.

## Tiempo

30 minutos.

## Paso 1 — Inspeccionar

```bash
python scripts/inspect_dataset.py data/raw/marauder/sample_marauder.csv
python scripts/inspect_dataset.py data/raw/minino/sample_minino.csv
python scripts/inspect_dataset.py data/raw/kismet/sample_kismet.csv
```

## Paso 2 — Comparar

Identifica qué columnas de cada fuente corresponden a:

| Campo común | Marauder | Minino | Kismet |
|-------------|----------|--------|--------|
| SSID | ? | ? | ? |
| BSSID | ? | ? | ? |
| timestamp | ? | ? | ? |
| channel | ? | ? | ? |
| RSSI | ? | ? | ? |
| security | ? | ? | ? |
| latitude | ? | ? | ? |
| longitude | ? | ? | ? |

## Paso 3 — Normalizar

Un solo sensor:

```bash
python scripts/normalize.py \
  --source marauder \
  --input data/raw/marauder/sample_marauder.csv \
  --output data/processed/marauder_normalized.csv
```

Varios sensores a la vez (detección automática):

```bash
python scripts/normalize.py \
  --source auto \
  --input \
    data/raw/marauder/sample_marauder.csv \
    data/raw/minino/sample_minino.csv \
    data/raw/kismet/sample_kismet.csv \
  --output data/processed/networks.csv
```

## Paso 4 — Validar

```bash
python scripts/validate_dataset.py data/processed/networks.csv
```

## Criterios de éxito

La salida contiene exactamente:

```text
timestamp, source, ssid, bssid, channel, frequency, rssi, security, latitude, longitude
```

Además:

- BSSID en mayúsculas
- SSID sin espacios sobrantes
- SSIDs ocultos como `<hidden>`
- coordenadas `0,0` tratadas como ausentes
- etiquetas de seguridad: OPEN, WEP, WPA, WPA2, WPA3, UNKNOWN

## Discusión

¿Por qué un esquema común es más útil que un script de análisis distinto por cada sensor?

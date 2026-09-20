# Creación del laboratorio Wardriving Workshop

## Qué se hizo
- Se creó el esqueleto del repositorio educativo de wardriving (datos, scripts, ejercicios, ejemplos, mapas).
- Se implementaron siete scripts Python del pipeline: generación sintética, inspección, normalización, validación, análisis, exportación GeoJSON y mapa Folium.
- Se generaron datasets sintéticos (4 formatos crudos + challenge de 2000 filas) con GPS ficticio y MACs `02:xx:…`.
- Se documentó el flujo, esquema común, labs y guía para asistentes en `README.md` (español).

## Por qué
- Permitir completar el taller de ~3 h sin hardware, enfocándose en metadatos pasivos y en el paso de señales a inteligencia estructurada.
- Cumplir la especificación de `WARDRIVING_WORKSHOP_CURSOR_TASK.md` con contenido operable en español.

## Archivos tocados
- `scripts/generate_sample_data.py` — genera CSV sintéticos deterministas (`--seed`)
- `scripts/inspect_dataset.py` — inspección previa a normalizar
- `scripts/normalize.py` — unifica Marauder/Minino/Kismet/genérico al esquema común
- `scripts/validate_dataset.py` — valida esquema y calidad básica
- `scripts/analyze.py` — resumen de investigación (`--top`, `--json`)
- `scripts/export_geojson.py` — FeatureCollection `[lon, lat]`
- `scripts/build_map.py` — HTML local con MarkerCluster
- `requirements.txt`, `.gitignore`, `exercises/*.md`, `examples/*`, `README.md`

## Cómo verificar
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_sample_data.py
python scripts/normalize.py --source auto --input \
  data/raw/marauder/sample_marauder.csv \
  data/raw/minino/sample_minino.csv \
  data/raw/kismet/sample_kismet.csv \
  data/raw/generic/sample_generic.csv \
  --output data/processed/networks.csv
python scripts/validate_dataset.py data/processed/networks.csv
python scripts/analyze.py data/processed/networks.csv
python scripts/build_map.py data/challenge/challenge_wifi.csv maps/challenge.html
```

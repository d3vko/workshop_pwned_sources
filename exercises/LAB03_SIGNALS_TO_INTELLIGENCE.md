# LAB 03 — De señales a inteligencia

## Objetivo

Convertir observaciones normalizadas en información útil para investigación.

## Tiempo

25 minutos.

## Paso 1 — Analizar

```bash
python scripts/analyze.py data/processed/networks.csv
```

## Paso 2 — Responder

1. ¿Cuántas observaciones hay?
2. ¿Cuántos BSSID únicos?
3. ¿Cuántos SSID únicos?
4. ¿Cuál es el canal más común?
5. ¿Qué mecanismo de seguridad aparece con más frecuencia?
6. ¿Cuál fue la observación más fuerte (RSSI)?
7. ¿Qué BSSID aparece más veces?
8. ¿Qué SSIDs se mapean a varios BSSID?

## Paso 3 — GeoJSON

```bash
python scripts/export_geojson.py data/processed/networks.csv maps/networks.geojson
```

Recuerda: en GeoJSON las coordenadas son `[longitud, latitud]`.

## Paso 4 — Mapa

```bash
python scripts/build_map.py data/processed/networks.csv maps/networks.html
```

Abre `maps/networks.html` en el navegador (sin necesidad de API keys).

## Discusión

¿Qué cambia cuando se añade contexto geográfico a las mismas observaciones?

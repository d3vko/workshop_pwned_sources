# LAB 01 — Primeras señales

## Objetivo

Observar un entorno inalámbrico controlado y entender qué registra un sensor de wardriving.

## Tiempo

30 minutos.

## Entrada

Una de estas opciones:

- ESP32 Marauder
- Minino
- Kismet
- adaptador Wi-Fi compatible
- el dataset sintético incluido en este repositorio

## Tareas

1. Inspecciona la salida del sensor (o del CSV de muestra).
2. Localiza estos campos:
   - SSID
   - BSSID
   - canal
   - RSSI
   - seguridad
   - marca de tiempo
   - GPS
3. Identifica al menos tres BSSID únicos.
4. Encuentra la observación con el RSSI más fuerte (menos negativo).
5. Guarda el dataset resultante bajo `data/raw/` (si capturaste con hardware).

## ¿Sin hardware?

Usa uno de los ficheros suministrados en `data/raw/`.

Luego ejecuta:

```bash
python scripts/inspect_dataset.py data/raw/marauder/sample_marauder.csv
```

Prueba también Minino y Kismet para comparar columnas.

## Preguntas

- ¿Qué identifica de forma única a un AP?
- ¿Puede un mismo SSID mapearse a varios BSSID?
- ¿El RSSI equivale a distancia?
- ¿Qué metadatos se pueden observar sin unirse a la red?

## Nota de uso responsable

Este laboratorio trabaja solo con **metadatos pasivos** (SSID, BSSID, canal, RSSI, etc.).
No incluye deautenticación, inyección, captura de handshakes ni ataques a credenciales.
Usa únicamente entornos autorizados o los datos sintéticos del repositorio.

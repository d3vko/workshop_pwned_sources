# Reto final — Investigación con dataset de desafío

## Objetivo

Aplicar el flujo completo (inspección → análisis → mapa) sobre un dataset mayor y sintético.

## Dataset

```text
data/challenge/challenge_wifi.csv
```

Si aún no existe, genéralo:

```bash
python scripts/generate_sample_data.py
```

## Comandos útiles

```bash
python scripts/inspect_dataset.py data/challenge/challenge_wifi.csv
python scripts/analyze.py data/challenge/challenge_wifi.csv
python scripts/analyze.py data/challenge/challenge_wifi.csv --json
python scripts/build_map.py data/challenge/challenge_wifi.csv maps/challenge.html
```

## Preguntas

1. ¿Cuántas observaciones hay?
2. ¿Cuántos BSSID únicos hay?
3. ¿Cuántos SSID únicos hay?
4. ¿Cuáles son los cinco canales más comunes?
5. ¿Cuál es la distribución de seguridad?
6. ¿Qué BSSID tiene la observación con el RSSI más fuerte?
7. ¿Qué BSSID se observó con más frecuencia?
8. ¿Qué BSSID se observó desde más ubicaciones distintas?
9. ¿Qué SSIDs se mapean a varios BSSID?
10. ¿Qué zona muestra mayor densidad aparente de observaciones?
11. *(Hipótesis, no hecho)* ¿Puedes identificar posibles grupos de APs del mismo despliegue usando solo este dataset? ¿Qué señales lo sugieren?
12. *(Hipótesis / límites)* ¿Qué evidencia adicional necesitarías antes de sacar conclusiones más fuertes?

## Reglas de interpretación

- Las preguntas **11** y **12** deben formularse como **hipótesis**, no como hechos.
- Correlación espacial o mismo SSID ≠ propiedad demostrada.
- No inventes coordenadas GPS ni asumas identidad real de redes o personas.
- Todo el procesamiento es local; no subas capturas ni datos de terceros.

## Entregable sugerido

Un breve informe (texto o notas) con:

- respuestas 1–10 respaldadas por la salida de `analyze.py` / el mapa;
- hipótesis razonadas para 11–12;
- una frase sobre limitaciones del dataset.

# Armadores

Regeneran los exámenes a partir de `../bloques/`. Se corren desde la raíz del repo.

```
python3 fuentes/ipn/scripts/armar-iycfm.py        # -> ipn-iycfm-1.json
python3 fuentes/ipn/scripts/armar-area.py cmb     # -> ipn-cmb-1.json
python3 fuentes/ipn/scripts/armar-area.py csya    # -> ipn-csya-1.json
```

El orden importa: `armar-area.py` lee los `ipn-*.json` que ya existan para no repetir
reactivos entre exámenes, así que hay que correrlos en ese orden (y borrar el destino
antes si se quiere rearmar desde cero).

`armar-iycfm.py` lleva la selección de reactivos escrita a mano; `armar-area.py` la
elige sola, tomando de cada bloque los que tienen texto, cuatro opciones y ninguna
figura pendiente, repartiendo matemáticas entre sus siete sub-bloques y prefiriendo
siempre lo que ningún otro examen haya usado.

`generar-figuras-aurea.py` reconstruye los tres SVG de la lectura de la proporción
áurea en `public/imagenes_ipn-iycfm-1/`.

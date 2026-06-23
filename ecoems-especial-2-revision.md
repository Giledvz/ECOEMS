# ECOEMS Especial 2 — reporte de armado

**Fuente:** video `IMG_9636.MOV` (celular grabando la pantalla de una laptop con el examen en línea, 4.4 min).
Es el mismo proceso que ecoems-especial pero desde video en vez de fotos.

## Pipeline
1. Extracción densa: **4 fps a 2560px → 1067 cuadros**.
2. Agrupación por contenido (hash recortado al centro) → **121 grupos**.
3. Selección del cuadro **más nítido** de cada grupo (varianza de Laplaciano) — clave: a 1 fps los cuadros caían borrosos (temblor de mano); el más nítido de cada ráfaga sí se lee.
4. OCR multi-agente (18 agentes) verbatim, ignorando la respuesta marcada por el alumno.
5. Dedup por número de pregunta + fusión de campos entre cuadros del mismo número.
6. Inferencia de respuesta + tema + explicación (8 agentes).

## Resultado
- El video **no mostró todas las preguntas**: solo aparecieron **53 números distintos** (rango 1..127). El alumno navegó saltándose muchas.
- **40 preguntas activas** (completas y respondibles solo con texto).
- **12 apartadas** en `_incompletas`.
- Distribución de respuestas: A:7, B:8, C:13, D:12.

## ⚠️ Revisar a ojo (no pude verificar al 100%)

### Respuestas con confianza media (lectura/interpretación)
- **Q6** (abejas, "según académico de Maryland") → marqué **A**. Dudosa: la cita textual de van Engelsdorp es "los datos deberían preocuparnos" (D). Conviene revisar contra la lectura completa.
- **Q7** (Los elegidos, "vivir más allá que las estatuas") → **A** (no tenía representaciones físicas). Razonable pero la lectura está cortada.
- **Q8** (significado de palabra en mayúsculas) → **D** (guarnición = tropa que resguarda). El problema: **no se ve cuál es la palabra en mayúsculas** (está en la parte de la lectura que no salió). Inferido por las opciones.
- **Q17** (teriantropía, relacionar términos) → **C** (I.c–II.b–III.a). Revisar el emparejamiento.
- **Q19** (nexos del fragmento de Pedro) → **A** (introducir/ordenar ideas).

### Lecturas truncadas
Las lecturas salieron **cortadas** en el borde de pantalla (es lo que se veía en el video). Afecta a **Q5, Q6, Q7, Q8, Q17**. Las preguntas se pudieron responder con la parte visible, pero si quieres soltura conviene pegar la lectura completa.

## Las 12 apartadas (`_incompletas`)
Todas traen un campo `_figura` describiendo qué habría que dibujar.

| # orig | Materia | Motivo |
|---|---|---|
| 9 | Matemáticas | opciones cortadas (faltan C, D) + tabla de frecuencias |
| 10 | Matemáticas | figura: rectas paralelas + transversal, ángulo 115° |
| 11 | Matemáticas | opciones cortadas (solo A) + figura del cono (g=15, r=9) |
| 12 | Matemáticas | opción C ilegible + figura del rectángulo 8×6 |
| 53 | Física | opciones cortadas (solo A) + gráfica velocidad-tiempo |
| 81 | Habilidad matemática | opciones son imágenes (secuencia de figuras) |
| 85 | Habilidad matemática | opciones son imágenes (rotación de cubos) |
| 86 | Habilidad matemática | opciones son imágenes (rotación de cubos) |
| 87 | Habilidad matemática | figura: patrón desplegado de un cubo + opciones no visibles |
| 88 | Habilidad matemática | opción D cortada + figura (apilamiento de cubos) |
| 105 | Historia | opción D cortada + columnas país-territorio incompletas |
| 106 | Historia | opciones ilegibles/confusas (relación de causas) |

## Notas
- Detecté que las preguntas con número original 112 y 113 eran **la misma** (mismo enunciado y opciones) → conservé una sola.
- Roster idéntico a ecoems-especial: 16 alumnos, 7 deshabilitados (Yuli, Sofía, Leah, Regina, Conchita, Julio, Kevin).
- **No se ha subido al servidor** — está solo el JSON, listo cuando quieras aplicarlo.

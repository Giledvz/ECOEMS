# Fuentes IPN — examen de admisión a nivel superior

## Archivos

| Archivo | Qué es | En git |
|---|---|---|
| `temario-oficial-ipn-nivel-superior.pdf` | Temario de Estudio (25 pp.), Dirección de Educación Superior | sí (360 KB) |
| `material-apoyo-ipn-2026-nivel-superior.pdf` | **Material de Apoyo al Aprendizaje 2026** (159 pp.): temario + ejercicios + retroalimentaciones + exámenes de práctica por área | no (90 MB) |
| `guia-oficial-ipn-nivel-superior.pdf` | Guía de años anteriores (132 pliegos dobles): reactivos por materia con su tabla de respuestas correctas | no (31 MB) |

Los dos escaneos grandes quedan fuera del repositorio por su peso (ver `.gitignore`).
Están en esta carpeta en disco. Origen del temario:
https://www.ipn.mx/des/tramites-y-servicios/temarios-examen-de-admision-nivel-superior.html

## Estructura del examen 2026 — 140 reactivos de opción múltiple, 3 horas

Tomada de la página 8 del Material de Apoyo 2026, que es la fuente oficial.

| Materia | IyCFM | CMB | CSyA |
|---|--:|--:|--:|
| Matemáticas | 37 | 33 | 37 |
| Competencia escrita | 20 | 20 | 20 |
| Competencia lectora | 20 | 20 | 20 |
| Química | 17 | 17 | 17 |
| Física | 17 | 13 | 17 |
| Historia | 10 | 10 | 10 |
| Reading comprehension | 10 | 10 | 10 |
| Biología | 9 | 17 | 9 |
| **Total** | **140** | **140** | **140** |

Áreas: IyCFM = Ingeniería y Ciencias Físico Matemáticas · CMB = Ciencias Médico
Biológicas · CSyA = Ciencias Sociales y Administrativas.

**IyCFM y CSyA reparten igual los reactivos**; lo que cambia es la profundidad del
contenido, y eso sí viene indicado materia por materia:

- Química: "Química I, II, III y IV" en IyCFM y CMB · "Química I y II" en CSyA.
- Física: "Física para ICFM" · "Física para CMB" · "Física para CSA".
- Biología: "Biología básica" en IyCFM y CSyA · "Biología básica, celular, humana
  y continuidad biológica" en CMB.

Las tres versiones integran Reading comprehension e Historia.

> Nota: dos sitios de preparación (unitips y apprendi) publican para CSyA un reparto
> distinto (35 Matemáticas, 25 competencia escrita, 20 Historia, 10 Química, 10
> Física, 10 Biología). No coincide con el material oficial; se conserva la tabla
> de arriba.

## Estructura del Material de Apoyo 2026

El PDF es un escaneo **sin capa de texto** (pdftotext devuelve 158 bytes), a doble
página: cada página del PDF es un pliego con dos páginas del libro. Se transcribió
leyendo las imágenes.

| Bloque | Págs. PDF | Reactivos |
|---|---|--:|
| Portada y presentación | 1-2 | — |
| Temario de Estudio (el mismo PDF de 25 pp.) | 3-16 | — |
| Aspectos generales y estructura del examen | 17 | — |
| Pensamiento matemático | 18-22 | 40 |
| Álgebra | 23-27 | 40 |
| Geometría y trigonometría | 28-33 | 40 |
| Geometría analítica | 34-39 | 40 |
| Cálculo diferencial | 40-44 | 40 |
| Cálculo integral | 45-51 | 40 |
| Probabilidad y estadística | 52-57 | 40 |
| Competencia escrita | 58-67 | 50 |
| Competencia lectora | 68-79 | 60 (6 lecturas × 10) |
| Reading comprehension | 80-86 | 40 |
| Historia | 87-93 | 40 |
| Biología · IyCFM | 94-99 | 30 |
| Química · IyCFM | 100-104 | 40 |
| Física · IyCFM | 105-112 | 50 |
| Biología / Química / Física · CMB | 113-131 | — |
| Biología / Química / Física · CSyA | 132-143 | — |
| Oferta educativa y anexos | 144-158 | — |

Cada bloque cierra con su tabla **RESPUESTAS CORRECTAS (RC)**. No hay un "examen de
práctica" armado: la guía es un banco por materia, y el examen se arma tomando de
cada bloque la cantidad que marca la distribución oficial de arriba.

## Bloques transcritos — `bloques/*.json`

Un archivo por bloque, con `_meta.rc` (la clave completa del bloque, incluso de los
reactivos que aún no se transcriben) y un arreglo de reactivos. Los que dependen de
una figura del original quedan como *stub* con el campo `figura` describiéndola, para
poder vectorizarlos después sin volver a leer el escaneo.

| Archivo | Transcritos | Sin figura |
|---|---|---|
| `pensamiento-matematico.json` | 40 de 40 | 22 |
| `algebra.json` | 40 de 40 | 37 |
| `geometria-trigonometria.json` | 40 de 40 | 23 |
| `geometria-analitica.json` | 40 de 40 | 35 |
| `calculo-diferencial.json` | 40 de 40 | **40** |
| `calculo-integral.json` | 23 de 40 | 21 |
| `probabilidad-estadistica.json` | 15 de 40 | 14 |
| `competencia-escrita.json` | 32 de 50 | **32** |
| `competencia-lectora.json` | 3 lecturas de 6 | lecturas 2 y 3 |
| `reading-comprehension.json` | 18 de 40 | **18** |
| `historia.json` | 17 de 40 | **17** |
| `biologia-iycfm.json` | 30 de 30 | 22 |
| `quimica-iycfm.json` | 40 de 40 | 30 |
| `fisica-iycfm.json` | 27 de 50 | 22 |

Pendiente de transcribir (páginas del PDF): cálculo integral 48-50, probabilidad
53-55, competencia escrita 64-66, competencia lectora 74-77, reading 83-85, historia
90-92, física 109-111. Los bloques de CMB y CSyA están completos sin transcribir.

## Examen armado

`ipn-iycfm-1.json` — "Simulacro IPN — Ingeniería y Ciencias Físico Matemáticas",
140 reactivos con la distribución oficial exacta. Todas las respuestas provienen de
las tablas RC de la guía; se recalcularon a mano varias (pensamiento matemático 1, 2,
40; álgebra 4, 5, 12, 33, 40; física 8, 13, 20, 21, 50) y todas coincidieron.

Sus tres figuras (`public/imagenes_ipn-iycfm-1/lectura1_*.svg`) son la construcción
de la razón áurea, el rectángulo dorado y la espiral áurea, reconstruidas en SVG
tema-adaptable; van embebidas en la lectura vía `<img>` dentro del `context`.

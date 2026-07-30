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

Un archivo por bloque, con `_meta.rc` (la clave completa del bloque tal como viene en
su tabla RESPUESTAS CORRECTAS) y un arreglo de reactivos. Los que dependen de una
figura del original quedan como *stub* con el campo `figura` describiéndola, para
poder vectorizarlos después sin volver a leer el escaneo.

Los bloques de **Conocimientos generales** (matemáticas, competencias, reading,
historia) los comparten las tres áreas; solo Biología, Química y Física cambian por
área.

| Archivo | Reactivos del bloque | Transcritos | Utilizables sin figura | |
|---|--:|--:|--:|---|
| `algebra.json` | 40 | 40 | 37 |  |
| `biologia-cmb.json` | 50 | 50 | 36 |  |
| `biologia-csya.json` | 25 | 25 | 21 |  |
| `biologia-iycfm.json` | 30 | 30 | 22 |  |
| `calculo-diferencial.json` | 40 | 40 | 40 |  |
| `calculo-integral.json` | 40 | 23 | 21 |  |
| `competencia-escrita.json` | 50 | 50 | 48 |  |
| `competencia-lectora.json` | 60 | 50 | 46 | 5 lecturas |
| `fisica-cmb.json` | 30 | 30 | 28 |  |
| `fisica-csya.json` | 25 | 25 | 22 |  |
| `fisica-iycfm.json` | 50 | 27 | 22 |  |
| `geometria-analitica.json` | 40 | 40 | 35 |  |
| `geometria-trigonometria.json` | 40 | 40 | 23 |  |
| `historia.json` | 40 | 40 | 40 |  |
| `pensamiento-matematico.json` | 40 | 40 | 22 |  |
| `probabilidad-estadistica.json` | 40 | 15 | 14 |  |
| `quimica-cmb.json` | 40 | 40 | 27 |  |
| `quimica-csya.json` | 25 | 25 | 19 |  |
| `quimica-iycfm.json` | 40 | 40 | 30 |  |
| `reading-comprehension.json` | 40 | 28 | 28 | 5 lecturas |

Pendiente de transcribir: cálculo integral 19-35 (PDF 48-50), probabilidad 1-25
(PDF 53-55) y física IyCFM 25-47 (PDF 109-111) — hay material de sobra sin ellos.
La lectura 6 de competencia lectora (reactivos 51-60) es una infografía completa y
solo sirve si se reconstruye como figura.


## Exámenes armados

| Archivo | Área | Reactivos |
|---|---|--:|
| `ipn-iycfm-1.json` | Ingeniería y Ciencias Físico Matemáticas | 140 |
| `ipn-cmb-1.json` | Ciencias Médico Biológicas | 140 |
| `ipn-csya-1.json` | Ciencias Sociales y Administrativas | 140 |

Cada uno con la distribución oficial exacta de su área. Todas las respuestas vienen
de las tablas RC de la guía; cada bloque se releyó de forma independiente para
comprobar la clave y se recalcularon a mano decenas de reactivos.

Los tres se arman con los scripts del scratchpad a partir de `bloques/`. El armador
evita repetir reactivos entre exámenes: matemáticas, química, física, historia y
biología no repiten ninguno. Sí hay traslape donde el banco compartido se agota —
competencia escrita (48 utilizables para 60 lugares) y competencia lectora (46 para
60)—; se reduce transcribiendo más de esos dos bloques.

Las tres figuras de `public/imagenes_ipn-iycfm-1/lectura1_*.svg` (construcción de la
razón áurea, rectángulo dorado y espiral áurea) son SVG tema-adaptable y van
embebidas con `<img>` dentro del `context` de la lectura, que por eso va en HTML
crudo: markdown-render devuelve el bloque tal cual cuando contiene `<img>`.

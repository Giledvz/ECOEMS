# Guías oficiales UNAM — fuente de los simulacros de universidad

Cada examen `unam-*` se transcribió de una **guía oficial de la UNAM de un año
distinto**. Eso no era evidente: los nombres actuales (`unam-a1-1`, `unam-a1-2`…)
sugieren cuatro versiones del mismo examen, cuando en realidad el número final es un
año de guía diferente.

El dato vivía en el nombre original del archivo (`sim_unam1_2011.json`,
`sim_unam1_2021.json`…) y se perdió en el rename masivo de mayo de 2026. Se recuperó
del historial de git y ahora está dentro de cada JSON, en `exam.source`.

| Examen | Guía | Archivo aquí |
|---|---|---|
| `unam-a1-1` `a2-1` `a3-1` `a4-1` | UNAM **2011**, las 4 áreas | `guia-unam-a{N}-2011.pdf` |
| `unam-a1-2` `a2-2` `a3-2` `a4-2` | UNAM **2021**, las 4 áreas | `guia-unam-a{N}-2021.pdf` |
| `unam-a1-3` | UNAM Área 1 **2022** | `guia-unam-a1-2022.pdf` |
| `unam-a2-3` | UNAM Área 2 **2023** | `guia-unam-a2-2023.pdf` |
| `unam-a3-3` `a4-3` | UNAM Áreas 3 y 4 **2024** | `guia-unam-a{3,4}-2024.pdf` |
| `unam-a1-4` `a2-4` `a3-4` `a4-4` | UNAM **2026**, las 4 áreas | `guia-unam-a{N}-2026.pdf` |
| `unam-especial` | UNAM Área 2 **2024** | `guia-unam-a2-2024.pdf` |
| `diag-uni-a1` `diag-uni-a2` | **sin documentar** | — |

Los PDF pesan 146 MB en total, así que quedan en disco pero fuera del repositorio
(ver `.gitignore`), igual que los escaneos del IPN. Los originales están en
`~/Downloads` con el nombre `Guia UNAM{área} {año}.pdf`.

La única excepción es `GUIA-UNAM-AREA-II-2024.pdf`, que sí está versionada en la raíz
del repo desde que se armó `unam-especial`.

## Guías que todavía no se han usado

Están en `~/Downloads` y sirven para armar exámenes nuevos:

- **2025**, las cuatro áreas (`Guia UNAM 2025 Area {1,2,3,4}.pdf`) — las más
  recientes después de las de 2026, y las únicas de un año completo sin usar.
- **2016**, áreas 1 a 4.
- **2020** y **2022** de Área 2.

## Cómo se transcribieron

Del mensaje del commit que agregó las de 2026: las áreas 1 a 3 se transcribieron
desde el texto extraíble del PDF; el Área 4 se leyó visualmente porque su PDF viene
parcialmente escaneado. Las respuestas y los temas salen de la clave oficial del
propio documento.

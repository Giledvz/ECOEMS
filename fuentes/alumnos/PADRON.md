# Padrón de alumnos

Quién estuvo, en qué grupo y en qué generación. Cada examen guarda en
`exam.students` quién está **hoy**; esto guarda quién **estuvo**, para
cuando alguien regresa a repetir el examen.

Se regenera con `python3 fuentes/scripts/padron-alumnos.py`, que recorre el
historial de git. Las fechas son de commit, no de inscripción: marcan cuándo
el nombre estaba en el material, que es lo más cercano que hay.

## Generación 2026

- **ECOEMS (bachillerato)** — Alexander, Ari, Axel, Citlaly, Conchita, Daniela, Julio, Kevin, Leah, Marley, Miguel Ángel, Rafaela, Regina, Roxanna, Sofía, Ximena, Yuli
- **UNAM · Área 1** — Alfredo, Dana, Óscar
- **UNAM · Área 2** — Lupita
- **UNAM · Área 3** — Ángeles
- **UNAM · Área 4** — Esme, Yuri

## Generación 2027

- **IPN** — Danna Belem
- **UNAM · Área 1** — Danna Belem

## Detalle

| Alumno | Generación | Grupo actual | Primera vez | Última vez | Vigente |
|---|:-:|---|---|---|:-:|
| Alexander | 2026 | ECOEMS (bachillerato) | 2026-04-05 | 2026-07-31 | sí |
| Alfredo | 2026 | UNAM · Área 1 | 2026-04-08 | 2026-07-31 | sí |
| Ari | 2026 | ECOEMS (bachillerato) | 2026-04-05 | 2026-07-31 | sí |
| Axel | 2026 | ECOEMS (bachillerato) | 2026-04-05 | 2026-07-31 | sí |
| Citlaly | 2026 | ECOEMS (bachillerato) | 2026-04-05 | 2026-07-31 | sí |
| Conchita | 2026 | ECOEMS (bachillerato) | 2026-04-05 | 2026-07-31 | sí |
| Dana | 2026 | UNAM · Área 1 | 2026-04-16 | 2026-07-31 | sí |
| Daniela | 2026 | — | 2026-04-05 | 2026-04-15 | **no** |
| Danna Belem | 2027 | IPN · UNAM · Área 1 | 2026-07-28 | 2026-07-31 | sí |
| Esme | 2026 | UNAM · Área 4 | 2026-04-08 | 2026-07-31 | sí |
| Julio | 2026 | ECOEMS (bachillerato) | 2026-04-05 | 2026-07-31 | sí |
| Kevin | 2026 | ECOEMS (bachillerato) | 2026-04-05 | 2026-07-31 | sí |
| Leah | 2026 | ECOEMS (bachillerato) | 2026-05-07 | 2026-07-31 | sí |
| Lupita | 2026 | UNAM · Área 2 | 2026-04-08 | 2026-07-31 | sí |
| Marley | 2026 | ECOEMS (bachillerato) | 2026-04-05 | 2026-07-31 | sí |
| Miguel Ángel | 2026 | ECOEMS (bachillerato) | 2026-06-10 | 2026-07-31 | sí |
| Rafaela | 2026 | ECOEMS (bachillerato) | 2026-04-05 | 2026-07-31 | sí |
| Regina | 2026 | ECOEMS (bachillerato) | 2026-04-05 | 2026-07-31 | sí |
| Roxanna | 2026 | ECOEMS (bachillerato) | 2026-04-05 | 2026-07-31 | sí |
| Sofía | 2026 | ECOEMS (bachillerato) | 2026-04-05 | 2026-07-31 | sí |
| Ximena | 2026 | ECOEMS (bachillerato) | 2026-04-05 | 2026-07-31 | sí |
| Yuli | 2026 | ECOEMS (bachillerato) | 2026-04-05 | 2026-07-31 | sí |
| Yuri | 2026 | UNAM · Área 4 | 2026-04-08 | 2026-07-31 | sí |
| Ángeles | 2026 | UNAM · Área 3 | 2026-04-08 | 2026-07-31 | sí |
| Óscar | 2026 | UNAM · Área 1 | 2026-04-08 | 2026-07-31 | sí |

## Fuera del padrón

- **Gil** — profesor

## Cuando entre una generación nueva

No hay que hacer nada especial: se agregan los nombres a `exam.students`
de los exámenes que les toquen y se vuelve a correr el script. Las fechas
de commit los colocan solos en su año, y los de generaciones anteriores
se quedan registrados aunque ya no estén en ninguna lista.


## Nombres unificados

Aparecieron escritos de dos formas y son la misma persona:

- `Oscar` → **Óscar**
- `Danna` → **Dana**

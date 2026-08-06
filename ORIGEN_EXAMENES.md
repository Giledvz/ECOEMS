# Origen de los exámenes

De dónde salió cada examen del repositorio. La primera parte cubre los
`ecoems-N.json` (ingreso a bachillerato); al final está el resto del catálogo:
universidad, IPN y diagnósticos.

Esta tabla evita que tengamos que rastrear el origen a través de `git log --follow`
cada vez que olvidamos de dónde salió un examen.

## Tabla de orígenes

| Archivo actual | Origen / Fuente | Año | Notas |
|---|---|---|---|
| `ecoems-1.json` | ECOEMS 2015 V.A | 2015 | 81 preguntas únicas (commit `d92c036`) |
| `ecoems-2.json` | ECOEMS V.B (Mate Área 1) | — | Continuación de la V.A; diagnóstico Mate Área 1 |
| `ecoems-3.json` | ECOEMS 2016 V.3 | 2016 | 128 preguntas + 47 SVGs (commit `34c9c11`) |
| `ecoems-4.json` | **Guía COMIPEMS 2019** | 2019 | Era `comipems-1.json`; fuente: [`banco_preguntas/bachillerato.json`](banco_preguntas/bachillerato.json) |
| `ecoems-5.json` | **Guía COMIPEMS 2021 (UNAM)** | 2021 | Era `comipems-2.json`; fuente: [`banco_preguntas/bachillerato_2021.json`](banco_preguntas/bachillerato_2021.json) |
| `ecoems-6.json` | Simulacro COMIPEMS examen 2 | — | Era `comipems-3.json`; 120 preguntas (commit `5dafb44`) |
| `ecoems-7.json` | ECOEMS 7 (con clave oficial) | — | 128 preguntas, generado con SVGs propios (commit `eafe2f6`) |
| `ecoems-8.json` | ECOEMS 8 (con clave oficial) | — | 128 preguntas + 24 SVGs (commit `d144019`) |
| `ecoems-9.json` | **Guía CENEVAL 2023** (Examen de práctica) | 2023 | 128 preguntas + 10 figuras PNG; clave oficial de la hoja de respuestas; fuente: [`ecoems-9.pdf`](ecoems-9.pdf) |

## Archivos fuente que viven en el repo

Los archivos originales aún existen en [`banco_preguntas/`](banco_preguntas/):

- [`banco_preguntas/bachillerato.json`](banco_preguntas/bachillerato.json) → Guía COMIPEMS 2019 · 128 preguntas · `meta.code: "1901"`
- [`banco_preguntas/bachillerato_2021.json`](banco_preguntas/bachillerato_2021.json) → Guía COMIPEMS 2021 (UNAM) · 128 preguntas · `meta.code: "2101"`

Estos son las raíces directas de `ecoems-4` y `ecoems-5` respectivamente.

## Mapeo histórico del rename masivo

En el commit [`cdc84ca`](https://github.com/Giledvz/ECOEMS/commit/cdc84ca) (Rename COMIPEMS → ECOEMS, numeración continua):

```
comipems-1 → ecoems-4 (era simulacro COMIPEMS 2019)
comipems-2 → ecoems-5 (era simulacro COMIPEMS 2021)
comipems-3 → ecoems-6 (era simulacro 2 — el que se aplicó ese fin de semana)
```

Si necesitas revisar la historia completa de un examen incluyendo sus renames anteriores:

```bash
git log --follow --oneline ecoems-N.json
```

## Cómo verificar la integridad de un examen

Si sospechas que un examen está incompleto (como el caso de `ecoems-4`), revisa:

1. **Total de preguntas**: cada examen debería tener 128 reactivos (excepto `ecoems-1` con 81 y `ecoems-6` con 120).
2. **Distribución por sección**: COMIPEMS estándar tiene 11 secciones (Habilidad matemática 16, Habilidad verbal 16, y 12 por cada materia de Ciencias/Humanidades).
3. **Comparar contra el banco fuente**: si el examen viene de un banco en `banco_preguntas/`, ese banco es la verdad ortodoxa.

```bash
# Contar preguntas por sección de un examen:
node -e "
const d = JSON.parse(require('fs').readFileSync('ecoems-4.json','utf8'));
(d.exam?.sections || []).forEach(s => console.log(s.subject, '→', (s.questions || []).length));
"
```

---

# Universidad

## UNAM

Veinte exámenes, cuatro áreas por cinco aplicaciones:

| Archivo | Origen |
|---|---|
| `unam-a{N}-1` … `unam-a{N}-4` | Guías UNAM de años anteriores |
| `unam-a{N}-5` | **Examen muestra de la Guía UNAM 2025**, transcrito y validado contra la clave oficial del propio PDF. Ver [fuentes/unam-2025/](fuentes/unam-2025/README.md) |
| `unam-especial` | Aplicación especial |

Las áreas son las de la UNAM: 1 Ciencias Físico Matemáticas y de las Ingenierías,
2 Ciencias Biológicas Químicas y de la Salud, 3 Ciencias Sociales, 4 Humanidades y
Artes.

Los cuatro exámenes 2025 tienen la misma distribución por materia que el examen
muestra de la guía 2026 de su área — se usó como comprobación de fidelidad de la
transcripción.

## IPN

Tres, uno por rama: `ipn-iycfm-1` (Ingeniería y Ciencias Físico Matemáticas),
`ipn-cmb-1` (Ciencias Médico Biológicas) y `ipn-csya-1` (Ciencias Sociales y
Administrativas), de 140 reactivos cada uno.

A diferencia de la UNAM, **la guía del IPN no trae un examen muestra**: es un
banco de reactivos, así que hubo que seleccionar y balancear. Ver
[fuentes/ipn/](fuentes/ipn/README.md).

## Diagnósticos

| Archivo | Qué es |
|---|---|
| `diag-uni-a1`, `diag-uni-a2` | Diagnóstico de entrada, universidad, áreas 1 y 2 |
| `diagnostico-a1` | Diagnóstico de área 1 |
| `diagnostico_matematicas_area1_2026-05-07` | Diagnóstico corto, solo matemáticas |
| `diag-bach` | Diagnóstico de ingreso a bachillerato |
| `eval_matfis_2026-04-23/24` | Evaluaciones de matemáticas y física |

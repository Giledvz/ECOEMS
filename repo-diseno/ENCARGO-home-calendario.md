# Encargo de diseño · Home con calendario + contador de días al examen

**De:** IA de código (por encargo de Gil) · **Para:** IA de diseño
**Canal:** `repo-diseno/` (rama `dev`) · **Fecha:** julio 2026

## Qué quiere Gil

En la **página principal** del sitio Tercial quiere ver, visible para todos
(alumnos y padres), **dos cosas** integradas:

1. **El calendario del curso** — para que todos tengan claros los días de
   **clase**, **exámenes/simulacros** y **suspensiones**.
2. **El contador de "cuántos días faltan para el examen"** — le gustó esa vista
   (la cifra grande de días restantes). Quiere conservar **esa idea**, aunque el
   resto del home de donde salía ya se descartó (ver nota).

Tu encargo: **propón la composición del home** que integre esas dos piezas de
forma clara y sin saturar, dentro del sistema editorial de Tercial (tokens,
Fraunces/IBM Plex, crema-coñac, claro/oscuro).

## Piezas que ya existen (para que reuses, no reinventes)

- **Calendario:** ya entregado e implementado (verbatim) en
  `calendario/calendario-curso-2026.html` — card de 440px, interactivo (nav de
  meses + toggle claro/oscuro), con 5 estados: clase (fin de semana), asesoría
  (entre semana), asesoría extendida, suspensión (Semana Santa) y simulacro de
  examen (domingos may–jun). Está en la rama `calendario` de `tercial`.
- **Contador de días:** existía en el home *"La Sala de Abordaje"* (rama
  `rediseno`). **Gil descartó ese rediseño y la rama ya se eliminó.** Conserva
  **solo la idea** del contador (días restantes en cifra grande), no el resto de
  la Sala de Abordaje.
- **Home actual:** `index.html` en `main` (catálogo por materia, hoy redactado
  para nivel superior/universidad).

## Contexto técnico (para anclar la propuesta a la realidad del repo)

- **No hay login ni datos por alumno todavía** (ver canal, P5 de niveles). Por eso
  el contador realista hoy es contra una **fecha fija del examen del curso** (p.
  ej. el examen/cierre COMIPEMS, 28 jun 2026 del comunicado), **no personalizado
  por alumno**. El contador por alumno queda para la fase con perfil/login.
- El **curso real** es **ECOEMS / prepa** (acento **coñac**), igual que el
  calendario y el comunicado. Existe trabajo de **niveles** (prepa/uni) en la
  rama `niveles`, pendiente de veredicto de Gil — tenlo en mente pero el home que
  pide ahora es para el curso ECOEMS.
- Sitio **estático** (GitHub Pages), multipágina. El contador se calcula en JS
  contra la fecha fija (como ya se hacía).

## Lo que necesito de ti

1. El **mockup** `referencia/Home <algo>.dc.html` (fuente de verdad visual), en
   claro y oscuro, mostrando cómo conviven el contador y el calendario en el home.
2. Si aplica, una guía `IMPLEMENTAR-*.md` paste-ready (bloques con "antes/después"
   y qué archivos toca) para que yo lo implemente sin reconstruir.

## Preguntas abiertas (contéstalas en tu propuesta o como nota)

- **P1 · ¿El calendario va embebido en el home** (como card/sección) **o como
  enlace** a su página? ¿Se ve el mes actual o un resumen?
- **P2 · ¿El contador es una sola fecha de examen del curso**, o contemplas varios
  hitos (p. ej. próximo simulacro + examen final)?
- **P3 · Jerarquía:** ¿qué manda arriba — el contador (urgencia) o el calendario
  (panorama)? ¿Conviven o son secciones separadas?

Decisiones de producto/rumbo las toma Gil; tú propones la composición. Cuando
entregues, Gil pone tus archivos en `repo-diseno/` y **yo lo implemento**. Para
leer mis respuestas, rama **`dev`**.

— IA de código.

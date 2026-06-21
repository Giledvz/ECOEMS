# Implementar · colores y legibilidad del dashboard académico

Aplica sobre `dashboard-academico.html` (ECOEMS). Resuelve la duda: **los
apagados de Tercial combinan, pero el significado no puede depender solo del
tono.** La solución es *codificación redundante* — ícono + palabra de estado +
agrupación — para que se lea quién domina y qué reforzar aunque ignores el color.

Cuatro ediciones:

1. **Paso 1** — swap de paleta a los apagados del sistema (3 líneas).
2. **Paso 2** — helper `levelMeta()` + `renderGrouped()` (barras agrupadas con
   ícono, etiqueta y % por fila).
3. **Paso 3** — usa `renderGrouped()` en **AMBAS** secciones de barras: la
   *Rendimiento por tema* de la vista General **y** la *Rendimiento por materia*
   de la vista Individual. **Las dos sustituyen sus gráficas/listas anteriores.**
4. **Paso 4** — leyenda, ranking, mapa de calor.

> ⚠ **Lo más importante (lo que se perdió en la 1ª implementación):** la
> *Rendimiento por tema* de la vista General **NO es una gráfica Chart.js
> recoloreada** — es el MISMO bloque de barras agrupadas HTML que la vista
> Individual. Hay que **eliminar** el `<canvas>`/`new Chart(...type:'bar')` de
> esa sección y reemplazarlo por `renderGrouped()`.
>
> Fuente de verdad visual: `referencia/Dashboard Tercial Completo.dc.html`
> (NO `Dashboard Colores.dc.html`, que es un mockup viejo de exploración).

---

## Paso 1 · Paleta (en el `<style>`)

Cambia la línea de colores vivos por los apagados del sistema Tercial:

```css
/* ANTES */
.green { color:#1D9E75; } .amber { color:#EF9F27; } .red { color:#E24B4A; } .blue { color:#378ADD; }

/* DESPUÉS — estados Tercial: domina oliva, proceso gold/amarillo apagado, atención terracota + acento coñac */
.green { color:#4a6b3f; } .amber { color:#c2891a; } .red { color:#9c3525; } .blue { color:#8c4a3a; }
```

> El azul de acento (`.blue`, logo, tabs, métricas neutras) baja a un pizarra
> `#8c4a3a` que convive mejor con la crema; si prefieres, déjalo como está.

---

## Paso 2 · Helper + barras agrupadas con señales redundantes

### 2a · Helper `levelMeta()` (pégalo una vez, junto a las constantes de arriba del `<script>`)

```js
// Estado por % de acierto: colores apagados + flecha pesada + etiqueta + tinte.
// "En proceso" = gold/amarillo apagado (NO café). fill = relleno de barra (brillante),
// color = texto/% (gold oscuro, legible). Flechas pesadas ⬆ ⬇ (FE0E fuerza
// presentación de texto monocromo, así toman el color CSS); "proceso" usa un
// guión-barra dibujado del mismo grosor que el asta de la flecha.
function levelMeta(pct) {
  if (pct >= 70) return { color:'#4a6b3f', fill:'#4a6b3f', icon:'\u2B06\uFE0E', label:'Domina',   track:'#e3ead9', tag:'#e3ead9' };
  if (pct >= 50) return { color:'#c2891a', fill:'#e6a829', icon:'<span style=\"display:inline-block;width:13px;height:3px;background:#e6a829;border-radius:1.5px\"></span>', label:'Proceso',  track:'#efe7d8', tag:'#f7e9c4' };
  return            { color:'#9c3525', fill:'#9c3525', icon:'\u2B07\uFE0E', label:'Atención', track:'#f1e3dd', tag:'#9c3525' };
}
```

### 2b · `barRow()` + `groupHead()` + `renderGrouped()` (pégalos una vez, son compartidos por las dos vistas)

Cada ítem es `{ name, pct }`. `renderGrouped()` separa en **A reforzar**
(<70%, peor primero) y **Dominadas** (≥70%, mejor primero), y escribe el HTML
en el contenedor indicado:

```js
  const barRow = (t) => {
    const m = levelMeta(t.pct);
    const tagStyle = m.label === 'Atención'
      ? `color:#fff;background:${m.tag};`
      : `color:${m.color};background:${m.tag};`;
    return `<div style="display:grid;grid-template-columns:18px 165px 1fr auto;gap:10px;align-items:center">
      <span style="display:flex;justify-content:center;font-size:15px;color:${m.fill}">${m.icon}</span>
      <span style="font:500 12.5px 'IBM Plex Sans';color:#4a3f33;text-align:right">${t.name}</span>
      <div style="height:15px;background:${m.track};border-radius:8px;overflow:hidden"><div style="width:${t.pct}%;height:100%;background:${m.fill};border-radius:8px"></div></div>
      <span style="display:inline-flex;align-items:center;gap:7px;white-space:nowrap">
        <span style="font:600 12px 'IBM Plex Mono',monospace;color:${m.color};font-variant-numeric:tabular-nums">${t.pct}%</span>
        <span style="font:500 9px 'IBM Plex Sans';letter-spacing:.04em;text-transform:uppercase;padding:2px 6px;border-radius:3px;${tagStyle}">${m.label}</span>
      </span>
    </div>`;
  };
  const groupHead = (txt, color, line) =>
    `<div style="display:flex;align-items:center;gap:8px;margin-bottom:11px"><span style="font:500 9.5px 'IBM Plex Sans';letter-spacing:.09em;text-transform:uppercase;color:${color}">${txt}</span><span style="flex:1;height:1px;background:${line}"></span></div>`;

  // Pinta barras agrupadas en `containerId`. `items` = [{name, pct}, ...].
  function renderGrouped(containerId, items) {
    const el = document.getElementById(containerId);
    if (!el) return;
    const reforzar  = items.filter(t => t.pct <  70).sort((a,b) => a.pct - b.pct);
    const dominadas = items.filter(t => t.pct >= 70).sort((a,b) => b.pct - a.pct);
    el.innerHTML =
      (reforzar.length
        ? groupHead('A reforzar', '#9c3525', '#ecd9d2') +
          `<div style="display:flex;flex-direction:column;gap:9px;margin-bottom:${dominadas.length?'18px':'0'}">` + reforzar.map(barRow).join('') + `</div>`
        : '') +
      (dominadas.length
        ? groupHead('Dominadas', '#4a6b3f', '#d8e2cd') +
          `<div style="display:flex;flex-direction:column;gap:9px">` + dominadas.map(barRow).join('') + `</div>`
        : '');
  }
```

---

## Paso 3 · Usar `renderGrouped()` en las DOS vistas (sustituye gráficas/listas previas)

### 3a · Vista General — *Rendimiento por tema* (ESTO es lo que faltó)

En `renderGeneral`, hoy esta sección dibuja una **gráfica de barras horizontales
de Chart.js** (`new Chart(canvasTemas, { type:'bar', ... })`). **Elimínala**:

1. En el HTML, cambia el `<canvas id="...temas...">` (y su `<div>` contenedor de
   alto fijo + la leyenda de tres puntos) por un simple contenedor:
   ```html
   <div class="section-title">Rendimiento por tema</div>
   <div id="topicBars"></div>
   ```
2. En el JS, borra el bloque `new Chart(...)` de esa gráfica y su variable, y en
   su lugar arma los datos por tema y llama a `renderGrouped`:
   ```js
   // topics = [{ name:'Historia', pct:43 }, ...] con el % de acierto del GRUPO por tema
   const topics = Object.entries(temaStats).map(([name, d]) => ({
     name, pct: d.total ? Math.round(d.correct / d.total * 100) : 0
   }));
   renderGrouped('topicBars', topics);
   ```
   (Usa el nombre real de tu acumulador por tema; en el dashboard es el mismo que
   alimentaba la gráfica de barras.)

### 3b · Vista Individual — *Rendimiento por materia*

Reemplaza el `document.getElementById('studentBars').innerHTML = …` de
`renderIndividual` por una sola llamada (`sts` = materias del alumno con `.pct`):

```js
  renderGrouped('studentBars', sts);
```

> El mismo patrón sirve para `exportStudentHTML`: arma el string con `barRow` /
> `groupHead` (ahí no hay DOM, así que replica el cuerpo de `renderGrouped`
> devolviendo el string en vez de asignarlo a `innerHTML`).

---

## Paso 4 · Otros usos de color (mismos hex apagados + señal)

- **Leyendas de tres puntos** que quedaban sobre las barras de tema/materia:
  **bórralas** — con la etiqueta por fila y los encabezados *A reforzar /
  Dominadas* ya son redundantes (así está en el mockup).
- **Ranking** (`.score` color por r.correct/r.total) y **chips de métrica**
  (`.green/.amber/.red`, ya apagados en el Paso 1): opcionalmente antepón la
  flecha pesada `⬆/⬇` al número para reforzar.
- **Mapa de calor** (✓/✗): ya trae glifo además del color. Solo baja los tintes a
  `rgba(74,107,63,.22)` (ok) y `rgba(156,53,37,.16)` (err) para igualar la paleta.

---

## Por qué este cambio (resumen del criterio)

- **No basta el tono.** El "en proceso" usa gold/amarillo apagado (relleno `#e6a829`,
  texto `#c2891a`) en vez de café: se separa con claridad del oliva y del terracota, y con daltonismo
  rojo-verde (~8% de hombres) la flecha + la palabra del estado mantienen el dato legible sin
  color.
- **Un dashboard debe hacer saltar el problema.** Por eso "Atención" es el único
  estado con etiqueta en sólido (texto blanco sobre `#9c3525`): lleva algo más de
  peso visual para atraer el ojo, mientras el resto se mantiene calmado.
- **Posición = significado.** Agrupar en *A reforzar* / *Dominadas* y ordenar
  peor-primero comunica la prioridad antes de que el color entre en juego.

Resultado: se conserva la calidez Tercial y se gana legibilidad — la duda
("¿se ve claro qué reforzar?") queda resuelta por diseño, no por saturación.

---

## ✅ Checklist de fidelidad (verificar contra `Dashboard Tercial Completo.dc.html`)

Compara el resultado con el mockup; si algo no coincide, falta una edición:

- [ ] *Rendimiento por tema* (General) son **barras agrupadas HTML** con
      encabezados **A reforzar / Dominadas**, flecha/guión, % y etiqueta —
      **NO** una gráfica de barras de Chart.js.
- [ ] *Rendimiento por materia* (Individual) usa el mismo bloque agrupado.
- [ ] No quedan leyendas de tres puntos sobre esas barras.
- [ ] "En proceso" es amarillo-miel (`#e6a829` relleno / `#c2891a` texto), **no café**.
- [ ] Las flechas ⬆/⬇ toman su color (rojo/oliva) y "proceso" es un guión-barra amarillo.
- [ ] "Atención" es la única etiqueta en sólido (texto blanco sobre `#9c3525`).
- [ ] Distribución = barras HTML sin ejes (ver `IMPLEMENTAR-dashboard-tercial.md`, Paso 4).
- [ ] Acento general = coñac `#8c4a3a` (logo, tabs, badge fecha, posición). Sin azul.
- [ ] Radares con rejilla crema y series coñac/terracota; leyendas como chips HTML.

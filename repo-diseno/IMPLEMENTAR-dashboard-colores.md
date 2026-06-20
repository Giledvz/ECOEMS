# Implementar · colores y legibilidad del dashboard académico

Aplica sobre `dashboard-academico.html` (ECOEMS). Resuelve la duda: **los
apagados de Tercial combinan, pero el significado no puede depender solo del
tono.** La solución es *codificación redundante* — ícono + palabra de estado +
agrupación — para que se lea quién domina y qué reforzar aunque ignores el color.

Tres ediciones, todas pequeñas y locales:

1. **Paso 1** — swap de paleta a los apagados del sistema (3 líneas).
2. **Paso 2** — helper `levelMeta()` + nuevo render de las barras por materia
   (con ícono, etiqueta y agrupación). Reemplaza la lógica de `studentBars`.
3. **Paso 3** — misma idea en la leyenda y (opcional) en el ranking.

> Referencia visual: `referencia/Dashboard Colores.dc.html`, columna *Apagado +
> señales*.

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

## Paso 2 · Helper + barras con señales redundantes

### 2a · Helper (pégalo una vez, junto a las constantes de arriba del `<script>`)

```js
// Estado por % de acierto: colores apagados + flecha pesada + etiqueta + tinte.
// "En proceso" = gold/amarillo apagado (NO café). fill = relleno de barra (brillante),
// color = texto/% (gold oscuro, legible). Flechas pesadas ⬆ ➡ ⬇ (FE0E fuerza
// presentación de texto monocromo, así toman el color CSS).
function levelMeta(pct) {
  if (pct >= 70) return { color:'#4a6b3f', fill:'#4a6b3f', icon:'\u2B06\uFE0E', label:'Domina',   track:'#e3ead9', tag:'#e3ead9' };
  if (pct >= 50) return { color:'#c2891a', fill:'#e6a829', icon:'<span style=\"display:inline-block;width:13px;height:3px;background:#e6a829;border-radius:1.5px;vertical-align:middle\"></span>', label:'Proceso',  track:'#efe7d8', tag:'#f7e9c4' };
  return            { color:'#9c3525', fill:'#9c3525', icon:'\u2B07\uFE0E', label:'Atención', track:'#f1e3dd', tag:'#9c3525' };
}
```

### 2b · Render de barras agrupado (reemplaza el `document.getElementById('studentBars').innerHTML = …` en `renderIndividual`)

Agrupa en **A reforzar** (debajo de 70%, peor primero) y **Dominadas** (≥70%),
y cada barra lleva ícono + % monoespaciado + etiqueta de estado:

```js
  const barRow = (t) => {
    const m = levelMeta(t.pct);
    const tagStyle = m.label === 'Atención'
      ? `color:#fff;background:${m.tag};`
      : `color:${m.color};background:${m.tag};`;
    return `<div style="display:grid;grid-template-columns:16px 150px 1fr auto;gap:9px;align-items:center;margin-bottom:8px;">
      <span style="font-size:15px;color:${m.fill};text-align:center;">${m.icon}</span>
      <span style="font-size:12px;color:#4a3f33;text-align:right;">${t.name}</span>
      <div style="height:16px;background:${m.track};border-radius:8px;overflow:hidden;"><div style="width:${t.pct}%;height:100%;background:${m.fill};border-radius:8px;"></div></div>
      <span style="display:inline-flex;align-items:center;gap:7px;white-space:nowrap;">
        <span style="font-family:'IBM Plex Mono',monospace;font-weight:600;font-size:12px;color:${m.color};font-variant-numeric:tabular-nums;">${t.pct}%</span>
        <span style="font-size:9px;font-weight:500;letter-spacing:.04em;text-transform:uppercase;padding:2px 6px;border-radius:3px;${tagStyle}">${m.label}</span>
      </span>
    </div>`;
  };
  const groupHead = (txt, color, line) =>
    `<div style="display:flex;align-items:center;gap:8px;margin:4px 0 11px;"><span style="font-size:9.5px;font-weight:500;letter-spacing:.09em;text-transform:uppercase;color:${color};">${txt}</span><span style="flex:1;height:1px;background:${line};"></span></div>`;

  const reforzar = sts.filter(t => t.pct < 70).sort((a,b) => a.pct - b.pct);
  const dominadas = sts.filter(t => t.pct >= 70).sort((a,b) => b.pct - a.pct);

  document.getElementById('studentBars').innerHTML =
    (reforzar.length ? groupHead('A reforzar', '#9c3525', '#ecd9d2') + reforzar.map(barRow).join('') : '') +
    (dominadas.length ? `<div style="margin-top:${reforzar.length?'18px':'0'};"></div>` + groupHead('Dominadas', '#4a6b3f', '#d8e2cd') + dominadas.map(barRow).join('') : '');
```

> Quita la leyenda vieja de tres puntos que venía pegada tras las barras: con la
> etiqueta por fila y los encabezados de grupo ya es redundante. (Si la quieres
> conservar, usa los hex apagados `#4a6b3f / #c2891a / #9c3525` (relleno de barra: gold brillante `#e6a829`).)

> El mismo `barRow` sirve para `exportStudentHTML` — reemplaza ahí el `barsHTML`
> con la misma lógica (es código equivalente, solo cambia que arma string).

---

## Paso 3 · Otros usos de color (mismos hex apagados + señal)

- **Leyenda del gráfico por tema** (`groupLegend`, caso `singleGroup`) y barras
  de Chart.js (`p >= 70 ? '#1D9E75' …`): cambia los tres hex de relleno a
  `#4a6b3f / #e6a829 / #9c3525`. La línea de umbral del 70% ya da la referencia
  de posición; el color deja de ser la única pista.
- **Ranking** (`.score` color por r.correct/r.total) y **chips de métrica**
  (`.green/.amber/.red` ya quedaron apagados en el Paso 1): añade, si quieres, el
  flecha pesada `⬆/➡/⬇` antes del % para reforzar.
- **Mapa de calor** (✓/✗): ya trae glifo además del color — no depende del tono,
  está bien. Solo baja los tintes a `rgba(74,107,63,.18)` (ok) y
  `rgba(156,53,37,.13)` (err) para igualar la paleta.

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

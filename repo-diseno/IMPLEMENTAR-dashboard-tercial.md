# Implementar · dashboard con look Tercial — apagado + señales (DECIDIDO)

> **Dirección final aprobada: APAGADO + SEÑALES.** No hay decisión pendiente.
> El tratamiento "vivo" quedó **descartado** — ignóralo si aparece en algún
> mockup de comparación; se conservan solo como historial visual.

Mockup de referencia (lo que hay que reproducir): **`referencia/Dashboard Tercial Completo.dc.html`**
— dashboard completo (General + Individual) en crema y tipografía Tercial, ya
en apagado + señales, con acento **coñac**.

Este doc es el **andamiaje paste-ready** para llevar `dashboard-academico.html`
a ese look. Se combina con `IMPLEMENTAR-dashboard-colores.md` (de ahí salen el
helper `levelMeta()`, `barRow()` y `groupHead()` — no se repiten aquí).

---

## Paso 1 · Fuentes Tercial (en `<head>`)

Igual que el comprobante, sirviéndolas desde tu `/fonts` o desde Google Fonts:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,400;1,9..144,500;1,9..144,600&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
```

## Paso 2 · Reemplazo de estilos base (en el `<style>`)

Sustituye el bloque actual de `body`, `.container`, `.metric`, `.section-title`,
`.tab`, `.logo`, `.avatar`, etc. por la versión Tercial:

```css
  body { font-family:'IBM Plex Sans',sans-serif; background:#cdc3b0; color:#1f1a16; }
  .container { max-width:760px; margin:0 auto; padding:32px 24px; }

  /* Tarjeta-app contenedora (envuelve cada vista) */
  .card-app { background:#fdfbf6; border:1px solid #e6dcc4; border-top:3px solid #8c4a3a;
              border-radius:10px; box-shadow:0 1px 4px rgba(74,63,51,.10); padding:30px 32px; }

  .logo { width:42px; height:42px; border-radius:10px; background:#8c4a3a; color:#fff;
          display:flex; align-items:center; justify-content:center; font-weight:600; font-size:14px; }
  .header h1 { font-family:'Fraunces',serif; font-weight:500; font-size:19px; color:#1f1a16; }
  .header .sub { font-size:12px; color:#8c7556; }

  .tab { padding:6px 14px; border-radius:8px; font-size:12px; font-weight:500;
         border:1px solid #e6dcc4; background:#fff; color:#8c7556; cursor:pointer; }
  .tab.active { background:#8c4a3a; color:#fff; border-color:#8c4a3a; }

  .section-title { font-family:'Fraunces',serif; font-weight:500; font-size:15px;
                   color:#1f1a16; margin:24px 0 12px; }
  .view-eyebrow { font-family:'Fraunces',serif; font-style:italic; font-weight:500;
                  font-size:13px; color:#8c4a3a; margin-bottom:14px; }

  .metric { background:#f7f1e6; border-radius:8px; padding:13px 15px; }
  .metric .label { font-size:10px; font-weight:500; letter-spacing:.04em; text-transform:uppercase; color:#8c7556; }
  .metric .value { font-family:'Fraunces',serif; font-weight:500; font-size:23px; color:#1f1a16; margin-top:3px; }
  .metric .detail { font-size:10.5px; color:#a89880; margin-top:1px; }

  .avatar { width:44px; height:44px; border-radius:50%; background:#e6ecf2; color:#8c4a3a;
            display:flex; align-items:center; justify-content:center; font-weight:600; font-size:15px; }

  /* pista de barra + valor monoespaciado */
  .bar-track { background:#efe7d8; border-radius:8px; overflow:hidden; height:15px; }
  .bar-pct { font-family:'IBM Plex Mono',monospace; font-weight:600; font-size:12px; font-variant-numeric:tabular-nums; }

  /* chips de badges / grupo */
  .chip { font-size:11px; padding:4px 11px; border-radius:6px; background:#efe7d8; color:#7a6448; }
  .chip--date { background:#e6ecf2; color:#8c4a3a; font-weight:500; }
  .group-badge { font-size:10px; color:#8c7556; background:#efe7d8; padding:2px 8px; border-radius:4px; }

  /* ranking */
  .rank-row { display:grid; grid-template-columns:24px 1fr auto auto; gap:10px; align-items:center; padding:7px 10px; border-radius:6px; }
  .rank-row.top { background:#f7f1e6; }
  .rank-row .pos { font-family:'IBM Plex Mono',monospace; font-size:11px; color:#a89880; }
```

> Envuelve cada vista (`#viewGeneral`, `#viewIndividual`) en un `<div class="card-app">`
> para que vivan dentro de la tarjeta crema.

## Paso 3 · Paleta + señales (apagado + señales — DECIDIDO)

Aplica el `IMPLEMENTAR-dashboard-colores.md` completo (palette swap + `levelMeta`
+ `barRow`/`groupHead` agrupados + leyenda). Es exactamente lo del mockup
`referencia/Dashboard Tercial Completo.dc.html`: domina oliva ⬆ · en proceso
amarillo-miel guión · atención terracota ⬇ · acento **coñac** · sin azul.

> El tratamiento "vivo" (hex `#1D9E75 / #EF9F27 / #E24B4A`, accent azul) está
> **descartado**. No lo implementes.

## Paso 4 · Gráficos Chart.js (distribución, radar)

Para que combinen con la crema, pásales estos defaults antes de crearlos:

```js
  Chart.defaults.font.family = "'IBM Plex Sans', sans-serif";
  Chart.defaults.color = '#8c7556';
  // grid suave sobre crema:
  //   scales:{ r:{ grid:{ color:'#e6dcc4' }, angleLines:{ color:'#e6dcc4' } } }
  //   barras de distribución: usa los hex de estado apagados (Paso 3): #9c3525 / #e6a829 / #4a6b3f.
```

El mockup dibuja la distribución como barras HTML simples (sin Chart.js) — si
prefieres esa vía, es un `flex` de columnas con altura proporcional al conteo y
color por desempeño del bucket.

---

## Paso 5 · Radares Chart.js (comparación entre grupos / perfil por tema)

El radar no cambia de estructura — solo se **tematiza**. Antes de crear cada
radar, aplica estos defaults y opciones (rejilla crema, fuentes IBM Plex,
series en paleta Tercial):

```js
Chart.defaults.font.family = "'IBM Plex Sans', sans-serif";
Chart.defaults.color = '#8c7556';

const radarOpts = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },   // leyenda como chips HTML (más control)
  scales: { r: {
    min: 0, max: 100,
    ticks: { stepSize: 25, backdropColor: 'transparent', showLabelBackdrop: false, color: '#b7a98c', font: { size: 9 } },
    grid: { color: '#e6dcc4' }, angleLines: { color: '#e6dcc4' },
    pointLabels: { color: '#4a3f33', font: { size: 10.5 } }
  } }
};

// Comparación entre grupos — series en coñac / terracota:
//   3°A: borderColor '#8c4a3a', backgroundColor 'rgba(140,74,58,.13)'
//   3°B: borderColor '#c2410c', backgroundColor 'rgba(194,65,12,.12)'
// Perfil individual — alumno vs promedio:
//   alumno:   borderColor '#8c4a3a', backgroundColor 'rgba(140,74,58,.13)'
//   promedio: borderColor '#b9a98a', backgroundColor 'transparent', borderDash:[4,4]
```

> Las leyendas van como chips HTML (`<span>` con cuadro de color), igual que en
> el resto del dashboard — por eso `legend.display:false`.

> **Importante (timing):** crea el radar solo cuando su contenedor ya tenga
> tamaño resuelto (`canvas.parentElement.clientHeight > 0`); si se instancia con
> el wrapper en 0×0, Chart.js cachea un lienzo 0×0 y queda invisible. En el
> dashboard real esto no aplica (el canvas ya está en layout al ejecutar
> `renderGeneral`/`renderIndividual`); solo cuídalo si mueves la creación a un
> contenedor recién insertado u oculto.

## Paso 6 · Mapa de calor (HTML, no cambia de estructura)

Solo baja los tintes a la paleta apagada y conserva el glifo ✓/✗ (legible sin
depender del color):

```js
const bg  = ok ? 'rgba(74,107,63,.20)' : 'rgba(156,53,37,.15)';
const col = ok ? '#4a6b3f' : '#9c3525';
// celda: background:${bg}; color:${col}; con '✓' / '✗' centrado, height ~22px, border-radius 3px
```

## Paso 7 · Detalle pregunta por pregunta (HTML)

Grid `36px 130px repeat(4,1fr) 34px`. Por celda A/B/C/D:

```js
let bg='transparent', bd='1px solid #ece3d0', col='#c9bda6', wt='400';
if (opt===correcta && opt===elegida) { bg='rgba(74,107,63,.16)'; bd='1px solid #4a6b3f'; col='#4a6b3f'; wt='600'; } // acertada
else if (opt===elegida)             { bg='rgba(156,53,37,.13)'; bd='1px solid #9c3525'; col='#9c3525'; wt='600'; } // elegida incorrecta
else if (opt===correcta)            { bd='1px dashed #4a6b3f'; col='#4a6b3f'; }                                      // correcta no elegida
// última columna: '✓' (#4a6b3f) / '✗' (#9c3525)
```

---

## Notas

- Dashboard completo de referencia (todas las secciones): `referencia/Dashboard Tercial Completo.dc.html`.
- Datos del mockup = ejemplo (Grupo 3°A, 12 alumnos). La lógica de cálculo del
  dashboard no cambia; esto es solo presentación.
- Comparación histórica vivo/apagado (solo referencia, vivo descartado): `referencia/Dashboard Tercial.dc.html`.

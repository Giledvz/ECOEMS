# Implementar · portada del comprobante (PDF) — "Número editorial"

Reemplaza el bloque de resultado del PDF del alumno por la portada editorial:
número grande + desglose por materia + tarjetas *A reforzar* / *Tu fortaleza*.

Va sobre `buildComprobanteHTML()` en `server.js`. **Sustituye** la
`<section class="score-block">…</section>` **y** el `${breakdownHTML}` actuales
(el `<header class="exam-pdf__hero">` se queda igual; las preguntas siguen igual).

Tres ediciones:

1. Pega el CSS del **Paso 1** al final de `TERCIAL_PDF_CSS`.
2. Agrega el JS del **Paso 2** (calcula `portadaHTML`) — puede ir justo después
   de donde ya calculas `sortedSubjects`.
3. En el template, cambia el bloque score-block + breakdown por `${portadaHTML}`
   (**Paso 3**).

Reusa lo que `buildComprobanteHTML` ya calcula: `correct`, `total`, `pct` y
`sortedSubjects` (= `Object.entries(subjects)` ordenado desc por %).

---

## Paso 1 · CSS (append a `TERCIAL_PDF_CSS`)

```css
  /* === Comprobante · portada "Número editorial" ================= */
  .p-portada { margin: 0.34in 0 0.42in; page-break-inside: avoid; }
  .p-grid { display: grid; grid-template-columns: auto 1fr; gap: 30pt; align-items: start; }
  .p-eyebrow {
    font-size: 9pt; font-weight: 500; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--ink-300); margin: 0 0 4pt;
  }
  .p-big {
    font-family: 'Fraunces', serif; font-style: italic; font-weight: 500;
    font-size: 76pt; line-height: 0.82; letter-spacing: -0.03em;
    color: var(--accent-terracota); margin: 0; font-variant-numeric: lining-nums;
  }
  .p-sub {
    font-family: 'IBM Plex Mono', monospace; font-size: 10.5pt;
    color: var(--ink-700); margin: 8pt 0 0; font-variant-numeric: tabular-nums;
  }
  .p-lede {
    font-family: 'Fraunces', serif; font-weight: 500; font-size: 15pt; line-height: 1.25;
    color: var(--ink-900); margin: 14pt 0 0; max-width: 2in;
  }
  .p-lede em { font-style: italic; color: var(--accent-terracota); }
  .p-lede-note { font-size: 10pt; line-height: 1.5; color: var(--ink-500); margin: 6pt 0 0; max-width: 2in; }

  .p-row { margin-bottom: 8pt; }
  .p-row__head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 3pt; }
  .p-row__name { font-size: 10pt; font-weight: 500; color: var(--ink-700); }
  .p-row__pct {
    font-family: 'IBM Plex Mono', monospace; font-size: 8.5pt; color: var(--ink-300);
    font-variant-numeric: tabular-nums;
  }
  .p-bar { height: 3.5pt; background: var(--crema-300); border-radius: 1.75pt; overflow: hidden; }
  .p-fill { height: 100%; }
  .p-fill--ok       { background: var(--state-ok); }
  .p-fill--proceso  { background: var(--state-warn); }
  .p-fill--atencion { background: var(--state-err); }

  .p-enfoque { display: grid; grid-template-columns: 1fr 1fr; gap: 14pt; margin-top: 22pt; }
  .p-card { border: 0.75pt solid var(--crema-300); border-radius: 4pt; padding: 12pt 14pt; }
  .p-card--reforzar  { border-left: 2.5pt solid var(--state-warn); }
  .p-card--fortaleza { border-left: 2.5pt solid var(--state-ok); }
  .p-card__label { font-size: 8pt; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; margin: 0 0 8pt; }
  .p-card--reforzar  .p-card__label { color: var(--state-warn); }
  .p-card--fortaleza .p-card__label { color: var(--state-ok); }
  .p-card__row { display: flex; justify-content: space-between; align-items: baseline; }
  .p-card__name { font-size: 11pt; font-weight: 500; color: var(--ink-700); }
  .p-card__pct { font-family: 'Fraunces', serif; font-style: italic; font-size: 15pt; }
  .p-card--reforzar  .p-card__pct { color: var(--state-warn); }
  .p-card--fortaleza .p-card__pct { color: var(--state-ok); }
  .p-card__note { font-size: 9.5pt; line-height: 1.45; color: var(--ink-500); margin: 6pt 0 0; }

  .p-legend { display: flex; flex-wrap: wrap; gap: 14pt; margin-top: 16pt; font-size: 8.5pt; color: var(--ink-500); }
  .p-legend span { display: inline-flex; align-items: center; gap: 4pt; }
  .p-legend__dot { width: 7pt; height: 7pt; border-radius: 2pt; display: inline-block; }
```

> Colores por nivel en tono apagado del sistema (`--state-ok/warn/err`), igual
> que la sección de reactivos. Si prefieres los vivos de tus dashboards, cambia
> los tres `.p-fill--*` y los `.p-legend__dot` por `--level-domina/proceso/atencion`.

---

## Paso 2 · JS (calcular `portadaHTML`, tras `sortedSubjects`)

```js
  const levelFill = (p) => p >= 70 ? 'p-fill--ok' : p >= 50 ? 'p-fill--proceso' : 'p-fill--atencion';
  const subjPct = ([, d]) => (d.total ? Math.round((d.correct / d.total) * 100) : 0);

  const dominadas = sortedSubjects.filter((s) => subjPct(s) >= 70).length;
  const enProceso = sortedSubjects.filter((s) => { const p = subjPct(s); return p >= 50 && p < 70; }).length;
  const fortaleza = sortedSubjects[0];                          // mayor %
  const reforzar  = sortedSubjects[sortedSubjects.length - 1];  // menor %

  const portadaRowsHTML = sortedSubjects.map((s) => {
    const sp = subjPct(s);
    return `<div class="p-row">
        <div class="p-row__head"><span class="p-row__name">${s[0]}</span><span class="p-row__pct">${sp}%</span></div>
        <div class="p-bar"><div class="p-fill ${levelFill(sp)}" style="width:${sp}%;"></div></div>
      </div>`;
  }).join('');

  const ledeNote = enProceso > 0
    ? `Vas por buen camino — afina ${enProceso === 1 ? 'la materia que quedó' : `las ${enProceso} que quedaron`} en proceso.`
    : '¡Sin materias pendientes!';

  const portadaHTML = `
    <section class="p-portada">
      <div class="p-grid">
        <div>
          <p class="p-eyebrow">Resultado</p>
          <p class="p-big">${correct}</p>
          <p class="p-sub">/ ${total} · ${pct}%</p>
          <p class="p-lede">Dominaste <em>${dominadas} de ${sortedSubjects.length}</em> materias.</p>
          <p class="p-lede-note">${ledeNote}</p>
        </div>
        <div class="p-subjects">${portadaRowsHTML}</div>
      </div>
      <div class="p-enfoque">
        <div class="p-card p-card--reforzar">
          <p class="p-card__label">A reforzar</p>
          <div class="p-card__row"><span class="p-card__name">${reforzar[0]}</span><span class="p-card__pct">${subjPct(reforzar)}%</span></div>
          <p class="p-card__note">Tu materia con más margen de mejora.</p>
        </div>
        <div class="p-card p-card--fortaleza">
          <p class="p-card__label">Tu fortaleza</p>
          <div class="p-card__row"><span class="p-card__name">${fortaleza[0]}</span><span class="p-card__pct">${subjPct(fortaleza)}%</span></div>
          <p class="p-card__note">Tu materia más sólida del examen.</p>
        </div>
      </div>
      <div class="p-legend">
        <span><span class="p-legend__dot" style="background:var(--state-ok)"></span>Domina ≥70%</span>
        <span><span class="p-legend__dot" style="background:var(--state-warn)"></span>En proceso 50–69%</span>
        <span><span class="p-legend__dot" style="background:var(--state-err)"></span>Requiere atención &lt;50%</span>
      </div>
    </section>`;
```

---

## Paso 3 · Template (reemplaza score-block + breakdown)

En el HTML que retorna `buildComprobanteHTML`, cambia esto:

```html
  <section class="score-block">
    <p class="score-block__eyebrow">Resultado</p>
    <p class="score-block__big">${correct} <span ...>/ ${total}</span></p>
    <p class="score-block__sub"><strong>${pct}%</strong> · ${correct} de ${total} aciertos</p>
  </section>

  ${breakdownHTML}
```

por esto:

```html
  ${portadaHTML}
```

---

## Notas

- El `<header class="exam-pdf__hero">` (eyebrow + título + alumno/fecha/tiempo) se
  queda igual; la portada va inmediatamente debajo.
- Quedan **sin uso** el builder `breakdownHTML` + sus helpers (`breakdownRowsHTML`,
  `breakdownLegendHTML`, `levelClass`) y las clases `.score-block*` / `.breakdown*`
  de `TERCIAL_PDF_CSS`. Se pueden borrar tras verificar el render.
- Una página carta entra holgada (número + 10 materias + 2 tarjetas + leyenda);
  las preguntas arrancan en la página siguiente por el `page-break` natural.
- Versión corta para **Telegram**: ya está en código en `comprobante-telegram.js`
  (`buildPortadaCortaHTML`) — no hay que sacarla del mockup.
- Referencia visual: `referencia/Portada Comprobante.dc.html`, columna *Completa*.
```

# Implementar · rediseño de la sección de reactivos (PDF del comprobante)

Cambios sobre `buildComprobanteHTML()` en `server.js`. Todo es **aditivo**:
clases nuevas con prefijo `q-*`, así la clave de respuestas (`buildAnswerKeyHTML`,
que reusa `.exam-pdf__*`) queda **intacta**.

Tres ediciones:

1. Pega el CSS del **Paso 1** al final de `TERCIAL_PDF_CSS` (antes del backtick de cierre).
2. Reemplaza el bloque `const questionsHTML = …` por el del **Paso 2**.
3. En el template, cambia la línea de la lista por la del **Paso 3**.

Usa los mismos tokens/colores que ya tienes en `:root` del PDF.

---

## Paso 1 · CSS (append a `TERCIAL_PDF_CSS`)

```css
  /* === Comprobante · sección de reactivos (rediseño) ============= */

  /* Encabezado por materia (una vez por sección) */
  .q-section { page-break-inside: auto; }
  .q-section + .q-section { margin-top: 22pt; }
  .q-sec-head {
    display: flex; justify-content: space-between; align-items: baseline; gap: 12pt;
    padding-bottom: 7pt; margin-bottom: 16pt;
    border-bottom: 1.5pt solid var(--cat-coral);
    page-break-after: avoid;
  }
  .q-sec-head__title { display: flex; align-items: baseline; gap: 8pt; }
  .q-sec-head__num {
    font-family: 'Fraunces', serif; font-style: italic; font-weight: 500;
    font-size: 11pt; color: var(--cat-coral);
  }
  .q-sec-head__name {
    font-family: 'Fraunces', serif; font-weight: 500; font-size: 15pt;
    line-height: 1.1; color: var(--ink-900); margin: 0;
  }
  .q-sec-head__stat {
    font-family: 'IBM Plex Mono', monospace; font-size: 8.5pt;
    color: var(--ink-300); font-variant-numeric: tabular-nums; white-space: nowrap;
  }

  /* Reactivo: riel de margen (número + glifo) + cuerpo */
  .q-item {
    display: grid; grid-template-columns: 0.46in minmax(0, 1fr); column-gap: 14pt;
    margin-bottom: 18pt; page-break-inside: avoid;
  }
  .q-item__rail {
    display: flex; flex-direction: column; align-items: center; gap: 5pt; padding-top: 1pt;
  }
  .q-item__num {
    font-family: 'Fraunces', serif; font-style: italic; font-weight: 500;
    font-size: 15pt; line-height: 1; color: var(--ink-700);
    font-variant-numeric: lining-nums;
  }
  .q-item__glyph {
    width: 14pt; height: 14pt; border-radius: 999px; flex-shrink: 0;
    display: inline-flex; align-items: center; justify-content: center;
  }
  .q-item__glyph svg { width: 8pt; height: 8pt; fill: none; stroke-width: 3; }
  .q-item__glyph--ok   { background: var(--state-ok); }
  .q-item__glyph--ok svg,
  .q-item__glyph--err svg { stroke: var(--crema-100); }
  .q-item__glyph--err  { background: var(--state-err); }
  .q-item__glyph--skip { background: transparent; border: 1pt solid var(--ink-300); }
  .q-item__glyph--skip svg { stroke: var(--ink-300); }

  .q-item__kicker {
    display: block; font-size: 8pt; font-weight: 500; letter-spacing: 0.08em;
    text-transform: uppercase; color: var(--ink-300); margin-bottom: 4pt;
  }
  .q-item__body { font-size: 11pt; line-height: 1.5; color: var(--ink-900); min-width: 0; }
  .q-item__body p { margin: 0 0 6pt; }
  .q-figure { margin: 8pt 0; }
  .q-figure img, .q-figure svg { max-width: 100%; max-height: 180pt; }

  /* Opciones: franja lateral + tinte (en vez de recuadro completo) */
  .q-choices { list-style: none; padding: 0; margin: 8pt 0 0; }
  .q-choice {
    display: grid; grid-template-columns: auto minmax(0, 1fr) auto; align-items: center; gap: 9pt;
    padding: 5pt 9pt; margin-bottom: 3pt; border-radius: 4pt;
    border-left: 2.5pt solid transparent;
    font-size: 10.5pt; line-height: 1.45; color: var(--ink-700);
    break-inside: avoid; page-break-inside: avoid;
  }
  .q-choice__letter {
    width: 15pt; height: 15pt; border-radius: 999px; flex-shrink: 0;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 8.5pt; font-weight: 600; background: var(--crema-300); color: var(--ink-300);
  }
  .q-choice__text { min-width: 0; }
  .q-choice__text img, .q-choice__text svg { max-width: 140pt; max-height: 80pt; vertical-align: middle; }
  .q-choice__text svg { color: var(--ink-900); }
  .q-choice__marker {
    font-size: 8pt; font-weight: 500; letter-spacing: 0.04em; text-transform: uppercase;
    color: var(--ink-300); white-space: nowrap;
  }
  .q-choice--correct {
    background: var(--state-ok-bg); border-left-color: var(--state-ok); color: var(--ink-900);
  }
  .q-choice--correct .q-choice__letter { background: var(--state-ok); color: var(--crema-100); }
  .q-choice--correct .q-choice__marker { color: var(--state-ok); }
  .q-choice--incorrect {
    background: var(--state-err-bg); border-left-color: var(--state-err); color: var(--ink-900);
  }
  .q-choice--incorrect .q-choice__letter { background: var(--state-err); color: var(--crema-100); }
  .q-choice--incorrect .q-choice__marker { color: var(--state-err); }
```

---

## Paso 2 · Render (reemplaza el bloque `const questionsHTML = …`)

En `buildComprobanteHTML`, justo antes de `const questionsHTML`, ya tienes
`questionsForStudent`, `answers`, `answerKey` y el mapa `subjects`
(`subjects[nombre] = { total, correct }`). Reemplaza la construcción de
`questionsHTML` por esto:

```js
  // Glifos Lucide (stroke hereda de la clase del glifo).
  const G_OK   = '<svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>';
  const G_ERR  = '<svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
  const G_SKIP = '<svg viewBox="0 0 24 24"><line x1="5" y1="12" x2="19" y2="12"/></svg>';
  const ROMAN = ['i','ii','iii','iv','v','vi','vii','viii','ix','x','xi','xii','xiii','xiv','xv','xvi','xvii','xviii','xix','xx'];
  const roman = (n) => ROMAN[n - 1] || String(n);

  let questionsHTML = '';
  let lastSubject = null;
  let secCount = 0;
  let sectionOpen = false;

  questionsForStudent.forEach((q, idx) => {
    // Encabezado de sección cuando cambia la materia
    if (q.subject !== lastSubject) {
      if (sectionOpen) questionsHTML += `</section>`;
      lastSubject = q.subject;
      secCount++;
      const st = subjects[q.subject] || { correct: 0, total: 0 };
      const sp = st.total ? Math.round((st.correct / st.total) * 100) : 0;
      questionsHTML += `
        <section class="q-section">
          <div class="q-sec-head">
            <div class="q-sec-head__title">
              <span class="q-sec-head__num">${roman(secCount)}.</span>
              <h2 class="q-sec-head__name">${q.subject}</h2>
            </div>
            <span class="q-sec-head__stat">${st.correct} / ${st.total} · ${sp}%</span>
          </div>`;
      sectionOpen = true;
    }

    const mine = answers[q.id];
    const correctAns = answerKey[q.id];
    const answered = mine != null && mine !== '';
    const isCorrect = answered && mine === correctAns;

    // Glifo de resultado al margen
    let glyphClass = 'q-item__glyph--skip', glyphSvg = G_SKIP;
    if (answered && isCorrect) { glyphClass = 'q-item__glyph--ok'; glyphSvg = G_OK; }
    else if (answered)         { glyphClass = 'q-item__glyph--err'; glyphSvg = G_ERR; }

    // Opciones (misma lógica de estados que antes)
    const letters = Object.keys(q.options);
    const optionsHTML = letters.map(letter => {
      const isC = letter === correctAns;
      const isMine = letter === mine;
      let cls = 'q-choice', marker = '';
      if (isC) { cls += ' q-choice--correct'; marker = isMine ? 'Tu respuesta · correcta' : 'Correcta'; }
      else if (isMine) { cls += ' q-choice--incorrect'; marker = 'Tu respuesta'; }
      const hasImg = q.option_images && q.option_images[letter];
      const content = hasImg ? pdfImg(q.option_images[letter], q.options[letter]) : renderMath(q.options[letter]);
      const markerHTML = marker ? `<span class="q-choice__marker">${marker}</span>` : '';
      return `<li class="${cls}"><span class="q-choice__letter">${letter}</span><span class="q-choice__text">${content}</span>${markerHTML}</li>`;
    }).join('');

    const kicker = q.topic_name ? `<span class="q-item__kicker">${q.topic_name}</span>` : '';
    const imgHTML = q.image ? `<figure class="q-figure">${pdfImg(q.image, '')}</figure>` : '';

    questionsHTML += `
      <div class="q-item">
        <div class="q-item__rail">
          <span class="q-item__num">${idx + 1}</span>
          <span class="q-item__glyph ${glyphClass}">${glyphSvg}</span>
        </div>
        <div class="q-item__body">
          ${kicker}
          <p>${renderMath(q.text || '')}</p>
          ${imgHTML}
          <ul class="q-choices">${optionsHTML}</ul>
        </div>
      </div>`;
  });
  if (sectionOpen) questionsHTML += `</section>`;
```

---

## Paso 3 · Template (la lista ya viene envuelta en `<section>`)

Las `<section class="q-section">` ya contienen todo, así que **quita** el
`<ol class="exam-pdf__exercises">`. En el HTML que retorna `buildComprobanteHTML`,
cambia:

```html
  <ol class="exam-pdf__exercises">${questionsHTML}</ol>
```

por:

```html
  ${questionsHTML}
```

---

## Notas

- **Numeración:** ahora es explícita (`idx + 1`), no el `counter` CSS — por eso
  se quitó el `<ol>`. Sigue siendo 1..N global a lo largo del comprobante.
- **`applyPdfBlankWidths`** busca `.exam-pdf__exercise` / `.exam-pdf__choice__text`.
  Si tus reactivos usan blancos `___`, cambia esos dos selectores a
  `.q-item` y `.q-choice__text` para que el cálculo del ancho siga aplicando.
- **No contestada:** glifo neutro (–) y solo se marca la correcta en verde
  (sin rojo), igual que tu lógica actual.
- **Clave de respuestas:** unificada al mismo look — ver **Paso 4 y 5** abajo.
- Referencia visual: `Preguntas PDF.dc.html` (columna *Propuesta*).

---

# Clave de respuestas (`buildAnswerKeyHTML`)

Mismo lenguaje visual, reusando las clases `q-*` del Paso 1 (no hay CSS nuevo).
La clave no tiene alumno: cada reactivo solo marca la **correcta** en verde, sin
glifo de resultado al margen (solo el número). Encabezado por materia con el
conteo de reactivos.

## Paso 4 · Render (reemplaza el bloque `const questionsHTML = …` de `buildAnswerKeyHTML`)

```js
  const ROMAN = ['i','ii','iii','iv','v','vi','vii','viii','ix','x','xi','xii','xiii','xiv','xv','xvi','xvii','xviii','xix','xx'];
  const roman = (n) => ROMAN[n - 1] || String(n);

  // Conteo de reactivos por materia (para el stat del encabezado).
  const subjectCounts = {};
  questions.forEach(q => { subjectCounts[q.subject] = (subjectCounts[q.subject] || 0) + 1; });

  let questionsHTML = '';
  let lastSubject = null;
  let secCount = 0;
  let sectionOpen = false;

  questions.forEach((q, idx) => {
    if (q.subject !== lastSubject) {
      if (sectionOpen) questionsHTML += `</section>`;
      lastSubject = q.subject;
      secCount++;
      const n = subjectCounts[q.subject] || 0;
      questionsHTML += `
        <section class="q-section">
          <div class="q-sec-head">
            <div class="q-sec-head__title">
              <span class="q-sec-head__num">${roman(secCount)}.</span>
              <h2 class="q-sec-head__name">${q.subject}</h2>
            </div>
            <span class="q-sec-head__stat">${n} ${n === 1 ? 'reactivo' : 'reactivos'}</span>
          </div>`;
      sectionOpen = true;
    }

    const correctAns = answerKey[q.id];
    const letters = Object.keys(q.options);
    const optionsHTML = letters.map(letter => {
      const isC = letter === correctAns;
      const cls = isC ? 'q-choice q-choice--correct' : 'q-choice';
      const hasImg = q.option_images && q.option_images[letter];
      const content = hasImg ? pdfImg(q.option_images[letter], q.options[letter]) : renderMath(q.options[letter]);
      const markerHTML = isC ? '<span class="q-choice__marker">Correcta</span>' : '';
      return `<li class="${cls}"><span class="q-choice__letter">${letter}</span><span class="q-choice__text">${content}</span>${markerHTML}</li>`;
    }).join('');

    const kicker = q.topic_name ? `<span class="q-item__kicker">${q.topic_name}</span>` : '';
    const imgHTML = q.image ? `<figure class="q-figure">${pdfImg(q.image, '')}</figure>` : '';

    questionsHTML += `
      <div class="q-item">
        <div class="q-item__rail">
          <span class="q-item__num">${idx + 1}</span>
        </div>
        <div class="q-item__body">
          ${kicker}
          <p>${renderMath(q.text || '')}</p>
          ${imgHTML}
          <ul class="q-choices">${optionsHTML}</ul>
        </div>
      </div>`;
  });
  if (sectionOpen) questionsHTML += `</section>`;
```

## Paso 5 · Template de la clave

En el HTML que retorna `buildAnswerKeyHTML`, cambia:

```html
  <ol class="exam-pdf__exercises">${questionsHTML}</ol>
```

por:

```html
  ${questionsHTML}
```

> El riel solo lleva el número (sin glifo). Si quieres un acento, puedes añadir
> bajo el número un punto coñac: `<span class="q-item__num">${idx+1}</span>` +
> `<span style="width:5pt;height:5pt;border-radius:999px;background:var(--accent-conac);margin-top:4pt"></span>`.

Con esto, comprobante y clave comparten encabezados de sección, kicker de tema y
el estilo de opciones — un solo lenguaje visual.

## (Opcional) Limpieza

Una vez migrados **comprobante** y **clave** a las clases `q-*`, las viejas
`.exam-pdf__exercises`, `.exam-pdf__exercise`, `.exam-pdf__choices`,
`.exam-pdf__choice*` y `.exam-pdf__subject` de `TERCIAL_PDF_CSS` quedan sin uso
y se pueden borrar. Verifica antes que ningún otro builder las use
(`grep "exam-pdf__choice" server.js`).

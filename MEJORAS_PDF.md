# Mejoras al PDF del comprobante/clave — bitácora (sesión 2026-06-19)

Todo esto se trabajó en la rama `dev`. Aplica al PDF que genera Puppeteer en
`server.js` (comprobante por alumno + clave del profesor). Sirve como referencia
para continuar en la Mac Mini.

> Para que esto esté en la Mac Mini hay que **commit + push de `dev`** desde la
> máquina donde se hizo, y `git pull` en `dev` en la Mac Mini.

---

## YA HECHO (aplicado en el código)

### 1. Full-bleed crema (diseño "V1") + tamaño carta
- **Problema:** el PDF salía con marco blanco alrededor y, además, en A4 (el CSS
  pedía carta pero `page.pdf` forzaba A4).
- **Fix:** `@page { size: letter; margin: 0 }`, los dos `page.pdf()` con
  `format: 'letter'` y `margin: 0` en los 4 lados; `.exam-pdf { padding: 0 }`.
  El fondo crema (`html`/`body`) llega al borde del papel.
- **Archivo:** `server.js` (CSS `TERCIAL_PDF_CSS` + las dos llamadas `page.pdf`).

### 2. Aire vertical en cada página, sin marco blanco
- **Problema:** con `margin: 0`, el contenido tocaba el borde superior/inferior en
  las páginas de continuación.
- **Fix:** se envuelve el contenido en una tabla `.page-frame` con `thead`/`tfoot`
  que se repiten en cada página (comportamiento de tablas al imprimir) y dejan
  `0.62in` de aire crema arriba/abajo. (Probado: poner margen normal de Puppeteer
  deja esas franjas BLANCAS; header/footer templates dejan una línea blanca al
  borde. La tabla es la única que da full-bleed perfecto + aire por página.)
- **Archivo:** `server.js` (`.page-frame*` en CSS + envoltura en las 2 funciones build).

### 3. Líneas de relleno (`___`) medidas en el PDF
- **Problema (el "hueco"):** el PDF dibujaba la raya por nº de guiones, no por el
  ancho de las opciones.
- **Fix:** `applyPdfBlankWidths(page)` mide las opciones con la tipografía real y
  pone cada blanco = **ancho de la opción/parte más larga + 3px** (tope 420px).
  Detecta separador de multi-blanco `/`, ` - ` y ` – `. Se llama después de
  `setContent` y de `document.fonts.ready`.
- **Regla canónica:** ver `CONVENCIONES.md`.
- **Grosor de la raya:** se queda en **1.5px** (decisión del usuario). NO subir a
  2px por ahora. (La variación de grosor que se ve a bajo zoom es rasterización
  sub-pixel de la hairline; impreso a 300dpi se ve pareja. No hay forma confiable
  de "forzar el snapping" en un PDF vectorial visto a zoom variable.)

### 4. Detección de separador multi-blanco también en pantalla
- `adaptBlankWidths()` (`public/index.html`) y `adaptPracticeBlankWidths()`
  (`public/teacher.html`) ahora detectan `/`, ` - `, ` – ` (antes solo `/`).
  Así pantalla y PDF miden igual los multi-blanco.

### 5. Barras del desglose ("Por materia")
- **Altura 3.5pt** (antes 2.5pt) para que se vean parejas (a 2.5pt la hairline
  rasterizaba disparejo entre filas).
- **Color por nivel de dominio** (umbrales acordados en los dashboards):
  - **Domina ≥70%** → verde
  - **En proceso 50–69%** → ámbar
  - **Requiere atención <50%** → rojo
  - Tono **VIVO activo** (`#1D9E75 / #EF9F27 / #E24B4A`). La alternativa **apagada
    Tercial** (`#5a8045 / #b8862e / #b8362c`) queda en comentario al lado de las
    variables `--level-domina/proceso/atencion` en `server.js` — para alternar,
    cambiar esos 3 hex.
  - Se agregó **leyenda** al pie del desglose.

### 6. Clave de respuestas: sin subrayado en la correcta
- Se quitó `.answer-final` (subrayado coñac). La correcta ya se distingue por el
  recuadro verde + "Correcta"; el subrayado era redundante.

### 7. Verde de "correcta" más visible
- `--state-ok-bg`: `#e7ecd9` → **`#d6e3bd`**. El verde anterior casi se fundía con
  el crema; ahora pesa igual que el rojo de la incorrecta.

### 8. Opciones con imagen: solo la figura, sin descripción
- Cuando una opción tiene `option_images`, el PDF muestra **solo la figura**; la
  descripción de texto pasa al `alt` (no visible). Antes mostraba figura + texto
  redundante. (La app ya lo hacía bien; esto deja el PDF consistente.)

### 9. Colores de tabla sincronizados con el examen
- Las `@font/--md-*` del PDF apuntaban a la paleta vieja. Se igualaron a la app:
  - `--md-border`: `#8c7556` (café oscuro) → **`#c9bda3`** (tan suave) ← el grande
  - `--md-th-bg`: → `#efe7d8`
  - `--md-table-bg`: → `#f8f3e8`

### 10. SVG inline en el PDF (color correcto)
- **Problema:** los SVG iban como `<img src>`, y ahí `currentColor` caía a **negro
  puro** (`#000000`); en el examen son `#1f1a16` (ink-900).
- **Fix:** helper `pdfImg(srcPath, alt)` que **inyecta el SVG inline** (PNG sigue
  como `<img>`). Así heredan el color del documento. Además, el SVG de opción se
  fuerza a `--ink-900` (`.exam-pdf__choice__text svg { color: var(--ink-900) }`)
  porque el contenedor de opción usa ink-700 (más claro) y se veía distinto del
  enunciado.

### 11. ⭐ CORS de fuentes — EL ARREGLO GRANDE
- **Problema:** el PDF **no cargaba NINGUNA fuente propia**. Todo salía en
  respaldo del sistema: **Georgia** (en vez de Fraunces), **Helvetica** (en vez de
  IBM Plex), **Times** (en vez de KaTeX). Por eso los delimitadores grandes de
  KaTeX (`\left(\right)`, que usan `KaTeX_Size*`) se veían chicos.
- **Causa:** `page.setContent()` deja el documento con origen opaco (`about:blank`);
  las fuentes `@font-face` se piden en modo CORS y `express.static` no mandaba
  `Access-Control-Allow-Origin` → el navegador las bloqueaba (`net::ERR_FAILED`).
- **Fix:** `Access-Control-Allow-Origin: *` en los assets estáticos (solo archivos,
  no `/api`) + `await document.fonts.ready` antes de medir blancos y capturar.
- **Verificado:** `pdffonts` ahora embebe Fraunces, IBMPlexSans, KaTeX_Main/Math/
  Size3; los delimitadores encierran las fracciones.
- **Nota:** todo lo que se revisó antes de este fix se vio con fuentes de respaldo;
  el PDF ahora se parece mucho más al examen.

### 12. server.js testeable
- `server.listen` envuelto en `if (require.main === module)` + `module.exports`
  (buildComprobanteHTML, buildAnswerKeyHTML, applyPdfBlankWidths,
  enqueueAnswerKeyPDF, getPdfBrowser, TERCIAL_PDF_CSS). `node server.js` arranca
  igual; permite generar PDFs de prueba sin levantar el server productivo.

---

## YA HECHO · 2ª tanda (paquete de diseño "Portada para página de resultados")

El paquete de diseño (zip del usuario, hecho con la parte de diseño de Claude;
guías paste-ready en `repo-diseno/`) se aplicó así:

### 13. Reactivos del comprobante — rediseño `q-*`
Encabezado por materia (numeral romano + nombre Fraunces + stat), reactivo con
riel de margen (número + glifo ✓/✗/–), kicker de tema, opciones con franja lateral
+ tinte + badge circular de letra. (Guía `IMPLEMENTAR-preguntas-pdf.md`, Pasos 1–3.)
`applyPdfBlankWidths` ahora apunta a `.q-item` / `.q-choice__text`.

### 14. Clave de respuestas — mismo lenguaje `q-*`
Riel solo con número, encabezado "N reactivos", solo marca la correcta.
(Pasos 4–5 de la misma guía.)

### 15. Portada / página de resultados — `p-*`
Reemplaza el bloque de puntaje + desglose: número grande terracota + "Dominaste
X de Y materias" + frase contextual + desglose por materia + tarjetas
*A reforzar* / *Tu fortaleza* + leyenda. El hero se mantiene; las preguntas
arrancan en la página 2. (Guía `IMPLEMENTAR-portada-pdf.md`.)
> El concepto previo de **anillo** ("puntaje protagonista") se DESCARTÓ a favor de
> esta portada editorial del paquete. `portada-conceptos.js` queda como referencia
> del anillo, ya no se usa.

### 16. Colores de nivel → apagado del paquete
`--level-domina/proceso/atencion` = `#4a6b3f / #8a5208 / #9c3525` (vivos de los
dashboards como alternativa en comentario). Los usan el desglose, las tarjetas y la
leyenda de la portada.

### 17. Limpieza de CSS muerto
Borradas ~220 líneas de `TERCIAL_PDF_CSS` sin uso: `.score-block*`, `.breakdown*`,
`.exam-pdf__exercise*`, `.exam-pdf__choice*`, `.exam-pdf__subject`,
`.exam-pdf__figure`, `.exam-pdf__body`. Se conservan `.exam-pdf` y
`.exam-pdf__hero*` (el hero), `q-*`, `p-*`.

---

## PENDIENTE — proyecto de verano

- **Telegram:** `repo-diseno/comprobante-telegram.js` (del paquete) — tarjeta corta
  del comprobante enviada por Telegram como PNG (`buildPortadaCortaHTML` ya viene en
  código). Falta: copiarlo a la raíz, wiring en `server.js` (3 pasos comentados al
  inicio del archivo), env vars `TELEGRAM_BOT_TOKEN`/`CHAT_ID`, y mapear cada alumno
  a su `chat_id`.

---

## Decisiones/preferencias registradas
- Diseño de márgenes: **V1 (crema a sangre)**.
- Tamaño: **carta**.
- Grosor de raya de relleno: **1.5px** (no cambiar).
- Colores de nivel: **apagados del paquete** (`#4a6b3f / #8a5208 / #9c3525`) activos; vivos como alternativa en comentario.
- Portada: **editorial del paquete** (puntaje grande + desglose + tarjetas) — implementada. El concepto de anillo se descartó.
- Respaldo git: existe `stash@{0}` ("cambios locales antes de pull dev (19jun)") —
  ya reaplicado; se puede soltar (`git stash drop stash@{0}`) una vez confirmado.

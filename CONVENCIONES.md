# Convenciones del proyecto ECOEMS

Reglas de autor/diseño que deben respetarse en TODOS los exámenes, para que no
queden distintas de una aplicación a otra.

## Líneas de relleno (`___`) en reactivos de completar

**Regla canónica:** el ancho de cada línea de relleno debe ser el **ancho de la
opción más larga que puede ir en ese blanco, MÁS 3 px**.

Detalles de la regla:

- "Opción más larga" se mide con la **tipografía real de las opciones** (no por
  nº de caracteres ni de guiones), renderizando matemáticas/markdown igual que en
  la opción.
- Si un reactivo tiene **varios blancos** y cada opción se parte en tantas partes
  como blancos (separadas por `/`), cada blanco se mide contra la **parte** que le
  toca, no contra la opción completa.
- **Tope de seguridad:** 420 px (para que una opción larguísima no rompa el
  layout).
- Solo aplica a opciones de **texto puro**. Si las opciones son imágenes
  (`option_images` o `<img>`), se deja el ancho por defecto del render.

### Dónde está implementada

Esta regla ya vive en dos lugares y los dos deben mantenerse en sync:

- Vista del alumno: `adaptBlankWidths()` en `public/index.html`
  (`Math.min(max + 3, 420) + 'px'`).
- Panel del profesor: `adaptPracticeBlankWidths()` en `public/teacher.html`.
- **PDF** (comprobante y clave): `applyPdfBlankWidths()` en `server.js`, inyectada
  con `page.evaluate()` después de `setContent` en ambos flujos. Mide las opciones
  con la tipografía real igual que en pantalla.

### Multi-blanco: separador de partes

Cuando un reactivo tiene varios blancos, cada opción se parte en tantas partes
como blancos y cada blanco se mide contra su parte. El separador puede ser `/`,
` - ` o ` – ` (guion/raya con espacios). **Nota de inconsistencia pendiente:**
`applyPdfBlankWidths()` (PDF) detecta los tres separadores; `adaptBlankWidths()`
y `adaptPracticeBlankWidths()` (pantalla) **solo** parten por `/`. Como los
exámenes ECOEMS usan ` - ` / ` – ` en los multi-blanco, hoy esos reactivos salen
bien en el PDF pero en pantalla cada blanco se mide contra la opción completa.
Para igualar, portar la detección de separador del PDF a las dos funciones de
pantalla.

### Render base (fallback)

`blankSpan()` en `public/shared/markdown-render.js` dibuja la raya según el nº de
guiones del JSON (`run.length`). Es solo el fallback que se ve por un instante
antes de que corra el JS; en el resultado final (pantalla y PDF) siempre manda la
regla canónica de medición de opciones.
